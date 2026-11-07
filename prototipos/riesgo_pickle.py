"""Demostración inofensiva del riesgo de pickle y joblib.

Un archivo pickle o joblib puede contener instrucciones que se ejecutan
al cargarlo, sin que el código que lo carga las llame. Aquí solo se
imprime un mensaje, pero podría ser cualquier orden.

Uso:
    uv run python prototipos/riesgo_pickle.py
"""
import json
import pickle
import tempfile
from pathlib import Path

import joblib


class ObjetoTrampa:
    """Al deserializarse, se llama a print con este mensaje."""

    def __reduce__(self):
        return (print, ("*** ESTE MENSAJE SE HA EJECUTADO AL CARGAR EL "
                        "ARCHIVO, sin llamarlo explícitamente ***",))


def main():
    with tempfile.TemporaryDirectory() as carpeta:
        carpeta = Path(carpeta)

        ruta = carpeta / "modelo_trampa.pkl"
        with open(ruta, "wb") as f:
            pickle.dump(ObjetoTrampa(), f)
        print("1) Archivo pickle creado. Lo cargo con pickle.load...")
        with open(ruta, "rb") as f:
            pickle.load(f)
        print("   Carga terminada.\n")

        ruta_joblib = carpeta / "modelo_trampa.joblib"
        joblib.dump(ObjetoTrampa(), ruta_joblib)
        print("2) Archivo joblib creado. Lo cargo con joblib.load...")
        joblib.load(ruta_joblib)
        print("   Carga terminada.\n")

        ruta_json = carpeta / "modelo.json"
        ruta_json.write_text(json.dumps({"coeficientes": [1.0]}))
        print("3) Archivo JSON creado. Lo cargo con json.loads...")
        print("  ", json.loads(ruta_json.read_text()))
        print("   Solo se leen datos: JSON no ejecuta código.")


if __name__ == "__main__":
    main()
