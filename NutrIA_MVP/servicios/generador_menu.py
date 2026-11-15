"""Generación de menús con Gemini a partir del perfil del paciente y el catálogo de alimentos.

Principios de diseño:
- Gemini SOLO elige alimentos (por código) y cantidades. Nunca calcula nutrientes:
  calorías y macros se calculan aquí con los valores del catálogo.
- Gemini solo ve alimentos del catálogo (ya filtrados por alergias / alimentos a evitar).
- La respuesta se valida y, si no cumple, se reintenta una vez con retroalimentación.
- No se envían datos identificables (nombre, teléfono, correo) a la API.
"""

import json
import os
import re
import time
import unicodedata
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from datos import repositorio

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MODELO_POR_DEFECTO = "gemini-3.5-flash-lite"
COMIDAS = ["Desayuno", "Colación I", "Comida", "Colación II", "Cena"]
REPARTO_KCAL = {"Desayuno": 0.25, "Colación I": 0.10, "Comida": 0.35, "Colación II": 0.10, "Cena": 0.20}
# % de las kcal para proteína / carbohidratos / grasa según la preferencia
REPARTO_MACROS = {
    "Alta en proteínas": (35, 40, 25),
    "Vegetariana": (20, 55, 25),
    "Baja en carbohidratos": (30, 30, 40),
}
REPARTO_MACROS_DEFECTO = (25, 50, 25)
TOLERANCIA_KCAL = 0.10      # desviación aceptada del total diario
MAX_INTENTOS = 2
REINTENTOS_ERRORES_TRANSITORIOS = 1
CANTIDAD_MIN, CANTIDAD_MAX = 5, 800


class GeneradorMenuError(Exception):
    """Error controlado al generar el menú (se muestra al usuario)."""


# ---------------------------------------------------------------- esquema de respuesta
class ItemIA(BaseModel):
    codigo: int = Field(description="Código numérico del alimento, tomado del catálogo")
    cantidad: float = Field(description="Cantidad en la unidad del alimento (g o ml)")


class ComidaIA(BaseModel):
    nombre: str = Field(description="Nombre exacto de la comida")
    alimentos: list[ItemIA]


class MenuIA(BaseModel):
    comidas: list[ComidaIA]
    notas: str = Field(description="Justificación breve del menú, máximo 3 frases")


SISTEMA = (
    "Eres un asistente de nutrición que ayuda a un nutriólogo a preparar el BORRADOR de un plan de "
    "alimentación de UN día. Reglas:\n"
    "1. Usa EXCLUSIVAMENTE alimentos del catálogo, referenciados por su código. No inventes alimentos.\n"
    "2. Respeta sin excepción alergias, alimentos a evitar y la preferencia alimentaria.\n"
    "3. Devuelve exactamente las comidas indicadas, con esos nombres exactos.\n"
    "4. Las cantidades van en la unidad del catálogo (g o ml), en múltiplos de 5, y deben ser porciones realistas.\n"
    "5. Procura que las calorías del día queden dentro de ±5% de la meta y los macros cerca de la meta.\n"
    "6. Varía categorías y evita repetir el mismo alimento en demasiadas comidas.\n"
    "7. Es un borrador: un profesional lo revisará."
)


# ---------------------------------------------------------------- utilidades
def _norm(texto):
    """Minúsculas y sin acentos, para comparar texto libre con nombres de alimentos."""
    texto = unicodedata.normalize("NFD", str(texto).casefold())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _terminos(texto_libre):
    """Convierte 'cacahuate, mariscos; leche' en una lista de términos normalizados."""
    return [t for t in (_norm(p).strip() for p in re.split(r"[,;\n]+", texto_libre or "")) if len(t) >= 3]


def _edad(fecha_nacimiento):
    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            nac = datetime.strptime(str(fecha_nacimiento).strip(), formato).date()
        except ValueError:
            continue
        hoy = date.today()
        return hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))
    return None


