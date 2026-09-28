"""Validación inicial de la gramática ingresada y validación de la Forma Normal de Chomsky."""

from dataclasses import dataclass, field

from fnc.entrada.lector import PATRON_VARIABLE, SIMBOLOS_EPSILON, leer_producciones, leer_simbolos
from fnc.modelo.gramatica import Gramatica

RESERVADOS = set(SIMBOLOS_EPSILON) | {"->", "→", "|", ","}


@dataclass
class ResultadoValidacion:
    """Resultado de validar lo ingresado. La gramática solo se construye si no hay errores."""

    gramatica: Gramatica | None = None
    errores: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)

    @property
    def es_valida(self) -> bool:
        return not self.errores


def _agregar_sin_repetir(mensajes: list[str], mensaje: str) -> None:
    if mensaje not in mensajes:
        mensajes.append(mensaje)


def _validar_variables(variables: list[str], errores: list[str]) -> list[str]:
    if not variables:
        errores.append("Error: debe declarar al menos una variable.")
    validas = []
    for variable in variables:
        if PATRON_VARIABLE.fullmatch(variable):
            validas.append(variable)
        else:
            errores.append(
                f"Error: la variable '{variable}' no es válida; las variables deben iniciar "
                "con letra mayúscula (ej.: S, A, B1)."
            )
    return validas


def _validar_terminales(terminales: list[str], errores: list[str]) -> list[str]:
    if not terminales:
        errores.append("Error: debe declarar al menos un terminal.")
    validos = []
    for terminal in terminales:
        if terminal[0].isupper() or terminal in RESERVADOS:
            errores.append(
                f"Error: el terminal '{terminal}' no es válido; los terminales no pueden iniciar "
                "con mayúscula ni ser ε, λ o eps."
            )
        else:
            validos.append(terminal)
    return validos


def validar_gramatica(texto_variables: str, texto_terminales: str,
                      texto_inicial: str, texto_producciones: str) -> ResultadoValidacion:
    """Valida todos los componentes (sección 8 del enunciado) y reporta todos los errores a la vez."""
    errores: list[str] = []
    advertencias: list[str] = []

    variables = _validar_variables(leer_simbolos(texto_variables), errores)
    terminales = _validar_terminales(leer_simbolos(texto_terminales), errores)
    for simbolo in variables:
        if simbolo in terminales:
            errores.append(f"Error: el símbolo {simbolo} fue declarado como variable y como terminal.")

    simbolo_inicial = texto_inicial.strip()
    if not simbolo_inicial:
        errores.append("Error: debe indicar el símbolo inicial.")
    elif simbolo_inicial not in variables:
        errores.append(f"Error: el símbolo inicial {simbolo_inicial} no pertenece al conjunto de variables.")

    producciones, errores_estructura = leer_producciones(texto_producciones, variables + terminales)
    errores += errores_estructura
    if not producciones and not errores_estructura:
        errores.append("Error: debe registrar al menos una producción.")

    # Cada símbolo de cada producción debe estar declarado.
    for produccion in producciones:
        texto_produccion = f"{produccion.izquierda} -> {produccion.texto_derecho}"
        if produccion.izquierda not in variables:
            _agregar_sin_repetir(
                errores,
                f"Error: el lado izquierdo de la producción '{texto_produccion}' no es una variable declarada.",
            )
        for simbolo in produccion.cuerpo:
            if simbolo in variables or simbolo in terminales:
                continue
            if simbolo[0].isupper():
                mensaje = f"Error: la variable {simbolo} utilizada en la producción {texto_produccion} no fue declarada."
            else:
                mensaje = f"Error: el símbolo {simbolo} no fue declarado como terminal."
            _agregar_sin_repetir(errores, mensaje)

    if errores:
        return ResultadoValidacion(None, errores, advertencias)

    gramatica = Gramatica(variables, terminales, simbolo_inicial)
    for produccion in producciones:
        gramatica.agregar_produccion(produccion.izquierda, produccion.cuerpo)
    for variable in gramatica.variables:
        if not gramatica.producciones[variable]:
            advertencias.append(f"Advertencia: la variable {variable} no tiene producciones.")
    return ResultadoValidacion(gramatica, errores, advertencias)


def validar_fnc(gramatica: Gramatica) -> list[str]:
    """Comprueba que toda producción sea A -> B C, A -> a o S -> ε (RNF12).

    S -> ε solo se acepta si S es el símbolo inicial y no aparece a la derecha
    de ninguna producción. Devuelve [] si la gramática cumple la FNC.
    """
    inicial_a_la_derecha = any(
        gramatica.simbolo_inicial in cuerpo for _, cuerpo in gramatica.lista_producciones()
    )
    errores = []
    for variable, cuerpo in gramatica.lista_producciones():
        motivo = None
        if len(cuerpo) == 0:
            if variable != gramatica.simbolo_inicial or inicial_a_la_derecha:
                motivo = "solo el símbolo inicial puede producir ε y no debe aparecer a la derecha"
        elif len(cuerpo) == 1:
            if gramatica.es_variable(cuerpo[0]):
                motivo = "es una producción unitaria"
            elif not gramatica.es_terminal(cuerpo[0]):
                motivo = f"el símbolo {cuerpo[0]} no está declarado"
        elif len(cuerpo) == 2:
            if not all(gramatica.es_variable(simbolo) for simbolo in cuerpo):
                motivo = "un cuerpo de longitud 2 debe tener dos variables"
        else:
            motivo = "tiene más de dos símbolos"
        if motivo:
            errores.append(
                f"La producción {Gramatica.produccion_a_texto(variable, cuerpo)} no cumple la FNC: {motivo}."
            )
    return errores
