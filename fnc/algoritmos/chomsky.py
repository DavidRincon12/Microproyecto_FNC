"""Transformación a Forma Normal de Chomsky (FNC) (RF15, RF16, RF17, RNF09)."""

from fnc.modelo.gramatica import Cuerpo, Gramatica, Produccion
from fnc.modelo.historial import Paso


def generar_nombre_auxiliar(gramatica: Gramatica, prefijo: str = "X") -> str:
    """Genera un nombre de variable auxiliar único que no exista en la gramática (RF17, RNF09).

    Prueba sucesivamente con X1, X2, X3... retornando el primer nombre que no esté
    ni en las variables ni en los terminales declarados.
    """
    indice = 1
    while True:
        candidato = f"{prefijo}{indice}"
        if not gramatica.es_variable(candidato) and not gramatica.es_terminal(candidato):
            return candidato
        indice += 1


def sustituir_terminales(gramatica: Gramatica) -> Paso:
    """Sustituye terminales en producciones de longitud >= 2 por variables auxiliares (RF15).

    Crea producciones de la forma Xn -> a para cada terminal presente en un cuerpo
    compuesto, reutilizando la misma variable auxiliar en toda la gramática.
    """
    resultado = gramatica.copiar()
    terminal_a_auxiliar: dict[str, str] = {}
    variables_originales = gramatica.variables_en_orden()

    eliminadas: list[Produccion] = []
    agregadas: list[Produccion] = []

    for variable in variables_originales:
        for cuerpo in gramatica.cuerpos_de(variable):
            # Solo se transforman cuerpos de longitud >= 2 con al menos un terminal
            if len(cuerpo) < 2 or not any(gramatica.es_terminal(simbolo) for simbolo in cuerpo):
                continue

            nuevo_cuerpo_lista = []
            for simbolo in cuerpo:
                if gramatica.es_terminal(simbolo):
                    if simbolo not in terminal_a_auxiliar:
                        aux = generar_nombre_auxiliar(resultado, "X")
                        resultado.agregar_variable(aux)
                        resultado.agregar_produccion(aux, (simbolo,))
                        terminal_a_auxiliar[simbolo] = aux
                        agregadas.append((aux, (simbolo,)))
                    nuevo_cuerpo_lista.append(terminal_a_auxiliar[simbolo])
                else:
                    nuevo_cuerpo_lista.append(simbolo)

            nuevo_cuerpo: Cuerpo = tuple(nuevo_cuerpo_lista)
            if nuevo_cuerpo != cuerpo:
                resultado.eliminar_produccion(variable, cuerpo)
                resultado.agregar_produccion(variable, nuevo_cuerpo)
                eliminadas.append((variable, cuerpo))
                agregadas.append((variable, nuevo_cuerpo))

    observaciones: list[str] = []
    if not terminal_a_auxiliar:
        observaciones.append("No hay terminales en producciones de longitud mayor o igual a dos; no hay cambios.")
    else:
        observaciones.append(
            f"Se sustituyeron {len(terminal_a_auxiliar)} terminal(es) usando variables auxiliares."
        )

    elementos_identificados = {
        "Terminales sustituidos": [
            f"{t} → {var}" for t, var in sorted(terminal_a_auxiliar.items())
        ]
    }

    return Paso(
        nombre="FNC (1/2): sustitución de terminales",
        gramatica_inicial=gramatica.copiar(),
        gramatica_resultante=resultado,
        elementos_identificados=elementos_identificados,
        producciones_eliminadas=eliminadas,
        producciones_agregadas=agregadas,
        observaciones=observaciones,
    )


def reducir_producciones_largas(gramatica: Gramatica) -> Paso:
    """Reduce producciones con más de dos variables a formas binarias (RF16).

    Reutiliza variables auxiliares cuando varias producciones comparten el mismo
    sufijo de variables, optimizando la cantidad de variables creadas.
    """
    resultado = gramatica.copiar()
    sufijo_a_auxiliar: dict[tuple[str, ...], str] = {}
    variables_originales = gramatica.variables_en_orden()

    eliminadas: list[Produccion] = []
    agregadas: list[Produccion] = []
    auxiliares_creadas: list[str] = []

    for variable in variables_originales:
        for cuerpo in gramatica.cuerpos_de(variable):
            if len(cuerpo) < 3:
                continue

            resultado.eliminar_produccion(variable, cuerpo)
            eliminadas.append((variable, cuerpo))

            actual = variable
            n = len(cuerpo)
            for i in range(n - 2):
                bi = cuerpo[i]
                sufijo = cuerpo[i + 1:]
                if sufijo in sufijo_a_auxiliar:
                    y = sufijo_a_auxiliar[sufijo]
                    resultado.agregar_produccion(actual, (bi, y))
                    agregadas.append((actual, (bi, y)))
                    break
                else:
                    y = generar_nombre_auxiliar(resultado, "X")
                    resultado.agregar_variable(y)
                    sufijo_a_auxiliar[sufijo] = y
                    auxiliares_creadas.append(f"{y} = {' '.join(sufijo)}")
                    resultado.agregar_produccion(actual, (bi, y))
                    agregadas.append((actual, (bi, y)))
                    actual = y
            else:
                # El último par binario B(n-1) Bn
                resultado.agregar_produccion(actual, (cuerpo[-2], cuerpo[-1]))
                agregadas.append((actual, (cuerpo[-2], cuerpo[-1])))

    observaciones: list[str] = []
    if not auxiliares_creadas:
        observaciones.append("No hay producciones de longitud mayor a dos; no hay cambios.")
    else:
        observaciones.append(
            f"Se redujeron {len(eliminadas)} producción(es) larga(s) creando {len(auxiliares_creadas)} variable(s) auxiliar(es)."
        )

    return Paso(
        nombre="FNC (2/2): reducción de producciones largas",
        gramatica_inicial=gramatica.copiar(),
        gramatica_resultante=resultado,
        elementos_identificados={"Variables auxiliares creadas": auxiliares_creadas},
        producciones_eliminadas=eliminadas,
        producciones_agregadas=agregadas,
        observaciones=observaciones,
    )
