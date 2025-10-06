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

# nodos = {}
"""
idea de nodo:
    NAME = {
        "term" = 0,
        "timeout" = 0,
        "t_actul" = 0
        "activo" = True,
        "ultimo_term_votado": -1,
        "logs" = [],
        "name": NAME,
    }
"""
# lider = None

def mayoria_lider(n_aceptan, n_nodos):
    if(n_aceptan >= (n_nodos // 2 +1)):
        return "elegido"
    return "no elegido"

def aumentar_term(nodos, nodo_name, posible_valor_mayor):
    nodo = nodos[nodo_name]
    if(nodo["term"] < posible_valor_mayor):
        nodo["term"] = posible_valor_mayor
    return nodos

def votar_por_lider(nodos, candidato):
    aceptan = 1
    rechazan = 0
    term_candidato = candidato["term"]
    for nodo in nodos.keys():
        nodo = nodos[nodo]
        # Si es el propoio nodo o está inactivo lo ignora
        if(nodo != candidato and nodo["activo"] != False):
            # Si el term del candidato es menor que votante, vota rechazo
            if(nodo["term"] > term_candidato):
                nodo["ultimo_term_votado"] = term_candidato
                rechazan += 1
                nodos = aumentar_term(nodos, candidato["name"], nodo["term"])
                continue

            # Si ya votó en el term actual, vota rechazo
            if(nodo["ultimo_term_votado"] == term_candidato):
                rechazan += 1
                nodos = aumentar_term(nodos, nodo["name"], term_candidato)
                nodos = aumentar_term(nodos, candidato["name"], nodo["term"])
                continue
            
            # Si votante no tiene logs, vota a favor
            if(len(nodo["logs"])==0):
                aceptan+=1
                nodo["ultimo_term_votado"] = term_candidato
                nodos = aumentar_term(nodos, nodo["name"], term_candidato)
                nodos = aumentar_term(nodos, candidato["name"], nodo["term"])
                continue
            else:
                ultimo_log_candidato = candidato["logs"][-1]
                ultimo_log = nodo["logs"][-1]
                condicion_largo_logs = (len(candidato["logs"]) >= len(nodo["logs"]))

                # Si term del último log es term mayor que el último del actual, vota a favor
                if(ultimo_log_candidato[1] > ultimo_log[1]):
                    aceptan+=1
                    nodo["ultimo_term_votado"] = term_candidato
                    nodos = aumentar_term(nodos, nodo["name"], term_candidato)
                    nodos = aumentar_term(nodos, candidato["name"], nodo["term"])
                    continue

                # Si el term del último log es igual, pero candidato tiene log >= largo
                # Vota a favor
                if(ultimo_log_candidato[1] == ultimo_log[1] and condicion_largo_logs):
                    aceptan+=1
                    nodo["ultimo_term_votado"] = term_candidato
                    nodos = aumentar_term(nodos, nodo["name"], term_candidato)
                    nodos = aumentar_term(nodos, candidato["name"], nodo["term"])
                    continue

                # En todo otro caso +
                # Si el term del último log fue menor al del votante, voto rechazo
                # if(ultimo_log_candidato[1] < ultimo_log[1]):
                else:
                    rechazan += 1
                    nodo["ultimo_term_votado"] = term_candidato
                    nodos = aumentar_term(nodos, nodo["name"], term_candidato)
                    continue
    return mayoria_lider(aceptan, len(nodos))


def imprimir_activos(nodos: dict):
    return 
    #print("=== NODOS ACTIVOS ===")
    for nombre, datos in nodos.items():
        if datos.get("activo"):
            logs = (
                ", ".join(f"{log[0]}@{log[1]}" for log in datos["logs"])
                if datos["logs"]
                else "-"
            )
            print(
                f"{nombre}: term={datos['term']} | timeout={datos['timeout']} | "
                f"ultimo_voto={datos['ultimo_term_votado']} | logs=[{logs}]"
            )
    #print("======================")


def eleccion_lider(nodos: dict, lider: dict):
    mayoria = False
    contador_activos = 0
    for nodo in nodos:
        nodo = nodos[nodo]
        if(nodo["activo"] == True):
            contador_activos += 1
        if(contador_activos >= len(nodos)// 2 +1):
            mayoria = True
            break
    if(contador_activos < len(nodos)// 2 +1):
        return (lider, nodos)
    while(lider == None and mayoria == True):
        for nodo in nodos.keys():
            nodo = nodos[nodo]
            if(nodo["activo"] == True):
                nodo["t_actual"] +=1
                if(nodo["t_actual"] == nodo["timeout"]):
                    nodo["term"] += 1
                    nodo["ultimo_term_votado"] = nodo["term"]
                    resultado = votar_por_lider(nodos, nodo)
                    if(resultado == "elegido"):
                        lider = nodo
                        nodo["t_actual"] = 0
                        nodos = enviar_heartbeat(lider, nodos)
                        break
                    else:
                        nodo["t_actual"] = 0
    return (lider, nodos)

def enviar_heartbeat(lider, nodos):
    for nodo in nodos.keys():
        nodo = nodos[nodo]
        if(nodo != lider and nodo["activo"] == True):
            nodo["t_actual"] = 0
    return nodos

def replicar(nodos, nodo_actual, logs_lider):
    nodo = nodos[nodo_actual]
    logs_actual = nodo["logs"]
    terms_logs_lider = []
    nueva_lista = []

    for log_l in logs_lider:
        term = log_l[1]
        if(term not in terms_logs_lider):
            terms_logs_lider.append(term)
        nueva_lista.append(log_l)
    # Recorro, guardando solo los que no tienen terms que ya tenía líder
    maximo_term_l = max(terms_logs_lider)

    for log in logs_actual:
        term = log[1]
        if(term not in terms_logs_lider and term <= maximo_term_l):
            nueva_lista.append(log)
    # Ordeno
    nuevos_logs_ordenados = sorted(nueva_lista, key=lambda x: x[1])
    # Nota: utilicé ChatGPT para encontrar una manera de sortear esto
    nodos[nodo_actual]["logs"] = nuevos_logs_ordenados
    return nodos

def consolidar(nodos, lider, ya_consolidadas):
    acciones_consolidadas = []
    if(lider["logs"] != []):
        for accion in lider["logs"]:
            if(accion not in ya_consolidadas):
                if(accion[1] == lider["term"]):
                    contador = 0
                    for nodo in nodos.keys():
                        nodo = nodos[nodo]
                        if(accion in nodo["logs"] and nodo["activo"] == True):
                            contador += 1
                    if(contador >= len(nodos)//2 + 1):
                            for subaccion in lider["logs"]:
                                if(subaccion in acciones_consolidadas):
                                    continue
                                else:
                                    acciones_consolidadas.append(subaccion)
                                    if(subaccion == accion):
                                        break             
    acciones_consolidadas = sorted(acciones_consolidadas, key=lambda x: x[1])

    if(len(acciones_consolidadas) != 0):
        # Osea, existen acciones consolidadas
        for accion in acciones_consolidadas:
            if(accion not in ya_consolidadas):
                ya_consolidadas.append(accion)
                f_aux.procesar_accion(accion[0])
    return (lider, nodos, ya_consolidadas)

def procesar_comandos_raft(nodos, lider, comando, linea, ya_consolidadas):
    if(lider == None and comando in ["Send", "Spread", "Start"]):
        (lider, nodos) = eleccion_lider(nodos, lider)
    if(comando == "Send" and lider != None):
        term_lider = lider["term"]
        accion = linea[1]
        lider["logs"].append((accion, term_lider))
    elif(comando == "Stop"):
        name_nodo = linea[1]
        if(name_nodo in nodos):
            nodos[name_nodo]["activo"] = False
            if(nodos[name_nodo] == lider):
                lider = None
                nodos = enviar_heartbeat(lider, nodos)
    elif(comando == "Start"):
        name_nodo = linea[1]
        if(name_nodo in nodos):
            nodos[name_nodo]["activo"] = True
    elif(comando == "Spread" and lider != None):
        lista_nodos = linea[1]
        if(len(lista_nodos) != 0):
            for nodo in nodos.keys():
                nodo_name = nodo
                nodo = nodos[nodo]
                if(nodo != lider and nodo["activo"] == True):
                    if(nodo["name"] in lista_nodos):
                        nodos = replicar(nodos, nodo_name, lider["logs"])
            (lider, nodos, ya_consolidadas) = consolidar(nodos, lider, ya_consolidadas)
    elif(comando == "Log"):
        variable_log = linea[1].strip()
        valor_log = f_aux.bbdd.get(variable_log, "Variable no existe")
        f_aux.logs_bbdd.append((variable_log,valor_log))
    return (lider, nodos, ya_consolidadas)


def armar_nodo(nodos, nombre_nodo, timeout):
    nodos[nombre_nodo] = {
        "timeout": timeout,
        "term": 0,
        "t_actual": 0,
        "activo": True,
        "ultimo_term_votado": -1,
        "logs": [],
        "name": nombre_nodo
    }
    return nodos

def funcion_raft(tests: str) -> None:
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
            # #print(procesamiento)
    
    # RAFT:
    # Primera línea: Nodos y timeouts
    nodos = {}
    lider = None
    ya_consolidadas = []
    linea_nodos = lineas_clear[0].split(";")
    for datos_nodo in linea_nodos:
        # nodos.append(nodo.strip())
        datos_nodo = datos_nodo.strip().split(",")
        nombre_nodo = datos_nodo[0]
        timeout = int(datos_nodo[1])
        nodos = armar_nodo(nodos, nombre_nodo, timeout)

    # Líneas siguientes: Procesamiento y lectura de comandos
    for linea in range(1, len(lineas_clear)):
        linea = lineas_clear[linea].strip().split(";")
        comando = linea[0]
        (lider, nodos, ya_consolidadas) = procesar_comandos_raft(nodos, lider, comando, linea, ya_consolidadas)
    f_aux.escribir_logs("Raft", tests, f_aux.logs_bbdd)

# funcion_raft("casos_Raft/test_02.txt")