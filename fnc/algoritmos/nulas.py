"""Identificación y eliminación de producciones nulas (RF07, RF08)."""

from itertools import combinations

from fnc.modelo.gramatica import Cuerpo, Gramatica, Produccion
from fnc.modelo.historial import Paso


def calcular_variables_anulables(gramatica: Gramatica) -> list[str]:
    """Variables que pueden derivar ε, calculadas por punto fijo.

    Una variable es anulable si tiene A -> ε o una producción cuyos símbolos
    son todos anulables. Se repite hasta que una vuelta no agregue ninguna.
    """
    anulables: set[str] = set()
    hubo_cambios = True
    while hubo_cambios:
        hubo_cambios = False
        for variable in gramatica.variables_en_orden():
            if variable in anulables:
                continue
            if any(all(simbolo in anulables for simbolo in cuerpo) for cuerpo in gramatica.cuerpos_de(variable)):
                anulables.add(variable)
                hubo_cambios = True
    return [variable for variable in gramatica.variables_en_orden() if variable in anulables]


def _variantes_sin_anulables(cuerpo: Cuerpo, anulables: set[str]) -> list[Cuerpo]:
    """Todas las formas de quitar o conservar los símbolos anulables del cuerpo (2^k variantes)."""
    posiciones = [i for i, simbolo in enumerate(cuerpo) if simbolo in anulables]
    variantes = []
    for cantidad in range(len(posiciones) + 1):
        for quitadas in combinations(posiciones, cantidad):
            variantes.append(tuple(s for i, s in enumerate(cuerpo) if i not in quitadas))
    return variantes


def _nombre_nuevo_inicial(gramatica: Gramatica) -> str:
    nombre = gramatica.simbolo_inicial + "0"
    while gramatica.es_variable(nombre) or gramatica.es_terminal(nombre):
        nombre += "'"
    return nombre


def eliminar_producciones_nulas(gramatica: Gramatica) -> Paso:
    """Elimina las producciones A -> ε generando las producciones equivalentes.

    Si el símbolo inicial es anulable se crea un nuevo inicial S0 -> S | ε para que
    la gramática conserve la cadena vacía (tratamiento especial de ε, RNF07).
    """
    anulables = calcular_variables_anulables(gramatica)
    conjunto_anulables = set(anulables)
    resultado = gramatica.copiar()
    eliminadas: list[Produccion] = []
    agregadas: list[Produccion] = []
    observaciones: list[str] = []

    for variable in gramatica.variables_en_orden():
        nuevos_cuerpos: set[Cuerpo] = set()
        for cuerpo in gramatica.cuerpos_de(variable):
            if not cuerpo:
                eliminadas.append((variable, cuerpo))
                continue
            for variante in _variantes_sin_anulables(cuerpo, conjunto_anulables):
                # Se descartan ε y A -> A: la primera es la que se elimina y la segunda no aporta nada.
                if variante and variante != (variable,):
                    nuevos_cuerpos.add(variante)

        for cuerpo in sorted(nuevos_cuerpos - gramatica.producciones[variable], key=lambda c: (len(c), c)):
            agregadas.append((variable, cuerpo))
        resultado.producciones[variable] = nuevos_cuerpos

    inicial = gramatica.simbolo_inicial
    if not anulables:
        observaciones.append("La gramática no tiene producciones nulas; no hay cambios.")
    elif inicial in conjunto_anulables:
        nuevo_inicial = _nombre_nuevo_inicial(gramatica)
        resultado.definir_simbolo_inicial(nuevo_inicial)
        for cuerpo in ((inicial,), ()):
            resultado.agregar_produccion(nuevo_inicial, cuerpo)
            agregadas.append((nuevo_inicial, cuerpo))
        observaciones.append(
            f"{inicial} es anulable, por lo tanto ε ∈ L(G). Se crea el nuevo símbolo inicial "
            f"{nuevo_inicial} con {nuevo_inicial} -> {inicial} | ε para conservar la cadena vacía."
        )
    else:
        observaciones.append(f"{inicial} no es anulable: no se crea un nuevo símbolo inicial.")

    return Paso(
        nombre="Eliminación de producciones nulas",
        gramatica_inicial=gramatica.copiar(),
        gramatica_resultante=resultado,
        elementos_identificados={"Variables anulables": anulables},
        producciones_eliminadas=eliminadas,
        producciones_agregadas=agregadas,
        observaciones=observaciones,
    )
