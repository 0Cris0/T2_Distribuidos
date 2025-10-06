# Tarea 2 - Sistemas Distribuidos.

Integrantes:
 - Cristóbal Ignacio Albornoz Luengo.
 - Randall Fabrizio Biermann Olivari.
 - Fecha de Entrega: 06-10-2025

## Generalidades sobre el proceso de ejecución de tests

## 1. Ejecutar python3 main.py Paxos casos_Paxos/test_XX.txt
Al ejecutar los tests de Paxos, se tiene que todos devuelven el output esperado, por lo que cumplen con lo solicitado.

## 2. Ejecutar python3 main.py Raft casos_Raft/test_01.txt
>>>>>>>>>>>>>> COMPLETAR <<<<<<<<<<<<

## 3. Con respecto al uso de herramientas generativas de código
Se ha hecho uso de herramienta de generación de texto para usos muy específicos:
- Caso Paxos: Se utilizó ChatGPT para realizar depuración y testeo de errores. Sin embargo, todo el código
fue escrito por humanos, por lo que el uso que se le ha dado ha sido bien específico y concreto para poder
corregir errores, la interpretación de los mismos y aclaramiento de dudas, en complemento con la información
que se encuentra disponible en GitHub discussions. Sin embargo, ninguna de las salidas para el testing y debugeo entregadas
por el modelo de lenguaje se han utilizado de manera textual sin realizar modificaciones y adaptaciones.

- Caso Raft: Se utilizó mayormente para entender mejor el funcionamiento de raft (lógica de los terms y condiciones de 
aceptar y rechazar) y así poder plantear el código. Pero en cuanto a código, solo se utilizó para plantear una función 
sencilla que permitiera ordenar los logs de los nodos:
"acciones_consolidadas = sorted(acciones_consolidadas, key=lambda x: x[1])"
(Ver línea 157 y 133, raft.py)

## Capturas de pantalla del uso de modelos de lenguaje.
![Referencia 1](imgs/paxos1.png)
![Referencia 2](imgs/paxos2.png)
![Referencia 1](imgs/paxos3.png)
