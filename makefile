# Makefile para ejecutar src/main.py
# Detecta el sistema operativo y usa el comando adecuado


ifeq ("$(OS)","Windows_NT")
    PYTHON=python
    CHECK_VENV=if not defined VIRTUAL_ENV (echo No hay un entorno virtual de Python activo. && exit 1)
else
    PYTHON=python3
    CHECK_VENV=test -n "$$VIRTUAL_ENV" || (echo "No hay un entorno virtual de Python activo." && exit 1)
endif

run:
	$(CHECK_VENV)
	$(PYTHON) src/main.py
