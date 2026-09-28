"""Identificación y eliminación de variables inalcanzables (RF13, RF14)."""

from fnc.modelo.gramatica import Gramatica, Produccion
from fnc.modelo.historial import Paso


def calcular_variables_alcanzables(gramatica: Gramatica) -> list[str]:
    """Variables alcanzables desde el símbolo inicial mediante recorrido en anchura (RF13).

    Comienza en el símbolo inicial y visita todas las variables que aparecen en
    los cuerpos de las producciones alcanzadas. Se reportan en el orden en que
    son descubiertas.
    """
    inicial = gramatica.simbolo_inicial
    if not gramatica.es_variable(inicial):
        return []

    cola = [inicial]
    indice = 0
    while indice < len(cola):
        variable_actual = cola[indice]
        for cuerpo in gramatica.cuerpos_de(variable_actual):
            for simbolo in cuerpo:
                if gramatica.es_variable(simbolo) and simbolo not in cola:
                    cola.append(simbolo)
        indice += 1

    return cola


def eliminar_variables_inalcanzables(gramatica: Gramatica) -> Paso:
    """Elimina variables inalcanzables desde el símbolo inicial y sus producciones (RF14).

    También depura los símbolos terminales que ya no son utilizados en ninguna
    producción de la gramática resultante.
    """
    alcanzables = calcular_variables_alcanzables(gramatica)
    conjunto_alcanzables = set(alcanzables)
    inalcanzables = [var for var in gramatica.variables_en_orden() if var not in conjunto_alcanzables]

    resultado = gramatica.copiar()
    observaciones: list[str] = []

    # Eliminar las variables inalcanzables
    for variable in inalcanzables:
        resultado.eliminar_variable(variable)

    # Identificar producciones eliminadas
    eliminadas: list[Produccion] = [
        (izq, cuerpo)
        for izq, cuerpo in gramatica.lista_producciones()
        if izq not in resultado.producciones or cuerpo not in resultado.producciones[izq]
    ]

    # Identificar terminales que ya no se usan
    terminales_usados = {
        simbolo
        for _, cuerpo in resultado.lista_producciones()
        for simbolo in cuerpo
        if resultado.es_terminal(simbolo)
    }
    terminales_sin_uso = [
        t for t in gramatica.terminales if t not in terminales_usados
    ]

    # Eliminar de la gramática los terminales que dejaron de usarse
    for t in terminales_sin_uso:
        resultado.eliminar_terminal(t)

    if not inalcanzables:
        observaciones.append("Todas las variables son alcanzables desde el símbolo inicial.")
    else:
        observaciones.append(
            f"Se eliminaron {len(inalcanzables)} variable(s) inalcanzable(s): {', '.join(inalcanzables)}."
        )

    if terminales_sin_uso:
        observaciones.append(
            f"Se eliminaron terminales que dejaron de usarse: {', '.join(terminales_sin_uso)}."
        )

    return Paso(
        nombre="Eliminación de variables inalcanzables",
        gramatica_inicial=gramatica.copiar(),
        gramatica_resultante=resultado,
        elementos_identificados={
            "Variables alcanzables": alcanzables,
            "Variables inalcanzables": inalcanzables,
            "Terminales que dejan de usarse": terminales_sin_uso,
        },
        producciones_eliminadas=eliminadas,
        producciones_agregadas=[],
        observaciones=observaciones,
    )
