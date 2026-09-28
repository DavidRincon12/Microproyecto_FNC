"""Funciones de apoyo compartidas por las pruebas."""

from fnc.modelo.gramatica import Gramatica
from fnc.validacion.validador import validar_gramatica


def gramatica_desde_texto(variables: str, terminales: str, inicial: str, producciones: str) -> Gramatica:
    """Construye una gramática validada a partir del mismo texto que escribiría el usuario."""
    resultado = validar_gramatica(variables, terminales, inicial, producciones)
    if not resultado.es_valida:
        raise AssertionError("La gramática de prueba no es válida: " + " ".join(resultado.errores))
    return resultado.gramatica


def gramatica_desde_lineas(inicial: str, lineas: str) -> Gramatica:
    """Construye una gramática a partir de líneas con símbolos separados por espacios.

    Las variables son los lados izquierdos; el resto de símbolos se toman como terminales.
    """
    producciones = []
    for linea in lineas.strip().splitlines():
        izquierda, derecha = linea.split("->")
        for alternativa in derecha.split("|"):
            simbolos = alternativa.split()
            producciones.append((izquierda.strip(), () if simbolos == ["ε"] else tuple(simbolos)))
    variables = list(dict.fromkeys(izquierda for izquierda, _ in producciones))
    terminales = list(dict.fromkeys(
        s for _, cuerpo in producciones for s in cuerpo if s not in variables
    ))
    gramatica = Gramatica(variables, terminales, inicial)
    for izquierda, cuerpo in producciones:
        gramatica.agregar_produccion(izquierda, cuerpo)
    return gramatica
