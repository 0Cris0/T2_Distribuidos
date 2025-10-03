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

import func_auxiliares as f_aux

def procesar_comandos_raft(nodos, lider, comando, argumentos):
    if(comando == "Send"):
        print("Send")
    elif(comando == "Spread"):
        print("Spread")
    elif(comando == "Stop"):
        print("Stop")
    elif(comando == "Start"):
        print("Start")
    elif(comando == "Log"):
        print("Log")

def exec_raft(tests: str) -> None:
    """ # Completar con tu implementación o crea más archivos y funciones
    print(f"Ejecutando Raft con {tests}")
    pass """
    # El primer paso es leer el archivo de tests
    with open(tests, "r", encoding="utf-8") as f:
        lineas = f.readlines()
    
    # Procesamos cada una de las lineas para limpiarlas
    lineas_clear = []
    for linea in lineas:
        # Eliminamos comentarios
        procesamiento = f_aux.eliminar_comentarios(linea)
        if len(procesamiento) > 0:
            lineas_clear.append(procesamiento)
    
    # RAFT:
    # Primera línea: Nodos y timeouts
    nodos = {}
    lider = None
    linea_nodos = lineas_clear[0].split(";")
    for datos_nodo in linea_nodos:
        # nodos.append(nodo.strip())
        datos_nodo = datos_nodo.strip().split(",")
        nodos[datos_nodo[0]] = int(datos_nodo[1])
        print(f"Nodo {datos_nodo[0]} con timeout {datos_nodo[1]}")
    # TODO:Ver que no haya problema con los espacios en blanco
    nodos = f_aux.quitar_duplicados(nodos)

    # Líneas siguientes: Procesamiento y lectura de comandos
    for linea in range(1, len(lineas_clear)):
        linea = lineas_clear[linea].strip().split(";")
        comando = linea[0]
        argumentos = linea[1]
        procesar_comandos_raft(nodos, lider, comando, argumentos)

exec_raft("casos_Raft/test_01.txt")