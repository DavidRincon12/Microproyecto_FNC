"""Registro paso a paso de las transformaciones aplicadas a la gramática."""

from dataclasses import dataclass, field

from fnc.modelo.gramatica import Gramatica, Produccion

SEPARADOR = "=" * 60
SIN_ELEMENTOS = "(ninguna)"


def _lineas_gramatica(gramatica: Gramatica) -> list[str]:
    lineas = gramatica.lineas_producciones()
    return ["  " + linea for linea in lineas] if lineas else ["  " + SIN_ELEMENTOS]


def _lineas_producciones(producciones: list[Produccion], marca: str) -> list[str]:
    if not producciones:
        return ["  " + SIN_ELEMENTOS]
    return [f"  {marca} {Gramatica.produccion_a_texto(variable, cuerpo)}" for variable, cuerpo in producciones]


@dataclass
class Paso:
    """Una etapa del proceso con todo lo que debe mostrarse (RF18)."""

    nombre: str
    gramatica_inicial: Gramatica
    gramatica_resultante: Gramatica
    elementos_identificados: dict[str, list[str]] = field(default_factory=dict)
    producciones_eliminadas: list[Produccion] = field(default_factory=list)
    producciones_agregadas: list[Produccion] = field(default_factory=list)
    observaciones: list[str] = field(default_factory=list)
    numero: int = 0

    def a_texto(self) -> str:
        titulo = f"Paso {self.numero}. {self.nombre}" if self.numero else self.nombre
        lineas = [SEPARADOR, titulo, SEPARADOR]

        lineas.append("Gramática inicial de la etapa:")
        lineas += _lineas_gramatica(self.gramatica_inicial)

        lineas.append("Elementos identificados:")
        if self.elementos_identificados:
            for descripcion, elementos in self.elementos_identificados.items():
                valor = ", ".join(elementos) if elementos else SIN_ELEMENTOS
                lineas.append(f"  {descripcion}: {valor}")
        else:
            lineas.append("  " + SIN_ELEMENTOS)

        lineas.append("Producciones eliminadas:")
        lineas += _lineas_producciones(self.producciones_eliminadas, "-")

        lineas.append("Producciones agregadas:")
        lineas += _lineas_producciones(self.producciones_agregadas, "+")

        lineas.append("Observaciones:")
        lineas += ["  " + observacion for observacion in self.observaciones] or ["  " + SIN_ELEMENTOS]

        lineas.append("Gramática resultante:")
        lineas += _lineas_gramatica(self.gramatica_resultante)
        return "\n".join(lineas)


class Historial:
    """Historial completo de pasos ejecutados (sección 9 del enunciado, RNF10)."""

    def __init__(self) -> None:
        self.pasos: list[Paso] = []

    def registrar(self, paso: Paso) -> None:
        """Agrega el paso al final y le asigna su número consecutivo."""
        paso.numero = len(self.pasos) + 1
        self.pasos.append(paso)

    def limpiar(self) -> None:
        self.pasos.clear()

    def esta_vacio(self) -> bool:
        return not self.pasos

    def a_texto(self) -> str:
        if self.esta_vacio():
            return "Aún no se ha ejecutado ningún paso."
        return "\n\n".join(paso.a_texto() for paso in self.pasos)
