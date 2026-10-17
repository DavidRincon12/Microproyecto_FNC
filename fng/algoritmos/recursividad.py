"""Detección y eliminación de la recursividad izquierda directa en FNG (RF10, RF11, RF12, RNF08)."""

from fnc.modelo.gramatica import Gramatica, Produccion
from fnc.modelo.historial import Paso
from fng.utilidades import crear_paso


def detectar_recursividad_izquierda(gramatica: Gramatica, variable: str) -> list[Produccion]:
    """Producciones de `variable` que empiezan con la propia `variable` (recursividad izquierda directa).

    Se devuelven en orden canónico (según cuerpos_de).
    """
    return [
        (variable, cuerpo)
        for cuerpo in gramatica.cuerpos_de(variable)
        if cuerpo and cuerpo[0] == variable
    ]


def nombre_variable_auxiliar(gramatica: Gramatica, variable: str) -> str:
    """Genera un nombre para la variable auxiliar de recursividad: A' (o A'' si A' ya existe)."""
    candidato = f"{variable}'"
    while gramatica.es_variable(candidato) or gramatica.es_terminal(candidato):
        candidato += "'"
    return candidato


def eliminar_recursividad_izquierda(gramatica: Gramatica, variable: str, posicion: int) -> Paso:
    """Elimina la recursividad izquierda directa de Ai introduciendo una variable auxiliar.

    Para cada producción recursiva Ai -> Ai γ y cada no recursiva Ai -> β:
      - se eliminan las Ai -> Ai γ;
      - se agregan Ai -> β B' (las Ai -> β se conservan);
      - se agregan B' -> γ y B' -> γ B'.
    """
    recursivas = detectar_recursividad_izquierda(gramatica, variable)
    resultado = gramatica.copiar()
    nombre_paso = f"Fase 1 · A{posicion} = {variable}: eliminación de recursividad izquierda"

    if not recursivas:
        elementos = {
            "Producciones con recursividad izquierda": [],
            "Producciones sin recursividad (β)": [
                Gramatica.produccion_a_texto(variable, c) for c in resultado.cuerpos_de(variable)
            ],
            "Variable auxiliar creada": [],
        }
        observaciones = [f"No hay recursividad izquierda directa en {variable}."]
        return crear_paso(nombre_paso, gramatica, resultado, elementos, observaciones)

    gammas = [cuerpo[1:] for _, cuerpo in recursivas]
    betas = [cuerpo for cuerpo in resultado.cuerpos_de(variable) if not cuerpo or cuerpo[0] != variable]

    if not betas:
        # Caso límite: todas las producciones son recursivas (la variable no genera cadenas)
        resultado.eliminar_variable(variable)
        elementos = {
            "Producciones con recursividad izquierda": [
                Gramatica.produccion_a_texto(variable, c) for _, c in recursivas
            ],
            "Producciones sin recursividad (β)": [],
            "Variable auxiliar creada": [],
        }
        observaciones = [f"{variable} no tiene producciones no recursivas: no genera cadenas."]
        return crear_paso(nombre_paso, gramatica, resultado, elementos, observaciones)

    auxiliar = nombre_variable_auxiliar(resultado, variable)
    resultado.agregar_variable(auxiliar)

    # Quitar las producciones recursivas
    for _, cuerpo in recursivas:
        resultado.eliminar_produccion(variable, cuerpo)

    # Agregar Ai -> β auxiliar
    for beta in betas:
        resultado.agregar_produccion(variable, beta + (auxiliar,))

    # Agregar auxiliar -> γ y auxiliar -> γ auxiliar
    for gamma in gammas:
        resultado.agregar_produccion(auxiliar, gamma)
        resultado.agregar_produccion(auxiliar, gamma + (auxiliar,))

    elementos = {
        "Producciones con recursividad izquierda": [
            Gramatica.produccion_a_texto(variable, c) for _, c in recursivas
        ],
        "Producciones sin recursividad (β)": [
            Gramatica.produccion_a_texto(variable, c) for c in betas
        ],
        "Variable auxiliar creada": [auxiliar],
    }
    observaciones = [
        f"Se elimina la recursividad izquierda de {variable} creando la variable auxiliar {auxiliar}."
    ]

    return crear_paso(nombre_paso, gramatica, resultado, elementos, observaciones)
