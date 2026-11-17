"""Adaptador de prueba que utiliza el mismo cliente SMTP de NutrIA."""

from datos.correo_smtp import enviar_correo

__all__ = ["enviar_correo"]
