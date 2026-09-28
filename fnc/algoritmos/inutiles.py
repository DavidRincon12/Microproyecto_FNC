"""Identificación y eliminación de variables inútiles (no generadoras) (RF11, RF12)."""

from fnc.modelo.gramatica import Gramatica, Produccion
from fnc.modelo.historial import Paso


def calcular_variables_generadoras(gramatica: Gramatica) -> list[str]:
    """Variables que pueden derivar al menos una cadena de terminales (RF11).

    Se calculan por punto fijo: una variable es generadora si tiene al menos una
    producción A -> α donde cada símbolo de α es un terminal o una variable ya
    marcada como generadora (las producciones A -> ε también cuentan, pues ε es
    una cadena terminal vacía). Se repite hasta que no se agreguen nuevas variables.
    Se devuelven en el orden canónico de variables de la gramática.
    """
    generadoras: set[str] = set()
    terminales_set = set(gramatica.terminales)

    hubo_cambios = True
    while hubo_cambios:
        hubo_cambios = False
        for variable in gramatica.variables_en_orden():
            if variable in generadoras:
                continue
            for cuerpo in gramatica.cuerpos_de(variable):
                # Un cuerpo genera terminales si está vacío (ε) o todos sus símbolos
                # son terminales o variables ya identificadas como generadoras.
                if all(simbolo in terminales_set or simbolo in generadoras for simbolo in cuerpo):
                    generadoras.add(variable)
                    hubo_cambios = True
                    break

    return [var for var in gramatica.variables_en_orden() if var in generadoras]


def eliminar_variables_inutiles(gramatica: Gramatica) -> Paso:
    """Elimina las variables no generadoras y todas las producciones asociadas (RF12).

    Si el símbolo inicial no es generador, L(G) es vacío y se registra la
    observación correspondiente para detener el proceso.
    """
    generadoras = calcular_variables_generadoras(gramatica)
    conjunto_generadoras = set(generadoras)
    variables_orden = gramatica.variables_en_orden()
    no_generadoras = [var for var in variables_orden if var not in conjunto_generadoras]

    resultado = gramatica.copiar()
    observaciones: list[str] = []

    # Eliminamos las variables no generadoras de la copia
    for variable in no_generadoras:
        resultado.eliminar_variable(variable)

    # Las producciones eliminadas son aquellas de la gramática inicial que ya no están
    eliminadas: list[Produccion] = [
        (izq, cuerpo)
        for izq, cuerpo in gramatica.lista_producciones()
        if izq not in resultado.producciones or cuerpo not in resultado.producciones[izq]
    ]

    inicial = gramatica.simbolo_inicial
    if inicial not in conjunto_generadoras:
        observaciones.append(
            f"El símbolo inicial {inicial} no genera ninguna cadena de terminales: "
            "el lenguaje es vacío. El proceso no puede continuar."
        )
    elif not no_generadoras:
        observaciones.append("Todas las variables son generadoras; no hay variables inútiles.")
    else:
        observaciones.append(
            f"Se eliminaron {len(no_generadoras)} variable(s) no generadora(s) y sus producciones: "
            f"{', '.join(no_generadoras)}."
        )

    return Paso(
        nombre="Eliminación de variables inútiles",
        gramatica_inicial=gramatica.copiar(),
        gramatica_resultante=resultado,
        elementos_identificados={
            "Variables generadoras": generadoras,
            "Variables no generadoras (inútiles)": no_generadoras,
        },
        producciones_eliminadas=eliminadas,
        producciones_agregadas=[],
        observaciones=observaciones,
    )
