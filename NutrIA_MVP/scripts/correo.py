"""Envía un mensaje de prueba usando la cuenta SMTP configurada en .env."""

import os

try:
    from scripts.verificar_envio import enviar_correo
except ModuleNotFoundError:  # Permite también ejecutar este archivo directamente.
    from verificar_envio import enviar_correo


def main():
    destinatario = os.getenv("NUTRIA_SMTP_TEST_TO", "").strip()
    try:
        enviar_correo(
            destinatario=destinatario,
            asunto="Prueba SMTP de NutrIA",
            mensaje=(
                "Hola.\n\n"
                "Este es un correo de prueba enviado desde NutrIA utilizando "
                "Python y Gmail SMTP.\n\n"
                "Saludos."
            ),
        )
    except Exception as error:
        print(f"No se pudo enviar el correo ({type(error).__name__}): {error}")
        return 1

    print(f"Correo enviado correctamente a {destinatario}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
