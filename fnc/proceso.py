"""Controlador del proceso: orden de las etapas, historial y reinicio.

La interfaz solo habla con ProcesoFNC; los algoritmos no conocen la interfaz.
"""

from collections.abc import Callable

from fnc.algoritmos.chomsky import reducir_producciones_largas, sustituir_terminales
from fnc.algoritmos.inalcanzables import eliminar_variables_inalcanzables
from fnc.algoritmos.inutiles import eliminar_variables_inutiles
from fnc.algoritmos.nulas import eliminar_producciones_nulas
from fnc.algoritmos.unitarias import eliminar_producciones_unitarias
from fnc.modelo.gramatica import Gramatica
from fnc.modelo.historial import Historial, Paso
from fnc.validacion.validador import validar_fnc, validar_gramatica

ETAPAS = ("nulas", "unitarias", "inutiles", "inalcanzables", "fnc")

NOMBRES_ETAPAS = {
    "nulas": "Eliminar producciones nulas",
    "unitarias": "Eliminar producciones unitarias",
    "inutiles": "Eliminar variables inútiles",
    "inalcanzables": "Eliminar variables inalcanzables",
    "fnc": "Convertir a Forma Normal de Chomsky",
}


class ErrorProceso(Exception):
    """Error cuyo mensaje ya está listo para mostrárselo al usuario."""


