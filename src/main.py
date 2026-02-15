import pandas as pd
import os
from src.tools import *
import re
import json
import logging
from src.tools import check_bancolombia_tab, check_field_named_factura, list_columns, list_tabs

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

RC_FILE_PATH = "src/files/RC.xlsx"
TAT_FILE_PATH = "src/files/TAT.xlsx"
SHEET_NAME_RC_FILE = "BANCOLOMBIA"

# validate files exist
def check_file_exists(file_path):
    if not os.path.exists(file_path):
        logger.error(f"Archivo {file_path.split('/')[-1].split('.')[0]} no encontrado. Verifique que el archivo exista y tenga el siguiente nombre: {file_path.split('/')[-1]}")
        exit(1)
        
check_file_exists(RC_FILE_PATH)
check_file_exists(TAT_FILE_PATH)
       
# list tabs from tat file and filter only those that match the pattern 5 digits - 5 digits
list_tabs_tat = [tab for tab in list_tabs(
    TAT_FILE_PATH) if re.match(r'^\d{5}-\d{5}$', tab)]

# rc dataset
df_rc = pd.read_excel(RC_FILE_PATH, sheet_name=SHEET_NAME_RC_FILE)

# check not blank rows in RC file
if df_rc.empty:
    logger.error("RC file is empty.")
    exit(1)

# check field FECHA and VALOR and FACTURA in RC file
if "FECHA" not in df_rc.columns or "VALOR" not in df_rc.columns or "FACTURA" not in df_rc.columns:
    logger.error(
        "RC file must contain 'FECHA', 'VALOR', and 'FACTURA' columns.")
    exit(1)

# check FECHA format in RC file is 18.11.2025
if not df_rc["FECHA"].apply(lambda x: re.match(r'^\d{2}\.\d{2}\.\d{4}$', str(x))).all():
    logger.error(
        "All 'FECHA' values in RC file must be in the format DD.MM.YYYY.")
    exit(1)

# convert VALOR to float to ensure proper comparison
df_rc["VALOR"] = df_rc["VALOR"].astype(float)

# create a list of dictionaries from df_rc for easier comparison with tat_data example: [{"FECHA": "18.11.2025", "VALOR": 1000.0}, {"FECHA": "19.11.2025", "VALOR": 2000.0}]
rac_data = df_rc[["FECHA", "VALOR"]].to_dict(orient="records")

# initialize MATCH column in df_rc with default value "NO EXISTE"
df_rc["MATCH"] = "NO EXISTE"

# iterate over each tab in TAT file and compare with rac_data, if match found, update MATCH column in df_rc with "ENCONTRADO EN TAT: {tab}"
for tab in list_tabs_tat:
    logger.info(f"Processing TAT tab: {tab}")
    df_tat = pd.read_excel(TAT_FILE_PATH, sheet_name=tab)

    # check field FECHA and VALOR in TAT file
    if "FECHA" not in df_tat.columns or "VALOR" not in df_tat.columns:
        logger.error(
            f"Error: archivo TAT '{tab}' debe contener las columnas 'FECHA' y 'VALOR'. valide que no tiene filas en blanco o espacios en blanco en el nombre de las columnas.")
        exit(1)

    # check not blank rows in TAT file
    if df_tat.empty:
        logger.error(f"Error: TAT file tab '{tab}' is empty.")
        exit(1)

    # convert VALOR to float to ensure proper comparison
    df_tat["VALOR"] = df_tat["VALOR"].astype(float)

    # create a list of dictionaries from df_tat for easier comparison with rac_data example: [{"FECHA": "18.11.2025", "RECIBO": "12345", "VALOR": 1000.0}, {"FECHA": "19.11.2025", "RECIBO": "67890", "VALOR": 2000.0}]
    tat_data = df_tat[["FECHA", "RECIBO", "VALOR"]].to_dict(orient="records")

    # iterate over each record in tat_data and check if there is a match in rac_data, if match found, update MATCH column in df_rc with "ENCONTRADO EN TAT: {tab}"
    for record_tat in tat_data:
        valor = record_tat["VALOR"]
        fecha = record_tat["FECHA"]

        # check FECHA format in TAT file is 18.11.2025
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', str(fecha)):
            logger.error(
                f"Error: La fecha: {fecha}' en el archivo TAT y pestaña '{tab}' debe estar en el formato DD.MM.YYYY.")
            exit(1)

        # check if there is a match in rac_data for the current record_tat, if match found, update MATCH column in df_rc with "ENCONTRADO EN TAT: {tab}"
        match = next(
            (record_rc for record_rc in rac_data if record_rc["VALOR"] == valor and record_rc["FECHA"] == fecha), None)

        if match:
            df_rc.loc[(df_rc["VALOR"] == valor) & (df_rc["FECHA"] ==
                                                   fecha), "MATCH"] = f"ENCONTRADO EN TAT: {tab}"

        continue

# summary
match_counts = (
    df_rc["MATCH"]
    .value_counts()
    .reset_index()
)

factura_counts = (
    df_rc["FACTURA"]
    .value_counts()
    .reset_index()
)

match_counts.columns = ["MATCH", "CANTIDAD"]
factura_counts.columns = ["FACTURA", "CANTIDAD"]

# save results.
with pd.ExcelWriter("resultado_conciliacion.xlsx") as writer:
    df_rc.to_excel(writer, sheet_name="Detalle", index=False)
    match_counts.to_excel(writer, sheet_name="Resumen_MATCH", index=False)
    factura_counts.to_excel(writer, sheet_name="Resumen_FACTURA", index=False)

logger.info(
    "Conciliación completada. Resultado guardado en 'resultado_conciliacion.xlsx'.")
