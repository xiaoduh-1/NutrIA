"""Comprueba que las credenciales de .env conecten con nutria_mvp."""

from datos.conexion import conectar


def main():
    try:
        with conectar() as conexion, conexion.cursor() as cursor:
            cursor.execute("SELECT current_database(), current_user, version()")
            base, usuario, version = cursor.fetchone()
        print(f"Conexión correcta a la base '{base}' con el usuario '{usuario}'.")
        print(version.split(",", maxsplit=1)[0])
    except Exception as error:
        print(f"No se pudo conectar a PostgreSQL: {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
