"""Ordenamiento de las variables A1, A2, …, An (RF07).

El algoritmo de conversión necesita un orden fijo: en la fase 1 cada Ai solo se
sustituye con variables anteriores, de modo que al final cada Ai empieza con un
terminal o con una variable posterior.
"""

from fnc.modelo.gramatica import Gramatica
from fnc.modelo.historial import Paso
from fng.utilidades import crear_paso


def calcular_orden(gramatica: Gramatica, orden_usuario: list[str] | None = None) -> tuple[list[str], list[str]]:
    """Devuelve (orden, advertencias).

    Por defecto: el símbolo inicial primero y luego el orden de declaración. Si el
    usuario indica un orden, sus variables válidas van primero en ese orden; las que no
    escribió se agregan al final en el orden por defecto y las que no existen se ignoran.
    """
    orden_por_defecto = gramatica.variables_en_orden()
    if not orden_usuario:
        return orden_por_defecto, []

    orden: list[str] = []
    advertencias: list[str] = []
    for variable in orden_usuario:
        if variable not in orden_por_defecto:
            advertencias.append(f"Advertencia: la variable {variable} del orden no existe en la gramática; se ignora.")
        elif variable not in orden:
            orden.append(variable)
    orden += [variable for variable in orden_por_defecto if variable not in orden]
    return orden, advertencias


def ordenar_variables(gramatica: Gramatica, orden_usuario: list[str] | None = None) -> tuple[Paso, list[str]]:
    """Paso "Ordenamiento de variables" y el orden calculado.

    Si el símbolo inicial tiene la producción ε, se aparta: no interviene en la conversión
    (el inicial no aparece a la derecha) y se reincorpora en la limpieza final.
    """
    orden, observaciones = calcular_orden(gramatica, orden_usuario)
    resultado = gramatica.copiar()
    inicial = gramatica.simbolo_inicial
    if resultado.eliminar_produccion(inicial, ()):
        observaciones.append(f"Se aparta {inicial} -> ε; se reincorpora en la limpieza final.")

    paso = crear_paso(
        "Ordenamiento de variables",
        gramatica,
        resultado,
        {"Orden de las variables": [f"A{indice} = {variable}" for indice, variable in enumerate(orden, start=1)]},
        observaciones,
    )
    return paso, orden
