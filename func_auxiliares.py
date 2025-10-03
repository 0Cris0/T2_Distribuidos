""" from __future__ import annotations  # Solo lo dejo por si lo necesitan. Lo pueden eliminar
from sys import argv """

# Librerías adicionales por si las necesitan
# No son obligatorias y no tampoco tienen que usarlas todas
# No pueden agregar ningun otro import que no esté en esta lista
""" import os
import typing
import collections
import itertools
import dataclasses
import enum """


def eliminar_comentarios(linea) -> str:
    # Eliminamos todo lo del comentario a la derecha
    procesado = ""
    for c in linea:
        if c == "#":
            break
        else:
            procesado += c
    return procesado.rstrip()

def quitar_duplicados(lista):
    vistos = set()
    resultado = []
    for item in lista:
        if item not in vistos:
            vistos.add(item)
            resultado.append(item)
    return resultado