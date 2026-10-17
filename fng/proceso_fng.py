"""Controlador del Microproyecto 2: conversión paso a paso de FNC a Forma Normal de Greibach.

La interfaz solo habla con ProcesoFNG. Los pasos se calculan de a uno con un generador:
en el modo paso a paso cada "Siguiente paso" calcula solo el que sigue, y el modo
automático repite eso hasta terminar.
"""

from collections.abc import Iterator

from fnc.algoritmos.inalcanzables import eliminar_variables_inalcanzables
from fnc.algoritmos.inutiles import eliminar_variables_inutiles
from fnc.entrada.lector import leer_simbolos
from fnc.modelo.gramatica import Gramatica
from fnc.modelo.historial import Historial, Paso
from fnc.proceso import ErrorProceso, ProcesoFNC
from fng.algoritmos.orden import ordenar_variables
from fng.algoritmos.recursividad import detectar_recursividad_izquierda, eliminar_recursividad_izquierda
from fng.algoritmos.sustitucion import sustituir_hacia_adelante
from fng.algoritmos.terminales import (convertir_variables_auxiliares, sustitucion_regresiva,
                                       verificar_variables_tras_terminal)
from fng.utilidades import crear_paso
from fng.validacion.entrada import validar_entrada
from fng.validacion.greibach import validar_fng


class ErrorProcesoFNG(Exception):
    """Error cuyo mensaje ya está listo para mostrárselo al usuario."""


