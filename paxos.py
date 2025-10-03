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


def funcion_paxos(tests: str) -> None:

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
    
    # PAXOS:
    nodos_aceptantes = []
    nodos_proponentes = []

    # Paso 1: Revisamos los nodos aceptantes
    row = lineas_clear[0]
    partes = row.split(";")
    for i in range(len(partes)):
        s = partes[i].strip()
        if s != "":
            nodos_aceptantes.append(s)
    nodos_aceptantes = f_aux.quitar_duplicados(nodos_aceptantes)
    nodos_aceptantes = {s: {
        "promised_n": None,
        "accepted_n": None,
        "accepted_value": None,
    } for s in nodos_aceptantes}

    # Paso 2: Revisamos los nodos proponentes
    row = lineas_clear[1]
    partes = row.split(";")
    for i in range(len(partes)):
        s = partes[i].strip()
        if s != "":
            nodos_proponentes.append(s)
    nodos_proponentes = f_aux.quitar_duplicados(nodos_proponentes)

    # Paso 3: Iteramos sobre los eventos para procesarlos
    for i in range(2, len(lineas_clear)):
        evento = lineas_clear[i].strip()
        separados = evento.split(";")
        comando = separados[0].strip()
        if comando == "Prepare" and len(separados) == 3:

            id_prop = separados[1].strip()
            n = int(separados[2].strip())
            if id_prop in nodos_proponentes:
                for id_acept in nodos_aceptantes.keys():
                    # Se itera sobre todos los aceptantes
                    promised_n = nodos_aceptantes[id_acept]["promised_n"]
                    if promised_n is None or n > promised_n:
                        # Acepta el prepare
                        nodos_aceptantes[id_acept]["promised_n"] = n    
                                                    
        elif comando == "Accept" and len(separados) == 4:
            id_prop = separados[1].strip()
            n = int(separados[2].strip())
            accion = separados[3].strip()
            
            if id_prop in nodos_proponentes:
                total = 0
                Av = None # valor a aceptar (accion)
                An = 0 # valor de n que acepto
                for id_acept in nodos_aceptantes.keys():
                    # Se itera sobre todos los aceptantes
                    promised_n = nodos_aceptantes[id_acept]["promised_n"]
                    accepted_n = nodos_aceptantes[id_acept]["accepted_n"]
                    accepted_value = nodos_aceptantes[id_acept]["accepted_value"]
                    if promised_n == n and accepted_n is not None and accepted_n > An:
                        An = accepted_n
                        Av = accepted_value

                    if promised_n is None or n >= promised_n: 
                        total+=1
                if total * 2 > len(nodos_aceptantes): # En este caso se acepta.
                    for id_acept in nodos_aceptantes.keys():
                        promised_n = nodos_aceptantes[id_acept]["promised_n"]
                        if promised_n is None or n >= promised_n:                            
                            if An > 0: # No puede enviar lo que quiera
                                nodos_aceptantes[id_acept]["accepted_n"] = n
                                nodos_aceptantes[id_acept]["accepted_value"] = Av
                            else:
                                nodos_aceptantes[id_acept]["accepted_n"] = n
                                nodos_aceptantes[id_acept]["accepted_value"] = accion

        elif comando == "Stop":
            pass
        elif comando == "Start":
            pass
        elif comando == "Learn":
            pass
        elif comando == "Log":
            pass

    # for l in lineas_clear:
    #     print(l)