"""Validación inicial de la gramática ingresada y validación de la Forma Normal de Chomsky."""

from dataclasses import dataclass, field

from fnc.entrada.lector import PATRON_VARIABLE, SIMBOLOS_EPSILON, leer_producciones, leer_simbolos
from fnc.modelo.gramatica import Gramatica, Produccion

RESERVADOS = set(SIMBOLOS_EPSILON) | {"->", "→", "|", ","}


@dataclass
class ResultadoValidacion:
    """Resultado de validar lo ingresado.

    Solo los errores de escritura impiden continuar. Los símbolos no declarados se
    reportan como advertencias y las producciones que los usan se descartan.
    """

    gramatica: Gramatica | None = None
    errores: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)
    gramatica_ingresada: Gramatica | None = None
    producciones_descartadas: list[Produccion] = field(default_factory=list)

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


def _validar_terminales(terminales: list[str], errores: list[str], advertencias: list[str]) -> list[str]:
    if not terminales:
        advertencias.append("Advertencia: no se declaró ningún terminal.")
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


def _primer_simbolo_no_declarado(cuerpo: tuple[str, ...], declarados: set[str]) -> str | None:
    return next((simbolo for simbolo in cuerpo if simbolo not in declarados), None)


def _construir_gramatica_ingresada(variables: list[str], terminales: list[str], simbolo_inicial: str,
                                   producciones: list) -> Gramatica:
    """Gramática tal como la escribió el usuario, incluidos los símbolos no declarados."""
    variables_ingresadas = list(variables)
    terminales_ingresados = list(terminales)
    for produccion in producciones:
        for simbolo in (produccion.izquierda, *produccion.cuerpo):
            if simbolo in variables_ingresadas or simbolo in terminales_ingresados:
                continue
            if simbolo[0].isupper():
                variables_ingresadas.append(simbolo)
            else:
                terminales_ingresados.append(simbolo)
    gramatica = Gramatica(variables_ingresadas, terminales_ingresados, simbolo_inicial)
    for produccion in producciones:
        gramatica.agregar_produccion(produccion.izquierda, produccion.cuerpo)
    return gramatica


def validar_gramatica(texto_variables: str, texto_terminales: str,
                      texto_inicial: str, texto_producciones: str) -> ResultadoValidacion:
    """Valida la gramática ingresada (sección 8 del enunciado).

    Bloquean el proceso solo los errores de escritura: formato de los símbolos, falta de
    flecha, alternativas vacías, ε mezclada, lado izquierdo mal escrito o componentes
    vacíos. Un símbolo no declarado se toma como inexistente: las producciones que lo
    usan no pueden generar ninguna cadena, así que se descartan como inútiles y se
    informa con una advertencia.
    """
    errores: list[str] = []
    advertencias: list[str] = []

    variables = _validar_variables(leer_simbolos(texto_variables), errores)
    terminales = _validar_terminales(leer_simbolos(texto_terminales), errores, advertencias)

    simbolo_inicial = texto_inicial.strip()
    if not simbolo_inicial:
        errores.append("Error: debe indicar el símbolo inicial.")
    elif not PATRON_VARIABLE.fullmatch(simbolo_inicial):
        errores.append(f"Error: el símbolo inicial '{simbolo_inicial}' no es una variable válida.")
    elif simbolo_inicial not in variables:
        advertencias.append(
            f"Advertencia: el símbolo inicial {simbolo_inicial} no pertenece al conjunto de variables; "
            "como no está declarado no genera ninguna cadena y el lenguaje resultará vacío."
        )

    producciones, errores_estructura = leer_producciones(texto_producciones, variables + terminales)
    errores += errores_estructura
    if not producciones and not errores_estructura:
        errores.append("Error: debe registrar al menos una producción.")
    for produccion in producciones:
        if not PATRON_VARIABLE.fullmatch(produccion.izquierda):
            _agregar_sin_repetir(
                errores,
                f"Error: el lado izquierdo de la producción '{produccion.izquierda} -> "
                f"{produccion.texto_derecho}' no es una variable válida.",
            )

    if errores:
        return ResultadoValidacion(None, errores, advertencias)

    # Las producciones con símbolos no declarados se descartan: no pueden generar cadenas del lenguaje.
    declarados = set(variables) | set(terminales)
    validas, descartadas = [], []
    for produccion in producciones:
        texto_produccion = f"{produccion.izquierda} -> {produccion.texto_derecho}"
        if produccion.izquierda not in variables:
            descartadas.append(produccion)
            _agregar_sin_repetir(
                advertencias,
                f"Advertencia: la variable {produccion.izquierda} no fue declarada; "
                "se descartan sus producciones.",
            )
            continue
        simbolo = _primer_simbolo_no_declarado(produccion.cuerpo, declarados)
        if simbolo is None:
            validas.append(produccion)
            continue
        descartadas.append(produccion)
        if simbolo[0].isupper():
            mensaje = (f"Advertencia: la producción {texto_produccion} usa la variable {simbolo}, "
                       "que no fue declarada; se descarta por ser inútil.")
        else:
            mensaje = (f"Advertencia: la producción {texto_produccion} usa el símbolo {simbolo}, "
                       "que no fue declarado como terminal; se descarta.")
        _agregar_sin_repetir(advertencias, mensaje)

    gramatica = Gramatica(variables, terminales, simbolo_inicial)
    for produccion in validas:
        gramatica.agregar_produccion(produccion.izquierda, produccion.cuerpo)
    for variable in gramatica.variables:
        if not gramatica.producciones[variable]:
            advertencias.append(f"Advertencia: la variable {variable} no tiene producciones.")

    return ResultadoValidacion(
        gramatica=gramatica,
        errores=[],
        advertencias=advertencias,
        gramatica_ingresada=_construir_gramatica_ingresada(variables, terminales, simbolo_inicial, producciones),
        producciones_descartadas=[(p.izquierda, p.cuerpo) for p in descartadas],
    )


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
