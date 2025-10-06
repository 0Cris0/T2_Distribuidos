""" from __future__ import annotations  # Solo lo dejo por si lo necesitan. Lo pueden eliminar
from sys import argv """

# Librerías adicionales por si las necesitan
# No son obligatorias y no tampoco tienen que usarlas todas
# No pueden agregar ningun otro import que no esté en esta lista
import os
import typing
import collections
import itertools
import dataclasses
import enum

bbdd = {}
logs_bbdd = []

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

def print_bbdd():
    # Este es un print de base de datos para debuguear
    print("Base de datos actual:")
    max_end = 0
    for k, v in bbdd.items():
        print(f"  {k}: {v}")
        if len(v) + len(k) + 3 > max_end:
            max_end = len(v) + len(k) + 3

    print(f"{'-' * max_end}")


def escribir_logs(algoritmo: str, ruta_test: str, logs: typing.List[typing.Tuple[str, str]]) -> None:
    # Se va a escribir un txt con los logs
    ruta_log = "logs/"
    nombre_salida = f"{algoritmo}_{os.path.basename(ruta_test)}"
    ruta_log = os.path.join("logs", nombre_salida)

    with open(ruta_log, "w", encoding="utf-8") as f:
        # LOGS
        f.write("LOGS\n")
        if logs:
            for log in logs:
                f.write(f"{log[0]}={log[1]}\n")
        else:
            f.write("No hubo logs\n")
        
        # BBDD
        f.write("BASE DE DATOS\n")
        if bbdd:
            for k, v in bbdd.items():
                f.write(f"{k}={v}\n")
        else:
            f.write("No hay datos\n")

def procesar_accion(accion: str) -> bool:
    partes = accion.split("-", 2) # Dividir en 3 partes como máximo
    
    # Las 3 partes son: comando, variable, valor
    comando = partes[0]
    variable = partes[1]
    valor = partes[2] if len(partes) > 2 else ""

    # Revisamos los distintos comandos
    if comando == "SET":
        
        bbdd[variable] = valor
        return True
    elif comando == "ADD":
        # Revisamos si estamos trabajando con str o int
        valor_bbdd = bbdd.get(variable)
        resultado = None
        if valor_bbdd is None:
            # Funciona como set en este caso
            resultado = valor
        else:
            if str(valor_bbdd).isdigit() and valor.isdigit():
                # En este caso, ambos son enteros
                resultado = int(valor_bbdd) + int(valor)
            else:
                # En este caso, alguno de los 2 es un string
                resultado = str(valor_bbdd) + str(valor)
        # Ahora, asignamos el valor a la bbdd
        bbdd[variable] = str(resultado)
        return True
    elif comando == "DEL":
        bbdd.pop(variable, None) # Se elimina solo si existe
        return True
    return False