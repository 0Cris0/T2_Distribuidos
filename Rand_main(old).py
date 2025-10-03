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

# Variables globales
bbdd = {}
logs_bbdd = []

def print_bbdd():
    # Este es un print de base de datos para debuguear
    print("Base de datos actual:")
    max_end = 0
    for k, v in bbdd.items():
        print(f"  {k}: {v}")
        if len(v) + len(k) + 3 > max_end:
            max_end = len(v) + len(k) + 3

    print(f"{max_end * "-"}")


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


def exec_paxos(test: str) -> None:

    # El primer paso es leer el archivo de test
    with open(test, "r", encoding="utf-8") as f:
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
        "alive": True
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
                    if not nodos_aceptantes[id_acept]["alive"]:
                        continue # Si el nodo no está vivo, no responde
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
                    if not nodos_aceptantes[id_acept]["alive"]:
                        continue # Si el nodo no está vivo, no responde
                    # Se itera sobre todos los aceptantes
                    promised_n = nodos_aceptantes[id_acept]["promised_n"]
                    accepted_n = nodos_aceptantes[id_acept]["accepted_n"]
                    accepted_value = nodos_aceptantes[id_acept]["accepted_value"]
                    if promised_n == n:
                        total += 1
                        if accepted_n is not None and accepted_n > An:
                            An = accepted_n
                            Av = accepted_value

                for id_acept in nodos_aceptantes.keys():
                    if not nodos_aceptantes[id_acept]["alive"]:
                        continue
                    if nodos_aceptantes[id_acept]["promised_n"] == n:
                        if An > 0:
                            nodos_aceptantes[id_acept]["accepted_n"] = n
                            nodos_aceptantes[id_acept]["accepted_value"] = Av
                        else:
                            nodos_aceptantes[id_acept]["accepted_n"] = n
                            nodos_aceptantes[id_acept]["accepted_value"] = accion


        elif comando == "Stop":
          idacept = separados[1].strip()
          if idacept in nodos_aceptantes:
                nodos_aceptantes[idacept]["alive"] = False  
        elif comando == "Start":
            idacept = separados[1].strip()
            if idacept in nodos_aceptantes:
                    nodos_aceptantes[idacept]["alive"] = True
        elif comando == "Learn":
            conteo = {}
            for id_acept in nodos_aceptantes.keys():
                if not nodos_aceptantes[id_acept]["alive"]:
                    continue # Si el nodo no está vivo, no responde
                if nodos_aceptantes[id_acept]["accepted_value"] is not None:
                    val = nodos_aceptantes[id_acept]["accepted_value"]
                    conteo[val] = conteo.get(val, 0) + 1
            # Revisamos si hay mayoria
            mayoria = (len(nodos_aceptantes) // 2) + 1
            for val, cnt in conteo.items():
                if cnt >= mayoria:
                    # Accion aceptada, se procesa
                    print(val)
                    procesar_accion(val)
                    # reseteo estado nodos aceptantes activos
                    for id_acept in nodos_aceptantes.keys():
                        if nodos_aceptantes[id_acept]["alive"]:
                            nodos_aceptantes[id_acept]["promised_n"] = None
                            nodos_aceptantes[id_acept]["accepted_n"] = None
                            nodos_aceptantes[id_acept]["accepted_value"] = None
                    break

        elif comando == "Log":
            variable_log = separados[1].strip()
            valor_log = bbdd.get(variable_log, "Variable no existe")
            logs_bbdd.append((variable_log,valor_log))

    # Paso 4: Se escriben los logs
    escribir_logs("Paxos", test, logs_bbdd)


def exec_raft(test: str) -> None:
    # Completar con tu implementación o crea más archivos y funciones
    print(f"Ejecutando Raft con {test}")
    pass

if __name__ == "__main__":
    # Completar con tu implementación o crea más archivos y funciones

    algoritmo = argv[1]
    test = argv[2]
    if algoritmo == "Paxos":
        exec_paxos(test)
    elif algoritmo == "Raft":
        exec_raft(test)

    # print("Mi nombre es Shinichi Kudo, tengo 17 años, reconocido como el mejor de")
    # print("los detectives, pero unos hombres me obligaron a tomar una droga,")
    # print("así fue como me convertí en Edogawa Conan, a pesar de ser un niño")
    # print("mi inteligencia es la de un joven normal y para mí no hay caso")
    # print("difícil de resolver.!")