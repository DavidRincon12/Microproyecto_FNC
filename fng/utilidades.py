"""Operaciones comunes a todas las etapas de la conversión a Forma Normal de Greibach.

La sustitución de la primera variable de un cuerpo es la operación que se repite en
las fases 1, 2 y 3, y todos los pasos del historial se arman igual. Por eso viven aquí.
"""

from fnc.modelo.gramatica import Cuerpo, Gramatica, Produccion
from fnc.modelo.historial import Paso


def reemplazar_cabeza(cuerpo: Cuerpo, reemplazos: list[Cuerpo]) -> list[Cuerpo]:
    """Cambia el primer símbolo de `cuerpo` por cada cuerpo de `reemplazos`.

    Si A -> B γ y B -> δ1 | δ2, entonces A -> δ1 γ | δ2 γ.
    reemplazar_cabeza(("S", "A"), [("A", "B"), ("b",)]) -> [("A", "B", "A"), ("b", "A")]
    """
    if not cuerpo:
        raise ValueError("No se puede sustituir el primer símbolo de una producción ε.")
    resto = tuple(cuerpo[1:])
    return [tuple(reemplazo) + resto for reemplazo in reemplazos]


def empieza_con_variable(gramatica: Gramatica, cuerpo: Cuerpo) -> bool:
    """True si el cuerpo no es ε y su primer símbolo es una variable."""
    return bool(cuerpo) and gramatica.es_variable(cuerpo[0])


def texto_sustitucion(variable: str, cuerpo: Cuerpo, nuevos: list[Cuerpo]) -> str:
    """Texto de una sustitución para el historial: 'B -> S A  ⇒  B -> A B A | b A'."""
    alternativas = " | ".join(Gramatica.cuerpo_a_texto(nuevo) for nuevo in nuevos)
    return f"{Gramatica.produccion_a_texto(variable, cuerpo)}  ⇒  {variable} -> {alternativas}"


def aplicar_sustitucion(gramatica: Gramatica, variable: str, cuerpo: Cuerpo) -> str:
    """Sustituye la primera variable de `variable -> cuerpo` por todas sus producciones.

    MODIFICA `gramatica`, así que se usa sobre la copia de trabajo de cada algoritmo:
    quita la producción original y agrega las nuevas (sin duplicados, RNF07).
    Devuelve el texto de la sustitución para "Sustituciones realizadas".
    """
    cabeza = cuerpo[0]
    nuevos = reemplazar_cabeza(cuerpo, gramatica.cuerpos_de(cabeza))
    gramatica.eliminar_produccion(variable, cuerpo)
    for nuevo in nuevos:
        gramatica.agregar_produccion(variable, nuevo)
    return texto_sustitucion(variable, cuerpo, nuevos)


def calcular_cambios(antes: Gramatica, despues: Gramatica) -> tuple[list[Produccion], list[Produccion]]:
    """Cambio neto de un paso: (eliminadas, agregadas).

    eliminadas: producciones de `antes` que ya no están en `despues` (orden canónico de `antes`).
    agregadas: producciones de `despues` que no estaban en `antes` (orden canónico de `despues`).
    Una producción creada y eliminada dentro del mismo paso no aparece en ninguna de las dos.
    """
    producciones_antes = set(antes.lista_producciones())
    producciones_despues = set(despues.lista_producciones())
    eliminadas = [p for p in antes.lista_producciones() if p not in producciones_despues]
    agregadas = [p for p in despues.lista_producciones() if p not in producciones_antes]
    return eliminadas, agregadas


def crear_paso(nombre: str, antes: Gramatica, despues: Gramatica,
               elementos: dict[str, list[str]], observaciones: list[str] | None = None) -> Paso:
    """Arma un Paso del historial con el cambio neto entre `antes` y `despues`.

    Guarda copias de las dos gramáticas para que el historial no cambie si después
    se sigue modificando alguna de ellas (RNF09).
    """
    eliminadas, agregadas = calcular_cambios(antes, despues)
    return Paso(
        nombre=nombre,
        gramatica_inicial=antes.copiar(),
        gramatica_resultante=despues.copiar(),
        elementos_identificados=elementos,
        producciones_eliminadas=eliminadas,
        producciones_agregadas=agregadas,
        observaciones=list(observaciones or []),
    )