class ProcesoFNG:
    """Lleva una gramática en FNC hasta la Forma Normal de Greibach registrando cada paso."""

    def __init__(self) -> None:
        self._historial = Historial()
        self.reiniciar()

    # ----------------------------------------------------------------- ingreso

    def ingresar_gramatica(self, texto_variables: str, texto_terminales: str, texto_inicial: str,
                           texto_producciones: str, texto_orden: str = "") -> None:
        """Guarda lo ingresado (RF01-RF05) y reinicia cualquier conversión anterior."""
        self.reiniciar()
        self._texto_ingresado = (texto_variables, texto_terminales, texto_inicial, texto_producciones)
        self._orden_usuario = leer_simbolos(texto_orden)

    def validar(self) -> list[str]:
        """RF06. Devuelve los errores que impiden convertir ([] = se puede convertir).

        Si la gramática es válida registra los pasos "Validación de la gramática" y
        "Validación de la Forma Normal de Chomsky" y deja lista la conversión.
        """
        texto_ingresado, orden_usuario = self._texto_ingresado, self._orden_usuario
        self.reiniciar()
        self._texto_ingresado, self._orden_usuario = texto_ingresado, orden_usuario
        if texto_ingresado is None:
            return ["Error: primero debe ingresar una gramática."]

        resultado = validar_entrada(*texto_ingresado)
        self._errores_fnc = resultado.errores_fnc
        self._advertencias = list(resultado.advertencias)
        if not resultado.es_valida:
            return resultado.errores

        gramatica = resultado.gramatica
        self._gramatica_original = gramatica
        self._gramatica_actual = gramatica
        conclusion = ("La gramática se puede procesar; se descartaron las producciones con símbolos no declarados."
                      if resultado.producciones_descartadas else "La gramática es válida.")
        paso_validacion = crear_paso(
            "Validación de la gramática",
            resultado.gramatica_ingresada,
            gramatica,
            {
                "Variables (no terminales)": gramatica.variables_en_orden(),
                "Terminales": list(gramatica.terminales),
                "Símbolo inicial": [gramatica.simbolo_inicial],
                "Número de producciones": [str(gramatica.cantidad_producciones())],
            },
            [conclusion] + resultado.advertencias,
        )
        self._historial.registrar(paso_validacion)
        self._historial.registrar(crear_paso(
            "Validación de la Forma Normal de Chomsky", gramatica, gramatica,
            {"Resultado": ["La gramática está en Forma Normal de Chomsky"]},
        ))
        self._pasos_pendientes = self._generar_pasos(gramatica)
        return []

    # ----------------------------------------------------------------- consultas

    def gramatica_es_valida(self) -> bool:
        return self._gramatica_original is not None

    def errores_son_de_fnc(self) -> bool:
        """True si la gramática está bien escrita y lo único que falla es la FNC."""
        return bool(self._errores_fnc)

    def advertencias(self) -> list[str]:
        """Advertencias de la última validación (símbolos no declarados que se descartaron).

        Se conservan aunque la gramática no esté en FNC, para avisarlas antes de convertirla.
        """
        return list(self._advertencias)

    def hay_siguiente_paso(self) -> bool:
        return self.gramatica_es_valida() and not self._terminado

    def proceso_terminado(self) -> bool:
        return self._terminado

    def lenguaje_vacio(self) -> bool:
        return self._lenguaje_vacio

    def orden_variables(self) -> list[str]:
        return list(self._orden)

    def gramatica_original(self) -> Gramatica | None:
        return self._gramatica_original

    def gramatica_actual(self) -> Gramatica | None:
        return self._gramatica_actual

    def gramatica_final(self) -> Gramatica | None:
        return self._gramatica_final

    def historial(self) -> Historial:
        return self._historial

    # ----------------------------------------------------------------- ejecución

    def siguiente_paso(self) -> Paso:
        """Modo paso a paso (RF20): calcula, registra y devuelve solo el paso siguiente."""
        if not self.gramatica_es_valida():
            raise ErrorProcesoFNG("Primero debe validar la gramática.")
        if self._terminado:
            raise ErrorProcesoFNG('La conversión ya terminó. Use "Nueva gramática" para empezar otra.')
        paso = next(self._pasos_pendientes)
        self._historial.registrar(paso)
        self._gramatica_actual = paso.gramatica_resultante
        return paso

    def ejecutar_todo(self) -> list[Paso]:
        """Modo automático (RF19): valida si hace falta y ejecuta todos los pasos que faltan."""
        pasos: list[Paso] = []
        if not self.gramatica_es_valida():
            errores = self.validar()
            if errores:
                raise ErrorProcesoFNG("La gramática tiene errores:\n" + "\n".join(errores))
            pasos += self._historial.pasos
        if self._terminado:
            raise ErrorProcesoFNG('La conversión ya terminó. Use "Nueva gramática" para empezar otra.')
        while self.hay_siguiente_paso():
            pasos.append(self.siguiente_paso())
        return pasos

    def reiniciar(self) -> None:
        """RF21. Borra la gramática, el historial y el avance de la conversión."""
        self._texto_ingresado: tuple[str, str, str, str] | None = None
        self._orden_usuario: list[str] = []
        self._errores_fnc: list[str] = []
        self._advertencias: list[str] = []
        self._gramatica_original: Gramatica | None = None
        self._gramatica_actual: Gramatica | None = None
        self._gramatica_final: Gramatica | None = None
        self._orden: list[str] = []
        self._pasos_pendientes: Iterator[Paso] | None = None
        self._terminado = False
        self._lenguaje_vacio = False
        self._historial.limpiar()

    def convertir_entrada_con_microproyecto1(self) -> dict[str, str]:
        """Convierte lo ingresado a FNC con el proceso del Microproyecto 1.

        Deja ingresada la gramática resultante (conservando el orden escrito) y devuelve
        sus textos, incluido el orden, para mostrarlos en el formulario.
        """
        if self._texto_ingresado is None:
            raise ErrorProcesoFNG("Primero debe ingresar una gramática.")
        orden_usuario = self._orden_usuario
        proceso_fnc = ProcesoFNC()
        proceso_fnc.ingresar_gramatica(*self._texto_ingresado)
        try:
            proceso_fnc.ejecutar_proceso_completo()
        except ErrorProceso as error:
            raise ErrorProcesoFNG(f"No se pudo convertir a FNC con el Microproyecto 1.\n{error}") from error
        gramatica = proceso_fnc.gramatica_final()
        if gramatica is None:
            raise ErrorProcesoFNG("La gramática genera el lenguaje vacío: no hay gramática en FNC que convertir.")

        textos = {
            "variables": ", ".join(gramatica.variables_en_orden()),
            "terminales": ", ".join(gramatica.terminales),
            "inicial": gramatica.simbolo_inicial,
            "producciones": "\n".join(gramatica.lineas_producciones()),
            "orden": ", ".join(orden_usuario),
        }
        self.ingresar_gramatica(textos["variables"], textos["terminales"], textos["inicial"],
                                textos["producciones"], textos["orden"])
        return textos

    # ----------------------------------------------------------------- internos

    def _generar_pasos(self, gramatica: Gramatica) -> Iterator[Paso]:
        """Produce los pasos en el orden de la sección 5.5 de la guía, uno por vez."""
        # Depuración previa: el algoritmo supone una gramática sin variables inútiles.
        paso = eliminar_variables_inutiles(gramatica)
        paso.nombre = "Depuración previa: eliminación de variables inútiles"
        gramatica = paso.gramatica_resultante
        if not gramatica.producciones.get(gramatica.simbolo_inicial):
            self._lenguaje_vacio = True
            self._terminado = True
            yield paso
            return
        yield paso

        paso = eliminar_variables_inalcanzables(gramatica)
        paso.nombre = "Depuración previa: eliminación de variables inalcanzables"
        gramatica = paso.gramatica_resultante
        yield paso

        epsilon_apartada = () in gramatica.producciones.get(gramatica.simbolo_inicial, set())
        paso, self._orden = ordenar_variables(gramatica, self._orden_usuario)
        gramatica = paso.gramatica_resultante
        yield paso

        # Fase 1: sustituciones hacia adelante y eliminación de recursividad izquierda.
        for indice, variable in enumerate(self._orden):
            paso = sustituir_hacia_adelante(gramatica, self._orden, indice)
            gramatica = paso.gramatica_resultante
            hay_recursividad = bool(detectar_recursividad_izquierda(gramatica, variable))
            if not hay_recursividad:
                paso.observaciones.append(f"No hay recursividad izquierda directa en {variable}.")
            yield paso
            if hay_recursividad:
                paso = eliminar_recursividad_izquierda(gramatica, variable, indice + 1)
                gramatica = paso.gramatica_resultante
                yield paso

        # Fases 2 y 3: todas las producciones pasan a empezar con un terminal.
        paso = sustitucion_regresiva(gramatica, self._orden)
        gramatica = paso.gramatica_resultante
        yield paso

        auxiliares = [variable for variable in gramatica.variables if variable not in self._orden]
        paso = convertir_variables_auxiliares(gramatica, auxiliares)
        gramatica = paso.gramatica_resultante
        yield paso

        paso = verificar_variables_tras_terminal(gramatica)
        gramatica = paso.gramatica_resultante
        yield paso

        paso = self._limpieza_final(gramatica, epsilon_apartada)
        gramatica = paso.gramatica_resultante
        yield paso

        # RNF12: la gramática final se valida automáticamente.
        errores = validar_fng(gramatica)
        elementos = ({"Producciones que no cumplen la FNG": errores} if errores
                     else {"Resultado": ["La gramática cumple la Forma Normal de Greibach"]})
        self._gramatica_final = gramatica
        self._terminado = True
        yield crear_paso("Validación de la Forma Normal de Greibach", gramatica, gramatica, elementos)

    @staticmethod
    def _limpieza_final(gramatica: Gramatica, epsilon_apartada: bool) -> Paso:
        """Reincorpora la ε apartada y elimina las variables que quedaron inalcanzables."""
        trabajo = gramatica.copiar()
        observaciones = []
        if epsilon_apartada:
            trabajo.agregar_produccion(trabajo.simbolo_inicial, ())
            observaciones.append("Se reincorpora la producción ε del símbolo inicial.")
        paso_inalcanzables = eliminar_variables_inalcanzables(trabajo)
        return crear_paso(
            "Limpieza final",
            gramatica,
            paso_inalcanzables.gramatica_resultante,
            paso_inalcanzables.elementos_identificados,
            observaciones + paso_inalcanzables.observaciones,
        )
