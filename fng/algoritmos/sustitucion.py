"""Fase 1 de la conversión: sustituciones hacia adelante (RF08, RF09)."""

from fnc.modelo.gramatica import Gramatica
from fnc.modelo.historial import Paso
from fng.utilidades import aplicar_sustitucion, crear_paso


def sustituir_hacia_adelante(gramatica: Gramatica, orden: list[str], indice: int) -> Paso:
    """Deja cada producción de Ai = orden[indice] empezando con terminal o con Aj, j ≥ i.

    Para j = 1, …, i−1 (en orden creciente) reemplaza cada Ai -> Aj γ por las
    producciones de Aj. Como al procesar Aj sus producciones ya empiezan con terminal
    o con una variable posterior a Aj, recorrer j de menor a mayor basta para hacer
    todas las sustituciones sucesivas.
    """
    variable = orden[indice]
    resultado = gramatica.copiar()
    analizadas = [Gramatica.produccion_a_texto(variable, cuerpo) for cuerpo in resultado.cuerpos_de(variable)]
    sustituciones: list[str] = []

    for anterior in orden[:indice]:
        # Foto de los cuerpos al empezar cada j: los nuevos que empiecen con una variable
        # posterior se atienden en una vuelta siguiente de j.
        for cuerpo in resultado.cuerpos_de(variable):
            if cuerpo and cuerpo[0] == anterior:
                sustituciones.append(aplicar_sustitucion(resultado, variable, cuerpo))

    observaciones = [] if sustituciones else [
        f"{variable} no tiene producciones que empiecen con una variable anterior; no requiere sustituciones."
    ]
    return crear_paso(
        f"Fase 1 · A{indice + 1} = {variable}: sustituciones",
        gramatica,
        resultado,
        {"Producciones analizadas": analizadas, "Sustituciones realizadas": sustituciones},
        observaciones,
    )
