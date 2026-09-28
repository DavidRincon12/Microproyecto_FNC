"""Identificación y eliminación de producciones unitarias (RF09, RF10)."""

from fnc.modelo.gramatica import Cuerpo, Gramatica, Produccion
from fnc.modelo.historial import Paso


def _es_unitaria(gramatica: Gramatica, cuerpo: Cuerpo) -> bool:
    return len(cuerpo) == 1 and gramatica.es_variable(cuerpo[0])


def encontrar_producciones_unitarias(gramatica: Gramatica) -> list[Produccion]:
    """Producciones de la forma A -> B, con B variable."""
    return [
        (variable, cuerpo)
        for variable, cuerpo in gramatica.lista_producciones()
        if _es_unitaria(gramatica, cuerpo)
    ]


def _cadena_unitaria(gramatica: Gramatica, variable: str) -> list[str]:
    """Variables alcanzables desde `variable` usando solo producciones unitarias (recorrido en anchura)."""
    cadena = [variable]
    indice = 0
    while indice < len(cadena):
        for cuerpo in gramatica.cuerpos_de(cadena[indice]):
            if _es_unitaria(gramatica, cuerpo) and cuerpo[0] not in cadena:
                cadena.append(cuerpo[0])
        indice += 1
    return cadena


def calcular_pares_unitarios(gramatica: Gramatica) -> list[tuple[str, str]]:
    """Pares (A, B) tales que A deriva B usando solo producciones unitarias, con A ≠ B."""
    pares = []
    for variable in gramatica.variables_en_orden():
        pares += [(variable, otra) for otra in _cadena_unitaria(gramatica, variable)[1:]]
    return pares


def eliminar_producciones_unitarias(gramatica: Gramatica) -> Paso:
    """Reemplaza cada A -> B por las producciones no unitarias de B (y de toda su cadena unitaria)."""
    unitarias = encontrar_producciones_unitarias(gramatica)
    pares = calcular_pares_unitarios(gramatica)
    resultado = gramatica.copiar()
    agregadas: list[Produccion] = []

    for variable in gramatica.variables_en_orden():
        nuevos_cuerpos: set[Cuerpo] = set()
        for otra in _cadena_unitaria(gramatica, variable):
            nuevos_cuerpos |= {c for c in gramatica.cuerpos_de(otra) if not _es_unitaria(gramatica, c)}
        for cuerpo in sorted(nuevos_cuerpos - gramatica.producciones[variable], key=lambda c: (len(c), c)):
            agregadas.append((variable, cuerpo))
        resultado.producciones[variable] = nuevos_cuerpos

    observaciones = [] if unitarias else ["La gramática no tiene producciones unitarias; no hay cambios."]
    return Paso(
        nombre="Eliminación de producciones unitarias",
        gramatica_inicial=gramatica.copiar(),
        gramatica_resultante=resultado,
        elementos_identificados={
            "Producciones unitarias": [Gramatica.produccion_a_texto(v, c) for v, c in unitarias],
            "Pares unitarios": [f"({a}, {b})" for a, b in pares],
        },
        producciones_eliminadas=unitarias,
        producciones_agregadas=agregadas,
        observaciones=observaciones,
    )
