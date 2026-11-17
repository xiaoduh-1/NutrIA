"""Escaneo BLE y decodificación experimental de la báscula RTC-2017."""

import asyncio
from dataclasses import dataclass
import math

from PySide6.QtCore import QThread, Signal


MAC_OBJETIVO = "F8F2F09C2DC4"
PRODUCTO_OBJETIVO = "0A01"
SEGUNDOS_ESCANEO = 45


@dataclass(frozen=True)
class LecturaPeso:
    peso_kg: float
    estable: bool
    producto: str
    propiedades: str
    company_id: int
    paquete: str


def _normalizar_mac(valor):
    return str(valor or "").upper().replace(":", "").replace("-", "")


def decodificar_paquete(data, company_id=0):
    """Interpreta solo el formato observado; no utiliza el campo BIA desconocido."""
    try:
        data = bytes(data)
        if len(data) != 13:
            return None
        producto = data[4:6].hex().upper()
        mac_paquete = data[7:13].hex().upper()
        if producto != PRODUCTO_OBJETIVO or mac_paquete != MAC_OBJETIVO:
            return None

        propiedades = data[6]
        unidad_codigo = (propiedades >> 3) & 0b11
        precision_codigo = (propiedades >> 1) & 0b11
        estable = bool(propiedades & 0b00000001)

        unidades = {0: "kg", 1: "jin", 2: "lb", 3: "st"}
        decimales = {0: 1, 1: 0, 2: 2, 3: 1}[precision_codigo]
        factores_a_kg = {
            "kg": 1.0,
            "jin": 0.5,
            "lb": 0.45359237,
            "st": 6.35029318,
        }
        unidad = unidades[unidad_codigo]
        valor = int.from_bytes(data[0:2], byteorder="big") / (10 ** decimales)
        peso_kg = valor * factores_a_kg[unidad]
        if not math.isfinite(peso_kg) or not 0 < peso_kg < 1000:
            return None

        return LecturaPeso(
            peso_kg=round(peso_kg, 2),
            estable=estable,
            producto=producto,
            propiedades=f"0x{propiedades:02X}",
            company_id=int(company_id),
            paquete=data.hex().upper(),
        )
    except (TypeError, ValueError, OverflowError):
        return None


class LectorRTC2017(QThread):
    """Escanea anuncios sin GATT y termina al obtener una lectura estable."""

    estado = Signal(str)
    lectura_estable = Signal(object)
    error_lectura = Signal(str)
    cancelado = Signal()

    def __init__(self, parent=None, timeout=SEGUNDOS_ESCANEO):
        super().__init__(parent)
        self.timeout = timeout
        self._loop = None
        self._stop_event = None
        self._cancel_requested = False
        self._lectura_enviada = False
        self._estado_leyendo_enviado = False
        self._dispositivo_encontrado = False

    def cancelar(self):
        self._cancel_requested = True
        if self._loop and self._stop_event:
            self._loop.call_soon_threadsafe(self._stop_event.set)

    def run(self):
        try:
            asyncio.run(self._escanear())
        except ModuleNotFoundError as error:
            if error.name == "bleak":
                self.error_lectura.emit(
                    "Falta instalar Bleak. Ejecuta: python -m pip install -r requirements-postgres.txt"
                )
            else:
                self.error_lectura.emit(f"Error en el escaneo BLE: {error}")
        except Exception as error:
            self.error_lectura.emit(f"Error en la medición: {error}")
        finally:
            self._loop = None
            self._stop_event = None

    async def _escanear(self):
        from bleak import BleakScanner

        self._loop = asyncio.get_running_loop()
        self._stop_event = asyncio.Event()

        def recibir_anuncio(device, advertisement):
            if _normalizar_mac(device.address) != MAC_OBJETIVO:
                return
            self._dispositivo_encontrado = True

            for company_id, payload in advertisement.manufacturer_data.items():
                lectura = decodificar_paquete(payload, company_id)
                if lectura is None:
                    continue
                if not self._estado_leyendo_enviado:
                    self._estado_leyendo_enviado = True
                    self.estado.emit("Leyendo peso...")
                if lectura.estable and not self._lectura_enviada:
                    self._lectura_enviada = True
                    self.lectura_estable.emit(lectura)
                    self._stop_event.set()
                    return

        async with BleakScanner(detection_callback=recibir_anuncio):
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self.timeout)
            except asyncio.TimeoutError:
                if not self._cancel_requested and not self._lectura_enviada:
                    if self._estado_leyendo_enviado:
                        mensaje = "No se recibió un peso estable. Baja de la báscula y vuelve a intentarlo."
                    elif self._dispositivo_encontrado:
                        mensaje = "Se encontró la báscula, pero el paquete recibido no coincide con el formato esperado."
                    else:
                        mensaje = "No se encontró la báscula. Verifica que esté encendida y cerca del equipo."
                    self.error_lectura.emit(mensaje)

        if self._cancel_requested and not self._lectura_enviada:
            self.cancelado.emit()
