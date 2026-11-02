"""Configuración y conexión a PostgreSQL para NutrIA MVP."""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def conectar():
    """Abre una conexión usando las variables de entorno locales de NutrIA."""
    requeridas = ("NUTRIA_DB_USER", "NUTRIA_DB_PASSWORD")
    faltantes = [nombre for nombre in requeridas if not os.getenv(nombre)]
    if faltantes:
        raise RuntimeError(
            "Faltan variables de conexión en el archivo .env: " + ", ".join(faltantes)
        )

    return psycopg.connect(
        host=os.getenv("NUTRIA_DB_HOST", "localhost"),
        port=int(os.getenv("NUTRIA_DB_PORT", "5432")),
        dbname=os.getenv("NUTRIA_DB_NAME", "nutria_mvp"),
        user=os.environ["NUTRIA_DB_USER"],
        password=os.environ["NUTRIA_DB_PASSWORD"],
        connect_timeout=5,
    )
