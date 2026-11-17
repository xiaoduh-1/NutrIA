"""Estimaciones antropométricas de grasa y agua corporal.

Son predicciones poblacionales, no mediciones directas de composición corporal.
"""

from datetime import date, datetime
import math


def _convertir_fecha(valor):
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if not valor:
        return None
    texto = str(valor).strip()
    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    return None


def calcular_edad(fecha_nacimiento, fecha_referencia=None):
    nacimiento = _convertir_fecha(fecha_nacimiento)
    referencia = _convertir_fecha(fecha_referencia) if fecha_referencia else date.today()
    if nacimiento is None or referencia is None or nacimiento > referencia:
        return None
    return (
        referencia.year - nacimiento.year
        - ((referencia.month, referencia.day) < (nacimiento.month, nacimiento.day))
    )


def estimar_composicion_corporal(peso_kg, altura_cm, imc, edad, sexo):
    """Retorna % grasa Deurenberg y TBW Watson (L y % del peso), si aplican."""
    resultado = {"grasa_pct": None, "agua_litros": None, "agua_pct": None}
    sexo_normalizado = str(sexo or "").strip().casefold()
    if sexo_normalizado not in {"masculino", "femenino"}:
        return resultado

    try:
        peso_kg = float(peso_kg)
        altura_cm = float(altura_cm)
        imc = float(imc)
        edad = int(edad)
    except (TypeError, ValueError, OverflowError):
        return resultado
    if (
        not all(math.isfinite(valor) for valor in (peso_kg, altura_cm, imc))
        or peso_kg <= 0 or altura_cm <= 0 or imc <= 0 or edad < 0
    ):
        return resultado

    sexo_codigo = 1 if sexo_normalizado == "masculino" else 0

    # Deurenberg et al. (1991) separó la ecuación infantil de la adulta.
    # Su muestra abarcó 7–83 años y BMI 13.9–40.9 kg/m².
    if 7 <= edad <= 15 and 13.9 <= imc <= 40.9:
        grasa = 1.51 * imc - 0.70 * edad - 3.6 * sexo_codigo + 1.4
        if math.isfinite(grasa) and 0 <= grasa <= 100:
            resultado["grasa_pct"] = round(grasa, 1)
    elif 16 <= edad <= 83 and 13.9 <= imc <= 40.9:
        grasa = 1.20 * imc + 0.23 * edad - 10.8 * sexo_codigo - 5.4
        if math.isfinite(grasa) and 0 <= grasa <= 100:
            resultado["grasa_pct"] = round(grasa, 1)

    # Watson et al. (1980) desarrolló estas ecuaciones para adultos.
    if edad >= 18:
        if sexo_codigo == 1:
            agua_litros = (
                2.447 - 0.09516 * edad + 0.1074 * altura_cm + 0.3362 * peso_kg
            )
        else:
            agua_litros = -2.097 + 0.1069 * altura_cm + 0.2466 * peso_kg
        agua_pct = 100 * agua_litros / peso_kg if peso_kg else math.nan
        if (
            math.isfinite(agua_litros) and math.isfinite(agua_pct)
            and 0 < agua_litros < peso_kg and 0 < agua_pct < 100
        ):
            resultado["agua_litros"] = round(agua_litros, 1)
            resultado["agua_pct"] = round(agua_pct, 1)

    return resultado
