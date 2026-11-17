"""Emisión por SMTP y validación de códigos de recuperación de contraseña."""

from datetime import datetime, timedelta, timezone
import secrets

from .correo_smtp import enviar_correo
from .repositorio_cuenta import repositorio_cuenta
from .sesion_nutriologo import SesionNutriologo


class ServicioRecuperacion:
    VIGENCIA_MINUTOS = 10

    def solicitar_codigo(self, correo):
        correo = correo.strip()
        # La interfaz siempre muestra la misma respuesta para no confirmar si
        # una dirección de correo pertenece a una cuenta registrada.
        cuenta = repositorio_cuenta.buscar_por_correo(correo)
        if not cuenta:
            return

        codigo = f"{secrets.randbelow(1_000_000):06d}"
        codigo_hash = SesionNutriologo.hashear_password(codigo)
        vence = datetime.now(timezone.utc) + timedelta(minutes=self.VIGENCIA_MINUTOS)
        guardado = repositorio_cuenta.guardar_codigo_recuperacion(
            correo, codigo_hash, vence
        )
        if not guardado:
            return

        cuerpo = (
            "Solicitaste cambiar la contraseña de tu cuenta NutrIA.\n\n"
            f"Tu código es: {codigo}\n\n"
            f"Vence en {self.VIGENCIA_MINUTOS} minutos. Si no solicitaste este cambio, "
            "ignora este mensaje."
        )
        try:
            enviar_correo(
                destinatario=cuenta["correo"],
                asunto="Código para recuperar tu contraseña de NutrIA",
                mensaje=cuerpo,
            )
        except Exception:
            repositorio_cuenta.invalidar_codigos_recuperacion(correo)
            raise

    def restablecer_password(self, correo, codigo, password_nueva):
        nuevo_hash = SesionNutriologo.hashear_password(password_nueva)
        return repositorio_cuenta.cambiar_password_con_codigo(
            correo,
            lambda hash_guardado: SesionNutriologo.verificar_password(
                codigo, hash_guardado
            ),
            nuevo_hash,
        )


servicio_recuperacion = ServicioRecuperacion()
