"""Sesión autenticada del nutriólogo con su perfil persistido en PostgreSQL."""

import base64
import hashlib
import hmac
import secrets

from .repositorio_cuenta import repositorio_cuenta


class SesionNutriologo:
    ITERACIONES = 600_000

    def __init__(self):
        self._cuenta = None
        self._consultorio = None

    @classmethod
    def hashear_password(cls, password):
        sal = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), sal, cls.ITERACIONES
        )
        return "pbkdf2_sha256${}${}${}".format(
            cls.ITERACIONES,
            base64.urlsafe_b64encode(sal).decode("ascii"),
            base64.urlsafe_b64encode(digest).decode("ascii"),
        )

    @staticmethod
    def verificar_password(password, hash_guardado):
        try:
            algoritmo, iteraciones, sal_codificada, digest_codificado = hash_guardado.split("$")
            if algoritmo != "pbkdf2_sha256":
                return False
            sal = base64.urlsafe_b64decode(sal_codificada.encode("ascii"))
            digest_esperado = base64.urlsafe_b64decode(digest_codificado.encode("ascii"))
            digest = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), sal, int(iteraciones)
            )
            return hmac.compare_digest(digest, digest_esperado)
        except (AttributeError, TypeError, ValueError):
            return False

    def registrar(self, cuenta, consultorio):
        cuenta_guardada = dict(cuenta)
        password = cuenta_guardada.pop("password")
        cuenta_guardada["password_hash"] = self.hashear_password(password)
        self.registrar_hash(cuenta_guardada, consultorio)

    def registrar_hash(self, cuenta, consultorio):
        cuenta_guardada = dict(cuenta)
        hash_guardado = cuenta_guardada.get("password_hash", "")
        if not hash_guardado.startswith("pbkdf2_sha256$"):
            raise ValueError("La contraseña debe llegar como hash PBKDF2; no se aceptan contraseñas en texto simple.")
        usuario_id = repositorio_cuenta.crear_cuenta(cuenta_guardada, consultorio)
        cuenta_guardada["id"] = usuario_id
        self._cuenta = cuenta_guardada
        self._consultorio = dict(consultorio)

    def autenticar(self, usuario, password):
        fila = repositorio_cuenta.buscar_por_usuario(usuario)
        if not fila or not fila["activo"]:
            return False
        if not self.verificar_password(password, fila["password_hash"]):
            return False
        self._cuenta = {
            "id": str(fila["usuario_id"]),
            "usuario": fila["usuario"],
            "correo": fila["correo"],
            "nombre": fila["nombre_completo"],
            "password_hash": fila["password_hash"],
        }
        self._consultorio = {
            "nombre_consultorio": fila["nombre_consultorio"],
            "telefono_consultorio": fila["telefono_consultorio"],
            "correo_consultorio": fila["correo_consultorio"],
            "foto_path": fila["foto_path"],
            "foto_bytes": fila["foto_bytes"],
        }
        return True

    @staticmethod
    def existe_cuenta():
        return repositorio_cuenta.existe_cuenta()

    def obtener_perfil(self):
        if not self._cuenta or not self._consultorio:
            return {}
        perfil = {k: v for k, v in self._cuenta.items() if k != "password_hash"}
        perfil.update(self._consultorio)
        return perfil

    def actualizar_perfil(self, datos):
        if not self._cuenta or not self._consultorio:
            return False
        if not repositorio_cuenta.actualizar_perfil(self._cuenta["id"], datos):
            return False
        campos_cuenta = {"nombre", "usuario", "correo"}
        campos_consultorio = {
            "nombre_consultorio", "telefono_consultorio", "correo_consultorio",
            "foto_path", "foto_bytes",
        }
        for campo in campos_cuenta:
            if campo in datos:
                self._cuenta[campo] = datos[campo]
        for campo in campos_consultorio:
            if campo in datos:
                self._consultorio[campo] = datos[campo]
        return True

    def cambiar_password(self, password_actual, password_nueva):
        if not self._cuenta or not self.verificar_password(
            password_actual, self._cuenta["password_hash"]
        ):
            return False
        nuevo_hash = self.hashear_password(password_nueva)
        if not repositorio_cuenta.actualizar_password_hash(self._cuenta["id"], nuevo_hash):
            return False
        self._cuenta["password_hash"] = nuevo_hash
        return True


sesion_nutriologo = SesionNutriologo()
