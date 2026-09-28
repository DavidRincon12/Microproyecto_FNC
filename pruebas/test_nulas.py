import unittest

from fnc.algoritmos.nulas import calcular_variables_anulables, eliminar_producciones_nulas
from utilidades_pruebas import gramatica_desde_texto


def e1():
    return gramatica_desde_texto("S, A, B", "a, b", "S", "S -> ASA | aB\nA -> B | S\nB -> b | ε")


class PruebasNulas(unittest.TestCase):
    def test_anulables_e1(self):
        self.assertEqual(calcular_variables_anulables(e1()), ["A", "B"])

    def test_e1(self):
        paso = eliminar_producciones_nulas(e1())
        self.assertEqual(paso.producciones_eliminadas, [("B", ())])
        self.assertEqual(paso.producciones_agregadas, [("S", ("a",)), ("S", ("A", "S")), ("S", ("S", "A"))])
        self.assertEqual(paso.gramatica_resultante.lineas_producciones(), [
            "S -> a | A S | S A | a B | A S A",
            "A -> B | S",
            "B -> b",
        ])
        self.assertEqual(paso.gramatica_resultante.simbolo_inicial, "S")

    def test_e3_inicial_anulable_crea_s0(self):
        gramatica = gramatica_desde_texto("S", "a, b", "S", "S -> aSb | ε")
        paso = eliminar_producciones_nulas(gramatica)
        self.assertEqual(paso.gramatica_resultante.simbolo_inicial, "S0")
        self.assertEqual(paso.producciones_agregadas,
                         [("S", ("a", "b")), ("S0", ("S",)), ("S0", ())])
        self.assertEqual(paso.gramatica_resultante.lineas_producciones(), [
            "S0 -> ε | S",
            "S -> a b | a S b",
        ])

    def test_e5_varias_anulables(self):
        gramatica = gramatica_desde_texto("S, A, B, C", "a, b, c", "S",
                                          "S -> ABC | aSc\nA -> aA | ε\nB -> bB | ε\nC -> c")
        paso = eliminar_producciones_nulas(gramatica)
        self.assertEqual(paso.elementos_identificados["Variables anulables"], ["A", "B"])
        self.assertEqual(paso.producciones_eliminadas, [("A", ()), ("B", ())])
        self.assertEqual(paso.gramatica_resultante.lineas_producciones(), [
            "S -> C | A C | B C | A B C | a S c",
            "A -> a | a A",
            "B -> b | b B",
            "C -> c",
        ])

    def test_sin_nulas_no_hay_cambios(self):
        gramatica = gramatica_desde_texto("S", "a", "S", "S -> aS | a")
        paso = eliminar_producciones_nulas(gramatica)
        self.assertEqual(paso.gramatica_resultante.lista_producciones(), gramatica.lista_producciones())
        self.assertEqual(paso.observaciones, ["La gramática no tiene producciones nulas; no hay cambios."])

    def test_no_modifica_la_gramatica_recibida(self):
        gramatica = e1()
        antes = gramatica.lista_producciones()
        eliminar_producciones_nulas(gramatica)
        self.assertEqual(gramatica.lista_producciones(), antes)


if __name__ == "__main__":
    unittest.main()
