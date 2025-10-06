from __future__ import annotations  # Solo lo dejo por si lo necesitan. Lo pueden eliminar
from sys import argv

from paxos import funcion_paxos
from raft import funcion_raft

# Recuerda que no se permite importar otros módulos/librerías a excepción de los creados
# por ustedes o las ya incluidas en este main.py


def exec_paxos(test: str) -> None:
    funcion_paxos(test)


def exec_raft(test: str) -> None:
    funcion_raft(test)

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