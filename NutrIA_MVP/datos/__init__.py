"""Acceso a datos del MVP."""

from .repositorio_transicional import RepositorioTransicional

repositorio = RepositorioTransicional()

__all__ = ["repositorio"]
