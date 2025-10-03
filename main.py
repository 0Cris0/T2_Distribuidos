from __future__ import annotations  # Solo lo dejo por si lo necesitan. Lo pueden eliminar
from sys import argv

# Librerías adicionales por si las necesitan
# No son obligatorias y no tampoco tienen que usarlas todas
# No pueden agregar ningun otro import que no esté en esta lista
import os
import typing
import collections
import itertools
import dataclasses
import enum

from paxos import funcion_paxos
from raft import funcion_raft 

# Recuerda que no se permite importar otros módulos/librerías a excepción de los creados
# por ustedes o las ya incluidas en este main.py
bbdd = {}

def print_bbdd():
    # Este es un print de base de datos para debuguear
    print("Base de datos actual:")
    max_end = 0
    for k, v in bbdd.items():
        print(f"  {k}: {v}")
        if len(v) + len(k) + 3 > max_end:
            max_end = len(v) + len(k) + 3

    print(f"{max_end * "-"}")

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

def exec_paxos(tests: str) -> None:
    funcion_paxos(tests)

    
def exec_raft(tests: str) -> None:
    funcion_raft(tests)

if __name__ == "__main__":
    # Completar con tu implementación o crea más archivos y funciones
    print(argv)

    algoritmo = argv[1]
    tests = argv[2]

    if algoritmo == "Paxos":
        exec_paxos(tests)
    elif algoritmo == "Raft":
        exec_raft(tests)

    # print("Mi nombre es Shinichi Kudo, tengo 17 años, reconocido como el mejor de")
    # print("los detectives, pero unos hombres me obligaron a tomar una droga,")
    # print("así fue como me convertí en Edogawa Conan, a pesar de ser un niño")
    # print("mi inteligencia es la de un joven normal y para mí no hay caso")
    # print("difícil de resolver.!")