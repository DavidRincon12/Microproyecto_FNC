"""Comparación de lenguajes para las pruebas del Microproyecto 2 (RNF06).

Dos gramáticas son equivalentes si generan el mismo lenguaje. No se puede comprobar
para todas las cadenas, pero sí para todas las de longitud ≤ n: se calcula el conjunto
de cadenas que genera la gramática de entrada (FNC) y el de la gramática final (FNG)
y se comparan.
"""

from fnc.modelo.gramatica import Gramatica

Cadena = tuple[str, ...]


def cadenas_fnc(gramatica: Gramatica, longitud_maxima: int) -> set[Cadena]:
    """Cadenas de longitud ≤ n que genera una gramática en FNC (programación dinámica de CYK).

    generadas[A][k] son las cadenas de longitud k que se derivan de A:
      k = 1: los terminales a con A -> a.
      k > 1: para cada A -> B C y cada corte i, las uniones de generadas[B][i] y generadas[C][k−i].
    """
    generadas = {variable: {1: set()} for variable in gramatica.variables}
    for variable in gramatica.variables:
        for cuerpo in gramatica.cuerpos_de(variable):
            if len(cuerpo) == 1:
                generadas[variable][1].add(cuerpo)

    for k in range(2, longitud_maxima + 1):
        for variable in gramatica.variables:
            generadas[variable][k] = set()
            for cuerpo in gramatica.cuerpos_de(variable):
                if len(cuerpo) != 2:
                    continue
                izquierda, derecha = cuerpo
                for i in range(1, k):
                    for prefijo in generadas[izquierda][i]:
                        for sufijo in generadas[derecha][k - i]:
                            generadas[variable][k].add(prefijo + sufijo)

    inicial = gramatica.simbolo_inicial
    resultado = {cadena for k in range(1, longitud_maxima + 1) for cadena in generadas[inicial].get(k, set())}
    if () in gramatica.producciones.get(inicial, set()):
        resultado.add(())
    return resultado


def cadenas_fng(gramatica: Gramatica, longitud_maxima: int) -> set[Cadena]:
    """Cadenas de longitud ≤ n que genera una gramática en FNG (derivaciones por la izquierda).

    En FNG cada paso de derivación agrega exactamente un terminal, así que toda forma
    sentencial es (terminales ya generados, variables pendientes). Cada variable pendiente
    produce al menos un terminal, por eso se descarta la forma si
    |terminales| + |variables| > n: así la búsqueda siempre termina.
    """
    inicial = gramatica.simbolo_inicial
    resultado: set[Cadena] = set()
    if () in gramatica.producciones.get(inicial, set()):
        resultado.add(())

    pendientes: list[tuple[Cadena, Cadena]] = [((), (inicial,))]
    visitadas: set[tuple[Cadena, Cadena]] = set(pendientes)
    while pendientes:
        terminales, variables = pendientes.pop()
        if not variables:
            resultado.add(terminales)
            continue
        primera, resto = variables[0], variables[1:]
        for cuerpo in gramatica.cuerpos_de(primera):
            if not cuerpo:
                continue  # solo el inicial puede tener ε y ya se contó arriba
            forma = (terminales + cuerpo[:1], tuple(cuerpo[1:]) + resto)
            if len(forma[0]) + len(forma[1]) <= longitud_maxima and forma not in visitadas:
                visitadas.add(forma)
                pendientes.append(forma)
    return resultado


def comparar_lenguajes(gramatica_fnc: Gramatica, gramatica_fng: Gramatica,
                       longitud_maxima: int) -> tuple[set[Cadena], set[Cadena]]:
    """Devuelve (faltantes, sobrantes) hasta longitud n.

    faltantes: cadenas que genera la gramática en FNC y no la de FNG.
    sobrantes: cadenas que genera la gramática en FNG y no la de FNC.
    Si las dos están vacías, las gramáticas coinciden hasta esa longitud.
    """
    esperadas = cadenas_fnc(gramatica_fnc, longitud_maxima)
    obtenidas = cadenas_fng(gramatica_fng, longitud_maxima)
    return esperadas - obtenidas, obtenidas - esperadas


def texto_cadena(cadena: Cadena) -> str:
    """'a b a' para mostrar una cadena en el mensaje de una prueba; ε si es vacía."""
    return " ".join(cadena) if cadena else "ε"
