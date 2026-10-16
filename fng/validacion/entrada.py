"""Validación de la gramática de entrada del Microproyecto 2 (sección 7 del enunciado).

Reutiliza la validación del Microproyecto 1 con la misma política: solo bloquean los
errores de escritura y los símbolos no declarados se descartan con advertencia. Además,
la conversión a Forma Normal de Greibach exige que la gramática esté en FNC, así que
cada producción fuera de la FNC es un error que bloquea.
"""

from dataclasses import dataclass, field

from fnc.modelo.gramatica import Gramatica, Produccion
from fnc.validacion.validador import validar_fnc, validar_gramatica

SUGERENCIA_FNC = 'Sugerencia: use "Convertir primero a FNC" para transformarla con el Microproyecto 1.'


@dataclass
class ResultadoEntrada:
    """Resultado de validar lo ingresado. `gramatica` solo existe si se puede convertir."""

    gramatica: Gramatica | None = None
    errores: list[str] = field(default_factory=list)
    errores_fnc: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)
    gramatica_ingresada: Gramatica | None = None
    producciones_descartadas: list[Produccion] = field(default_factory=list)

    @property
    def es_valida(self) -> bool:
        return not self.errores


def validar_entrada(texto_variables: str, texto_terminales: str,
                    texto_inicial: str, texto_producciones: str) -> ResultadoEntrada:
    """Valida la escritura, descarta símbolos no declarados y exige la Forma Normal de Chomsky."""
    resultado = validar_gramatica(texto_variables, texto_terminales, texto_inicial, texto_producciones)
    if not resultado.es_valida:
        return ResultadoEntrada(errores=resultado.errores, advertencias=resultado.advertencias)

    errores_fnc = validar_fnc(resultado.gramatica)
    if errores_fnc:
        return ResultadoEntrada(
            errores=errores_fnc + [SUGERENCIA_FNC],
            errores_fnc=errores_fnc,
            advertencias=resultado.advertencias,
            gramatica_ingresada=resultado.gramatica_ingresada,
            producciones_descartadas=resultado.producciones_descartadas,
        )

    return ResultadoEntrada(
        gramatica=resultado.gramatica,
        advertencias=resultado.advertencias,
        gramatica_ingresada=resultado.gramatica_ingresada,
        producciones_descartadas=resultado.producciones_descartadas,
    )
