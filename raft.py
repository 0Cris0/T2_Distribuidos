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

nodos = {}
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
lider = None

def mayoria_lider(n_aceptan, n_nodos):
    if(n_aceptan >= (n_nodos // 2 +1)):
        return "elegido"
    return "no elegido"

def Votacion(nodos, candidato):
    aceptan = 1
    rechazan = 0
    ultimo_log_candidato = candidato["logs"][-1]
    term_candidato = candidato["term"]
    for nodo in nodos.keys():
        nodo = nodos[nodo]
        # Si es el propoio nodo o está inactivo lo ignora
        if(nodo != candidato and nodo["activo"] != False):
            # Si ya votó en el term actual, vota rechazo
            if(nodo["ultimo_term_votado"] == term_candidato):
                rechazan += 1
                if(term_candidato > nodo["term"]): #TODO: Duda si esto está bien
                    nodo["term"] = term_candidato
                continue
            # Si el term del candidato es menor que votante, vota rechazo
            if(nodo["term"] > term_candidato):
                nodo["ultimo_term_votado"] = term_candidato #TODO: Duda si esto está bien
                rechazan += 1
                continue
            # Si votante no tiene logs, vota a favor
            if(len(nodo["logs"])==0):
                aceptan+=1
                nodo["ultimo_term_votado"] = term_candidato
                if(term_candidato > nodo["term"]): #TODO: Duda si esto está bien
                    nodo["term"] = term_candidato
                continue
            # Casos con igual term
            # if(term_candidato == nodo["term"]):
            else:
                ultimo_log = nodo["logs"][-1]
                condicion_largo_logs = (len(candidato["logs"]) >= len(nodo["logs"]))
                # Si term del último log es term mayor que el último del actual, vota a favor
                if(ultimo_log_candidato[1] > ultimo_log[1]):
                    aceptan+=1
                    nodo["ultimo_term_votado"] = term_candidato
                    if(term_candidato > nodo["term"]): #TODO: Duda si esto está bien
                        nodo["term"] = term_candidato
                    continue
                # Si el term del último log es igual, pero candidato tiene log >= largo
                # Vota a favor
                if(ultimo_log_candidato[1] == ultimo_log[1] and condicion_largo_logs):
                    aceptan+=1
                    nodo["ultimo_term_votado"] = term_candidato
                    if(term_candidato > nodo["term"]): #TODO: Duda si esto está bien
                        nodo["term"] = term_candidato
                    continue
                # En todo otro caso +
                # Si el term del último log fue menor al del votante, voto rechazo
                # if(ultimo_log_candidato[1] < ultimo_log[1]):
                else:
                    rechazan += 1
                    nodo["ultimo_term_votado"] = term_candidato #TODO: Duda si esto está bien
                    if(term_candidato > nodo["term"]): #TODO: Duda si esto está bien
                        nodo["term"] = term_candidato
                    continue
    return mayoria_lider(aceptan, len(nodos))

def enviar_heartbeat(lider, nodos):
    for nodo in nodos.keys():
        nodo = nodos[nodo]
        if(nodo != lider and nodo["activo"] == True):
            nodo["t_actual"] = 0



def eleccion_lider(nodos: dict, lider: dict):
    # TODO: Ver si las cosas cambian por referencia o no, sino retornar cosas
    # Considerar implementar contador
    while(lider == None):
        for nodo in nodos.keys():
            nodo = nodos[nodo]
            if(nodo["activo"] == True):
                nodo["t_actual"] +=1
                if(nodo["t_actual"] == nodo["timeout"]):
                    nodo["term"] += 1
                    nodo["ultimo_term_votado"] = nodo["term"]
                    resultado = Votacion(nodos, nodo)
                    if(resultado == "elegido"):
                        lider = nodo
                        for nodo in nodos.keys():
                            if(nodo != lider):
                                nodo["t_actual"] = 0
                        break
                    else:
                        nodo["t_actual"] = 0

def replicar(nodo_actual, logs_lider):
    logs_actual = nodo_actual["logs"]
    terms_logs_lider = []
    nueva_lista = []
    for log_l in logs_lider:
        term = log_l[1]
        if(term not in terms_logs_lider):
            terms_logs_lider.append(term)
            nueva_lista.append(log_l)
    for log in logs_actual:
        term = log[1]
        if(term not in terms_logs_lider):
            nueva_lista.append(log)
    nodo_actual["logs"] = nueva_lista

def consolidar(nodos, lider):
    term_actual = lider["term"]
    consolidadas = []
    for log in lider["logs"]:
        # TODO: Implementar sistema para logs indirectos
        contador = 0
        for nodo in nodos:
            nodo = nodos[nodo]
            if(lider != nodo and log[1]==term_actual):
                if(log in nodo["logs"]):
                    contador+=1
        if(contador >= len(nodos)//2 + 1):
            consolidadas.append(log)
    if(len(consolidadas) != 0):
        # Mandar a BD
        print("TODOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOooooo")

def procesar_comandos_raft(nodos, lider, comando, linea):
    if(comando == "Send" and lider != None):
        term_lider = lider["term"]
        accion = linea[1]
        lider["logs"].append((accion, term_lider))
    elif(comando == "Spread" and lider != None):
        lista_nodos = linea[1]
        if(len(lista_nodos) != 0):
            for nodo in nodos.keys():
                nodo = nodos[nodo]
                if(nodo["activo"] == True):
                    if(nodo != lider and nodo["name"] in lista_nodos):
                        replicar(nodo, lider["logs"])
        consolidar(nodos, lider)
    elif(comando == "Stop"):
        name_nodo = linea[1]
        if(name_nodo in nodos.keys()):
            nodos[name_nodo]["activo"] = True
    elif(comando == "Start"):
        name_nodo = linea[1]
        if(name_nodo in nodos.keys()):
            nodos[name_nodo]["activo"] = False
            lider = None
            eleccion_lider(nodos, lider)
    elif(comando == "Log"):
        print("Log")
        # TODO: hacer esto

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
    # nodos = {}
    # lider = None
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
        procesar_comandos_raft(nodos, lider, comando, linea)

# exec_raft("casos_Raft/test_01.txt")