class ProcesoFNC:
    """Lleva la gramática desde su ingreso hasta la Forma Normal de Chomsky.

    Modo paso a paso: ejecutar_etapa() ejecuta una etapa a la vez en el orden de ETAPAS.
    Modo automático: ejecutar_proceso_completo() ejecuta todas las etapas pendientes.
    """

    def __init__(self) -> None:
        self._historial = Historial()
        self.reiniciar()

    # ----------------------------------------------------------------- ingreso

    def ingresar_gramatica(self, texto_variables: str, texto_terminales: str,
                           texto_inicial: str, texto_producciones: str) -> None:
        """RF01-RF05. Guarda el texto ingresado y reinicia cualquier proceso anterior."""
        self.reiniciar()
        self._texto_ingresado = (texto_variables, texto_terminales, texto_inicial, texto_producciones)

    def validar(self) -> list[str]:
        """RF06. Valida lo ingresado y devuelve la lista de errores ([] = válida).

        Si la gramática es válida se registra el paso de validación en el historial.
        """
        texto_ingresado = self._texto_ingresado
        self.reiniciar()
        self._texto_ingresado = texto_ingresado
        if texto_ingresado is None:
            return ["Error: primero debe ingresar una gramática."]

        resultado = validar_gramatica(*texto_ingresado)
        if not resultado.es_valida:
            return resultado.errores

        gramatica = resultado.gramatica
        self._gramatica_original = gramatica
        self._gramatica_actual = gramatica
        self._historial.registrar(Paso(
            nombre="Validación de la gramática",
            gramatica_inicial=gramatica.copiar(),
            gramatica_resultante=gramatica.copiar(),
            elementos_identificados={
                "Variables (no terminales)": gramatica.variables_en_orden(),
                "Terminales": list(gramatica.terminales),
                "Símbolo inicial": [gramatica.simbolo_inicial],
                "Número de producciones": [str(gramatica.cantidad_producciones())],
            },
            observaciones=["La gramática es válida."] + resultado.advertencias,
        ))
        return []

    # ----------------------------------------------------------------- consultas

    def gramatica_es_valida(self) -> bool:
        return self._gramatica_original is not None

    def siguiente_etapa(self) -> str | None:
        """Clave de la próxima etapa, o None si el proceso terminó o el lenguaje es vacío."""
        if not self.gramatica_es_valida() or self._lenguaje_vacio:
            return None
        if self._indice_etapa >= len(ETAPAS):
            return None
        return ETAPAS[self._indice_etapa]

    def proceso_terminado(self) -> bool:
        return self._indice_etapa >= len(ETAPAS)

    def lenguaje_vacio(self) -> bool:
        return self._lenguaje_vacio

    def gramatica_original(self) -> Gramatica | None:
        return self._gramatica_original

    def gramatica_actual(self) -> Gramatica | None:
        return self._gramatica_actual

    def gramatica_final(self) -> Gramatica | None:
        return self._gramatica_actual if self.proceso_terminado() else None

    def historial(self) -> Historial:
        return self._historial

    # ----------------------------------------------------------------- ejecución

    def ejecutar_etapa(self, etapa: str) -> list[Paso]:
        """Modo paso a paso: ejecuta la etapa indicada si es la que sigue."""
        self._verificar_que_se_puede_ejecutar(etapa)
        pasos = self._ejecutar_algoritmos(etapa)
        for paso in pasos:
            self._historial.registrar(paso)
        self._gramatica_actual = pasos[-1].gramatica_resultante
        self._indice_etapa += 1

        # Si el símbolo inicial dejó de generar cadenas el lenguaje es vacío y no se puede seguir.
        if etapa == "inutiles" and not self._gramatica_actual.producciones.get(self._gramatica_actual.simbolo_inicial):
            self._lenguaje_vacio = True
        return pasos

    def ejecutar_proceso_completo(self) -> list[Paso]:
        """Modo automático: valida si hace falta y ejecuta todas las etapas pendientes."""
        if not self.gramatica_es_valida():
            errores = self.validar()
            if errores:
                raise ErrorProceso("La gramática tiene errores:\n" + "\n".join(errores))
            pasos = [self._historial.pasos[-1]]
        else:
            pasos = []
        if self.proceso_terminado():
            raise ErrorProceso('El proceso ya terminó. Use "Nueva gramática" para empezar otra.')

        while self.siguiente_etapa() is not None:
            pasos += self.ejecutar_etapa(self.siguiente_etapa())
        return pasos

    def reiniciar(self) -> None:
        """RF20. Borra la gramática, el historial y el avance del proceso."""
        self._texto_ingresado: tuple[str, str, str, str] | None = None
        self._gramatica_original: Gramatica | None = None
        self._gramatica_actual: Gramatica | None = None
        self._indice_etapa = 0
        self._lenguaje_vacio = False
        self._historial.limpiar()

    # ----------------------------------------------------------------- internos

    def _verificar_que_se_puede_ejecutar(self, etapa: str) -> None:
        if etapa not in ETAPAS:
            raise ErrorProceso(f"La etapa '{etapa}' no existe.")
        if not self.gramatica_es_valida():
            raise ErrorProceso("Primero debe validar la gramática.")
        if self._lenguaje_vacio:
            raise ErrorProceso("El lenguaje de la gramática es vacío; no es posible continuar.")
        if self.proceso_terminado():
            raise ErrorProceso('El proceso ya terminó. Use "Nueva gramática" para empezar otra.')
        siguiente = ETAPAS[self._indice_etapa]
        if etapa != siguiente:
            raise ErrorProceso(f"Primero debe ejecutar: {NOMBRES_ETAPAS[siguiente]}.")

    def _ejecutar_algoritmos(self, etapa: str) -> list[Paso]:
        algoritmos: dict[str, Callable[[Gramatica], Paso]] = {
            "nulas": eliminar_producciones_nulas,
            "unitarias": eliminar_producciones_unitarias,
            "inutiles": eliminar_variables_inutiles,
            "inalcanzables": eliminar_variables_inalcanzables,
        }
        if etapa in algoritmos:
            return [algoritmos[etapa](self._gramatica_actual)]

        # La etapa FNC tiene dos transformaciones y termina con la validación automática (RNF12).
        paso_terminales = sustituir_terminales(self._gramatica_actual)
        paso_largas = reducir_producciones_largas(paso_terminales.gramatica_resultante)
        return [paso_terminales, paso_largas, self._paso_validacion_fnc(paso_largas.gramatica_resultante)]

    @staticmethod
    def _paso_validacion_fnc(gramatica: Gramatica) -> Paso:
        errores = validar_fnc(gramatica)
        if errores:
            elementos = {"Producciones que no cumplen la FNC": errores}
        else:
            elementos = {"Resultado": ["La gramática cumple la Forma Normal de Chomsky"]}
        return Paso(
            nombre="Validación de la Forma Normal de Chomsky",
            gramatica_inicial=gramatica.copiar(),
            gramatica_resultante=gramatica.copiar(),
            elementos_identificados=elementos,
        )