def _construir_perfil(paciente, medicion, objetivos):
    try:
        kcal = float(str(objetivos["calorias"]).replace(",", "."))
    except (KeyError, ValueError):
        raise GeneradorMenuError("Faltan las calorías objetivo del paciente.")
    preferencia = objetivos.get("preferencia") or "Sin preferencia"
    p, c, g = REPARTO_MACROS.get(preferencia, REPARTO_MACROS_DEFECTO)
    por_defecto = {"Proteínas": kcal * p / 100 / 4, "Carbohidratos": kcal * c / 100 / 4, "Grasa": kcal * g / 100 / 9}
    guardados = objetivos.get("macronutrientes") or {}
    macros = {k: round(guardados.get(k) or v) for k, v in por_defecto.items()}
    return {
        "edad": _edad(paciente.get("fecha_nacimiento")),
        "sexo": paciente.get("sexo"),
        "peso_kg": medicion.get("peso"),
        "estatura_cm": medicion.get("altura_cm"),
        "imc": medicion.get("imc"),
        "grasa_corporal_pct": medicion.get("grasa"),
        "masa_muscular_pct": medicion.get("masa_muscular"),
        "agua_corporal_pct": medicion.get("agua"),
        "objetivo_consulta": medicion.get("objetivo") or None,
        "nivel_actividad": medicion.get("actividad") or None,
        "calorias_objetivo_kcal": round(kcal),
        "macros_objetivo_g": macros,
        "preferencia": preferencia,
        "alergias": objetivos.get("alergias") or "ninguna",
        "alimentos_a_evitar": objetivos.get("evitar") or "ninguno",
        "reparto_kcal_por_comida": {k: round(kcal * v) for k, v in REPARTO_KCAL.items()},
    }, kcal


def _catalogo_filtrado(objetivos):
    """Catálogo activo sin los alimentos cuyo nombre coincide con alergias / alimentos a evitar."""
    excluir = _terminos(objetivos.get("alergias")) + _terminos(objetivos.get("evitar"))
    catalogo = []
    for a in repositorio.listar_catalogo(limite=500):
        if any(t in _norm(a["nombre"]) for t in excluir):
            continue
        catalogo.append(a)
    for codigo, a in enumerate(catalogo, start=1):
        a["codigo"] = codigo
    return catalogo


def _catalogo_a_texto(catalogo):
    lineas = ["codigo|nombre|categoria|unidad|kcal_100|prot_100|carb_100|grasa_100"]
    for a in catalogo:
        lineas.append(
            f"{a['codigo']}|{a['nombre']}|{a['categoria']}|{a['unidad_base']}|"
            f"{a['calorias_100']:g}|{a['proteinas_100']:g}|{a['carbohidratos_100']:g}|{a['grasas_100']:g}")
    return "\n".join(lineas)


def _construir_prompt(perfil, catalogo):
    return (
        f"PERFIL DEL PACIENTE (JSON):\n{json.dumps(perfil, ensure_ascii=False, indent=2)}\n\n"
        f"COMIDAS A GENERAR (nombres exactos): {', '.join(COMIDAS)}\n\n"
        f"CATÁLOGO DE ALIMENTOS PERMITIDOS (valores por 100 g o 100 ml):\n{_catalogo_a_texto(catalogo)}"
    )


# ---------------------------------------------------------------- validación y cálculo
def _resolver(menu_ia, catalogo, kcal_meta, ultimo_intento):
    por_codigo = {a["codigo"]: a for a in catalogo}
    problemas, menu, resumen = [], {}, {}
    total = {"kcal": 0.0, "prot": 0.0, "carb": 0.0, "grasa": 0.0}
    nombres_vistos = set()

    for comida in menu_ia.comidas:
        if comida.nombre not in COMIDAS:
            problemas.append(f"La comida '{comida.nombre}' no existe; usa solo: {', '.join(COMIDAS)}.")
            continue
        nombres_vistos.add(comida.nombre)
        items, sub = [], {"kcal": 0.0, "prot": 0.0, "carb": 0.0, "grasa": 0.0}
        for item in comida.alimentos:
            alimento = por_codigo.get(item.codigo)
            if not alimento:
                problemas.append(f"El código {item.codigo} no está en el catálogo (comida {comida.nombre}).")
                continue
            cantidad = round(item.cantidad / 5) * 5
            if not CANTIDAD_MIN <= cantidad <= CANTIDAD_MAX:
                problemas.append(
                    f"Cantidad no realista para {alimento['nombre']} ({item.cantidad:g}); "
                    f"usa entre {CANTIDAD_MIN} y {CANTIDAD_MAX}.")
                continue
            f = cantidad / 100
            sub["kcal"] += alimento["calorias_100"] * f
            sub["prot"] += alimento["proteinas_100"] * f
            sub["carb"] += alimento["carbohidratos_100"] * f
            sub["grasa"] += alimento["grasas_100"] * f
            items.append({
                "alimento_id": alimento["id"],
                "nombre": alimento["nombre"],
                "porcion": f"{cantidad:g} {alimento['unidad_base']}",
                "cantidad_base": float(cantidad),
                "unidad_base": alimento["unidad_base"],
            })
        if not items:
            problemas.append(f"La comida {comida.nombre} quedó sin alimentos válidos.")
            continue
        menu[comida.nombre] = items
        resumen[comida.nombre] = {k: round(v, 1) for k, v in sub.items()}
        for k in total:
            total[k] += sub[k]

    for faltante in (c for c in COMIDAS if c not in nombres_vistos):
        problemas.append(f"Falta la comida {faltante}.")

    desviacion = (total["kcal"] - kcal_meta) / kcal_meta if kcal_meta else 0
    if menu and abs(desviacion) > TOLERANCIA_KCAL:
        problemas.append(
            f"El total del día es {total['kcal']:.0f} kcal y la meta es {kcal_meta:.0f} kcal "
            f"({desviacion:+.0%}). Ajusta las cantidades para acercarte a la meta.")

    resumen["Total"] = {k: round(v, 1) for k, v in total.items()}
    return menu, resumen, problemas


