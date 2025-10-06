from __future__ import annotations

import func_auxiliares as f_aux


def funcion_paxos(test: str) -> None:
    # El primer paso es leer el archivo de test
    with open(test, "r", encoding="utf-8") as f:
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
        "alive": True
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
                    f_aux.procesar_accion(val)
                    # reseteo estado nodos aceptantes activos
                    for id_acept in nodos_aceptantes.keys():
                        if nodos_aceptantes[id_acept]["alive"]:
                            nodos_aceptantes[id_acept]["promised_n"] = None
                            nodos_aceptantes[id_acept]["accepted_n"] = None
                            nodos_aceptantes[id_acept]["accepted_value"] = None
                    break

        elif comando == "Log":
            variable_log = separados[1].strip()
            valor_log = f_aux.bbdd.get(variable_log, "Variable no existe")
            f_aux.logs_bbdd.append((variable_log,valor_log))

    # Paso 4: Se escriben los logs
    f_aux.escribir_logs("Paxos", test, f_aux.logs_bbdd)
