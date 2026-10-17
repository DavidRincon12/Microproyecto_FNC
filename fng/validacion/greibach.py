"""Validación automática de la Forma Normal de Greibach (RF17, RNF12)."""

from fnc.modelo.gramatica import Gramatica


def validar_fng(gramatica: Gramatica) -> list[str]:
    """Comprueba si todas las producciones de la gramática cumplen la FNG (RF17, RNF12).

    Una producción cumple la Forma Normal de Greibach si:
      - Es de la forma A -> a B1 B2 ... Bk con 'a' terminal y B1...Bk variables (k >= 0).
      - O es S -> ε, admitida únicamente si S es el símbolo inicial y no aparece
        en el lado derecho de ninguna producción de la gramática.

    Devuelve la lista de mensajes de error ([] si la gramática cumple la FNG).
    """
    inicial = gramatica.simbolo_inicial
    inicial_a_la_derecha = any(
        inicial in cuerpo for _, cuerpo in gramatica.lista_producciones()
    )
    errores: list[str] = []

    for variable, cuerpo in gramatica.lista_producciones():
        texto_p = Gramatica.produccion_a_texto(variable, cuerpo)
        if not cuerpo:
            if variable != inicial or inicial_a_la_derecha:
                errores.append(
                    f"La producción {texto_p} no cumple la FNG: solo el símbolo inicial puede producir ε y no debe aparecer a la derecha."
                )
            continue

        cabeza = cuerpo[0]
        if not gramatica.es_terminal(cabeza):
            errores.append(
                f"La producción {texto_p} no cumple la FNG: debe comenzar con un terminal."
            )
            continue

        resto = cuerpo[1:]
        if any(not gramatica.es_variable(s) for s in resto):
            errores.append(
                f"La producción {texto_p} no cumple la FNG: después del terminal solo puede haber variables."
            )

    return errores
