"""Fases 2 y 3 de la conversión a Greibach y verificación de terminales (RF13, RF14)."""

from fnc.modelo.gramatica import Gramatica
from fnc.modelo.historial import Paso
from fng.utilidades import aplicar_sustitucion, crear_paso, empieza_con_variable


def sustitucion_regresiva(gramatica: Gramatica, orden: list[str]) -> Paso:
    """Fase 2: sustituye hacia atrás para que todas las variables del orden empiecen con terminal.

    Recorre las variables desde A_(n-1) hasta A_1. Como cada producción que empieza
    con variable tiene como cabeza una A_k con k > i, y A_k ya empieza con terminal,
    sustituirla garantiza que la nueva producción empiece con terminal.
    """
    resultado = gramatica.copiar()
    sustituciones: list[str] = []

    for variable in reversed(orden[:-1]):
        cuerpos_a_sustituir = [
            cuerpo for cuerpo in resultado.cuerpos_de(variable)
            if empieza_con_variable(resultado, cuerpo)
        ]
        for cuerpo in cuerpos_a_sustituir:
            sustituciones.append(aplicar_sustitucion(resultado, variable, cuerpo))

    observaciones = [] if sustituciones else [
        "Todas las variables ya empiezan con terminal; no hay sustituciones."
    ]

    return crear_paso(
        "Fase 2: sustitución regresiva",
        gramatica,
        resultado,
        {"Sustituciones realizadas": sustituciones},
        observaciones,
    )


def convertir_variables_auxiliares(gramatica: Gramatica, auxiliares: list[str]) -> Paso:
    """Fase 3: sustituye las variables originales en las producciones de las variables auxiliares.

    Las variables auxiliares (creadas al eliminar recursividad izquierda) tienen cuerpos
    que comienzan con variables originales. Como todas las variables originales ya
    empiezan con terminal tras la Fase 2, sustituirlas deja a las auxiliares en FNG.
    """
    resultado = gramatica.copiar()
    sustituciones: list[str] = []

    if not auxiliares:
        return crear_paso(
            "Fase 3: conversión de variables auxiliares",
            gramatica,
            resultado,
            {"Variables auxiliares": [], "Sustituciones realizadas": []},
            ["No se crearon variables auxiliares."],
        )

    hubo_cambios = True
    while hubo_cambios:
        hubo_cambios = False
        for aux in auxiliares:
            cuerpos_a_sustituir = [
                cuerpo for cuerpo in resultado.cuerpos_de(aux)
                if empieza_con_variable(resultado, cuerpo)
            ]
            for cuerpo in cuerpos_a_sustituir:
                cabeza = cuerpo[0]
                # Solo sustituimos si todas las producciones de la cabeza ya empiezan con terminal
                if all(not empieza_con_variable(resultado, c) for c in resultado.cuerpos_de(cabeza)):
                    sustituciones.append(aplicar_sustitucion(resultado, aux, cuerpo))
                    hubo_cambios = True

    # Comprobación de seguridad
    for aux in auxiliares:
        for cuerpo in resultado.cuerpos_de(aux):
            if empieza_con_variable(resultado, cuerpo):
                raise RuntimeError(
                    f"Error interno: no se pudieron convertir todas las producciones de {aux} a terminal."
                )

    observaciones = [
        f"Se convirtieron las producciones de {len(auxiliares)} variable(s) auxiliar(es)."
    ]

    return crear_paso(
        "Fase 3: conversión de variables auxiliares",
        gramatica,
        resultado,
        {"Variables auxiliares": list(auxiliares), "Sustituciones realizadas": sustituciones},
        observaciones,
    )


def verificar_variables_tras_terminal(gramatica: Gramatica) -> Paso:
    """Verifica que después del primer terminal solo existan variables (RF14).

    En una conversión que parte de FNC esto siempre se cumple de forma natural;
    este paso comprueba formalmente la condición y deja constancia en el historial.
    """
    resultado = gramatica.copiar()
    total = resultado.cantidad_producciones()
    observaciones: list[str] = []

    fallas = False
    for _, cuerpo in gramatica.lista_producciones():
        if len(cuerpo) > 1 and any(resultado.es_terminal(s) for s in cuerpo[1:]):
            fallas = True
            break

    if not fallas:
        observaciones.append("Todas las producciones tienen solo variables después del terminal.")
    else:
        from fnc.algoritmos.chomsky import generar_nombre_auxiliar
        terminal_a_aux = {}
        for variable, cuerpo in gramatica.lista_producciones():
            if len(cuerpo) > 1 and any(resultado.es_terminal(s) for s in cuerpo[1:]):
                nuevo = [cuerpo[0]]
                for s in cuerpo[1:]:
                    if resultado.es_terminal(s):
                        if s not in terminal_a_aux:
                            aux = generar_nombre_auxiliar(resultado, "X")
                            resultado.agregar_variable(aux)
                            resultado.agregar_produccion(aux, (s,))
                            terminal_a_aux[s] = aux
                        nuevo.append(terminal_a_aux[s])
                    else:
                        nuevo.append(s)
                resultado.eliminar_produccion(variable, cuerpo)
                resultado.agregar_produccion(variable, tuple(nuevo))
        observaciones.append("Se sustituyeron terminales que aparecían después de la posición inicial.")

    return crear_paso(
        "Verificación: solo variables después del terminal",
        gramatica,
        resultado,
        {"Producciones revisadas": [str(total)]},
        observaciones,
    )