# ---------------------------------------------------------------- llamada a Gemini
def _cliente():
    clave = os.getenv("GEMINI_API_KEY")
    if not clave:
        raise GeneradorMenuError("Falta GEMINI_API_KEY en el archivo .env.")
    return genai.Client(api_key=clave, http_options=types.HttpOptions(timeout=90_000))  # ms


def _llamar_gemini(cliente, contenido):
    modelo = os.getenv("GEMINI_MODEL", MODELO_POR_DEFECTO)
    for intento in range(REINTENTOS_ERRORES_TRANSITORIOS + 1):
        try:
            respuesta = cliente.models.generate_content(
                model=modelo,
                contents=contenido,
                config=types.GenerateContentConfig(
                    system_instruction=SISTEMA,
                    temperature=0.4,
                    response_mime_type="application/json",
                    response_schema=MenuIA,
                ),
            )
            return respuesta.parsed or MenuIA.model_validate_json(respuesta.text)
        except GeneradorMenuError:
            raise
        except Exception as error:
            detalle = str(error).upper()
            codigo = getattr(error, "code", None)
            estado = str(getattr(error, "status", "")).upper()
            es_tiempo_agotado = (
                codigo == 504
                or "DEADLINE_EXCEEDED" in detalle
                or "DEADLINE_EXCEEDED" in estado
                or "TIMED OUT" in detalle
            )
            if es_tiempo_agotado and intento < REINTENTOS_ERRORES_TRANSITORIOS:
                time.sleep(2)
                continue
            if es_tiempo_agotado:
                raise GeneradorMenuError(
                    "Gemini tardó demasiado en responder, incluso después de reintentar. "
                    "Espera un momento y vuelve a generar el menú."
                ) from error
            raise GeneradorMenuError(f"No se pudo obtener respuesta de Gemini: {error}") from error


# ---------------------------------------------------------------- API pública
def generar_menu(paciente, medicion, objetivos):

    perfil, kcal_meta = _construir_perfil(paciente, medicion, objetivos)
    catalogo = _catalogo_filtrado(objetivos)
    if len(catalogo) < 5:
        raise GeneradorMenuError(
            "El catálogo tiene muy pocos alimentos disponibles para este paciente "
            "(revisa el catálogo o las restricciones).")

    cliente = _cliente()
    prompt = _construir_prompt(perfil, catalogo)
    contenido = prompt
    menu = resumen = None
    problemas = []

    for intento in range(1, MAX_INTENTOS + 1):
        menu_ia = _llamar_gemini(cliente, contenido)
        menu, resumen, problemas = _resolver(menu_ia, catalogo, kcal_meta, intento == MAX_INTENTOS)
        if not problemas:
            return {"menu": menu, "resumen": resumen, "avisos": [], "notas": menu_ia.notas}
        contenido = [
            prompt,
            "TU RESPUESTA ANTERIOR:\n" + menu_ia.model_dump_json(),
            "Tuvo estos problemas, corrígelos y devuelve el menú completo:\n- " + "\n- ".join(problemas),
        ]

    if len(menu) < len(COMIDAS):
        raise GeneradorMenuError("Gemini no devolvió un menú completo. Intenta regenerarlo.")
    return {"menu": menu, "resumen": resumen, "avisos": problemas, "notas": menu_ia.notas}
