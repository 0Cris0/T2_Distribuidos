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


def exec_paxos(tests: str) -> None:

    # El primer paso es leer el archivo de tests
    with open(tests, "r", encoding="utf-8") as f:
        lineas = f.readlines()
    
    # Procesamos cada una de las lineas para limpiarlas
    lineas_clear = []
    for linea in lineas:
        # Eliminamos comentarios
        procesamiento = eliminar_comentarios(linea)
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
    nodos_aceptantes = quitar_duplicados(nodos_aceptantes)
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
    nodos_proponentes = quitar_duplicados(nodos_proponentes)

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

    
def exec_raft(tests: str) -> None:
    # Completar con tu implementación o crea más archivos y funciones
    print(f"Ejecutando Raft con {tests}")
    pass

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