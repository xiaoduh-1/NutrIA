"""Acceso PostgreSQL a la cuenta del nutriólogo y su consultorio."""

from uuid import UUID

from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row

from .conexion import conectar


class RepositorioCuenta:
    CONSULTA_PERFIL = (
        "SELECT u.id AS usuario_id, u.usuario, u.correo, u.password_hash, u.activo, "
        "p.nombre_completo, c.nombre AS nombre_consultorio, "
        "c.telefono_contacto AS telefono_consultorio, "
        "c.correo_contacto AS correo_consultorio, c.foto_path, c.foto_bytes "
        "FROM usuarios u "
        "JOIN perfiles_nutriologo p ON p.usuario_id = u.id "
        "JOIN consultorio c ON c.usuario_id = u.id"
    )

    @staticmethod
    def _perfil_publico(fila):
        if not fila:
            return {}
        perfil = dict(fila)
        perfil["id"] = str(perfil.pop("usuario_id"))
        perfil["nombre"] = perfil.pop("nombre_completo")
        return perfil

    def existe_cuenta(self):
        with conectar() as conexion, conexion.cursor() as cursor:
            cursor.execute("SELECT EXISTS (SELECT 1 FROM usuarios WHERE activo)")
            return cursor.fetchone()[0]

    def buscar_por_usuario(self, usuario):
        with conectar() as conexion, conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                self.CONSULTA_PERFIL + " WHERE lower(u.usuario) = lower(%s)",
                (usuario.strip(),),
            )
            fila = cursor.fetchone()
            return dict(fila) if fila else None

    def buscar_por_correo(self, correo):
        with conectar() as conexion, conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                self.CONSULTA_PERFIL + " WHERE lower(u.correo) = lower(%s) AND u.activo",
                (correo.strip(),),
            )
            fila = cursor.fetchone()
            return dict(fila) if fila else None

    def crear_cuenta(self, cuenta, consultorio):
        try:
            with conectar() as conexion, conexion.cursor() as cursor:
                # El MVP tiene una sola cuenta administradora; el bloqueo evita
                # que dos registros iniciales simultáneos creen cuentas distintas.
                cursor.execute("LOCK TABLE usuarios IN SHARE ROW EXCLUSIVE MODE")
                cursor.execute("SELECT EXISTS (SELECT 1 FROM usuarios WHERE activo)")
                if cursor.fetchone()[0]:
                    raise ValueError("Ya existe una cuenta de administrador para este MVP.")
                cursor.execute(
                    "INSERT INTO usuarios (usuario, correo, password_hash) "
                    "VALUES (%s, %s, %s) RETURNING id",
                    (cuenta["usuario"].strip(), cuenta["correo"].strip(), cuenta["password_hash"]),
                )
                usuario_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO perfiles_nutriologo (usuario_id, nombre_completo) VALUES (%s, %s)",
                    (usuario_id, cuenta["nombre"].strip()),
                )
                cursor.execute(
                    "INSERT INTO consultorio "
                    "(usuario_id, nombre, telefono_contacto, correo_contacto, foto_path, foto_bytes) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (
                        usuario_id,
                        consultorio["nombre_consultorio"].strip(),
                        consultorio["telefono_consultorio"].strip(),
                        consultorio["correo_consultorio"].strip(),
                        consultorio.get("foto_path", ""),
                        consultorio.get("foto_bytes", b""),
                    ),
                )
        except UniqueViolation as error:
            raise ValueError("Ese usuario o correo ya está registrado.") from error
        return str(usuario_id)

    def actualizar_perfil(self, usuario_id, datos):
        usuario_id = UUID(str(usuario_id))
        try:
            with conectar() as conexion, conexion.cursor() as cursor:
                cursor.execute(
                    "UPDATE usuarios SET usuario = %s, correo = %s, "
                    "actualizado_en = CURRENT_TIMESTAMP WHERE id = %s",
                    (datos["usuario"].strip(), datos["correo"].strip(), usuario_id),
                )
                if cursor.rowcount != 1:
                    return False
                cursor.execute(
                    "UPDATE perfiles_nutriologo SET nombre_completo = %s, "
                    "actualizado_en = CURRENT_TIMESTAMP WHERE usuario_id = %s",
                    (datos["nombre"].strip(), usuario_id),
                )
                cursor.execute(
                    "UPDATE consultorio SET nombre = %s, telefono_contacto = %s, "
                    "correo_contacto = %s, foto_path = %s, foto_bytes = %s, "
                    "actualizado_en = CURRENT_TIMESTAMP "
                    "WHERE usuario_id = %s",
                    (
                        datos["nombre_consultorio"].strip(),
                        datos["telefono_consultorio"].strip(),
                        datos["correo_consultorio"].strip(),
                        datos.get("foto_path", ""),
                        datos.get("foto_bytes", b""),
                        usuario_id,
                    ),
                )
        except UniqueViolation as error:
            raise ValueError("Ese usuario o correo ya está registrado por otra cuenta.") from error
        return True

    def actualizar_password_hash(self, usuario_id, password_hash):
        with conectar() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "UPDATE usuarios SET password_hash = %s, actualizado_en = CURRENT_TIMESTAMP WHERE id = %s",
                (password_hash, UUID(str(usuario_id))),
            )
            return cursor.rowcount == 1

    def guardar_codigo_recuperacion(self, correo, codigo_hash, vence_en):
        with conectar() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM usuarios WHERE lower(correo) = lower(%s) "
                "AND activo = TRUE FOR UPDATE",
                (correo.strip(),),
            )
            cuenta = cursor.fetchone()
            if not cuenta:
                return False
            cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM recuperaciones_password "
                "WHERE lower(correo) = lower(%s) "
                "AND creado_en > CURRENT_TIMESTAMP - INTERVAL '60 seconds')",
                (correo.strip(),),
            )
            if cursor.fetchone()[0]:
                return False
            cursor.execute(
                "UPDATE recuperaciones_password SET usado = TRUE "
                "WHERE lower(correo) = lower(%s) AND usado = FALSE",
                (correo.strip(),),
            )
            cursor.execute(
                "INSERT INTO recuperaciones_password (correo, codigo_hash, vence_en) "
                "SELECT correo, %s, %s FROM usuarios WHERE id = %s",
                (codigo_hash, vence_en, cuenta[0]),
            )
            return cursor.rowcount == 1

    def invalidar_codigos_recuperacion(self, correo):
        with conectar() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "UPDATE recuperaciones_password SET usado = TRUE "
                "WHERE lower(correo) = lower(%s) AND usado = FALSE",
                (correo.strip(),),
            )

    def cambiar_password_con_codigo(self, correo, verificar_codigo, nuevo_hash):
        """Consume atómicamente un código válido y reemplaza el hash de contraseña."""
        with conectar() as conexion, conexion.cursor() as cursor:
            cursor.execute(
                "SELECT id, codigo_hash, intentos FROM recuperaciones_password "
                "WHERE lower(correo) = lower(%s) AND usado = FALSE "
                "AND vence_en > CURRENT_TIMESTAMP "
                "ORDER BY creado_en DESC LIMIT 1 FOR UPDATE",
                (correo.strip(),),
            )
            solicitud = cursor.fetchone()
            if not solicitud:
                return "invalido"
            solicitud_id, hash_guardado, intentos = solicitud
            if intentos >= 5:
                cursor.execute(
                    "UPDATE recuperaciones_password SET usado = TRUE WHERE id = %s",
                    (solicitud_id,),
                )
                return "invalido"
            if not verificar_codigo(hash_guardado):
                cursor.execute(
                    "UPDATE recuperaciones_password SET intentos = intentos + 1 "
                    "WHERE id = %s",
                    (solicitud_id,),
                )
                return "invalido"
            cursor.execute(
                "UPDATE usuarios SET password_hash = %s, actualizado_en = CURRENT_TIMESTAMP "
                "WHERE lower(correo) = lower(%s) AND activo = TRUE",
                (nuevo_hash, correo.strip()),
            )
            if cursor.rowcount != 1:
                return "invalido"
            cursor.execute(
                "UPDATE recuperaciones_password SET usado = TRUE WHERE id = %s",
                (solicitud_id,),
            )
            cursor.execute(
                "UPDATE recuperaciones_password SET usado = TRUE "
                "WHERE lower(correo) = lower(%s) AND usado = FALSE",
                (correo.strip(),),
            )
            return "correcto"


repositorio_cuenta = RepositorioCuenta()
