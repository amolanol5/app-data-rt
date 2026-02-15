import pandas as pd

def check_bancolombia_tab(file_path: str, name_tab: str) -> bool:
    try:
        xls = pd.ExcelFile(file_path)
        return name_tab in xls.sheet_names
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return False
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return False

def check_field_named_factura(df: pd.DataFrame) -> bool:
    return 'FACTURA' in df.columns.str.strip() # limpiar espacios en blanco alrededor de los nombres de las columnas

def list_columns(df: pd.DataFrame) -> list:
    return df.columns.tolist()

def list_tabs(file_path: str) -> list:
    try:
        xls = pd.ExcelFile(file_path)
        return xls.sheet_names
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []