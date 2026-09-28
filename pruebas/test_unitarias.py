import unittest

from fnc.algoritmos.nulas import eliminar_producciones_nulas
from fnc.algoritmos.unitarias import (calcular_pares_unitarios, eliminar_producciones_unitarias,
                                      encontrar_producciones_unitarias)
from utilidades_pruebas import gramatica_desde_texto


def despues_de_nulas(variables, terminales, inicial, producciones):
    gramatica = gramatica_desde_texto(variables, terminales, inicial, producciones)
    return eliminar_producciones_nulas(gramatica).gramatica_resultante


class PruebasUnitarias(unittest.TestCase):
    def test_e1(self):
        gramatica = despues_de_nulas("S, A, B", "a, b", "S", "S -> ASA | aB\nA -> B | S\nB -> b | ε")
        self.assertEqual(encontrar_producciones_unitarias(gramatica), [("A", ("B",)), ("A", ("S",))])
        self.assertEqual(calcular_pares_unitarios(gramatica), [("A", "B"), ("A", "S")])
        paso = eliminar_producciones_unitarias(gramatica)
        self.assertEqual(paso.gramatica_resultante.lineas_producciones(), [
            "S -> a | A S | S A | a B | A S A",
            "A -> a | b | A S | S A | a B | A S A",
            "B -> b",
        ])

    def test_e3(self):
        gramatica = despues_de_nulas("S", "a, b", "S", "S -> aSb | ε")
        paso = eliminar_producciones_unitarias(gramatica)
        self.assertEqual(paso.producciones_eliminadas, [("S0", ("S",))])
        self.assertEqual(paso.producciones_agregadas, [("S0", ("a", "b")), ("S0", ("a", "S", "b"))])
        self.assertEqual(paso.gramatica_resultante.lineas_producciones(), [
            "S0 -> ε | a b | a S b",
            "S -> a b | a S b",
        ])

    def test_e4_cadena_de_unitarias(self):
        gramatica = despues_de_nulas("E, T, F", "+, *, (, ), a", "E",
                                     "E -> E+T | T\nT -> T*F | F\nF -> (E) | a")
        self.assertEqual(calcular_pares_unitarios(gramatica), [("E", "T"), ("E", "F"), ("T", "F")])
        paso = eliminar_producciones_unitarias(gramatica)
        self.assertEqual(paso.gramatica_resultante.lineas_producciones(), [
            "E -> a | ( E ) | E + T | T * F",
            "T -> a | ( E ) | T * F",
            "F -> a | ( E )",
        ])

    def test_e5(self):
        gramatica = despues_de_nulas("S, A, B, C", "a, b, c", "S",
                                     "S -> ABC | aSc\nA -> aA | ε\nB -> bB | ε\nC -> c")
        paso = eliminar_producciones_unitarias(gramatica)
        self.assertEqual(paso.producciones_agregadas, [("S", ("c",))])
        self.assertEqual(paso.gramatica_resultante.lineas_producciones()[0],
                         "S -> c | A C | B C | A B C | a S c")

    def test_ciclo_de_unitarias(self):
        gramatica = gramatica_desde_texto("S, A", "a, b", "S", "S -> A | a\nA -> S | b")
        paso = eliminar_producciones_unitarias(gramatica)
        self.assertEqual(paso.gramatica_resultante.lineas_producciones(), ["S -> a | b", "A -> a | b"])


if __name__ == "__main__":
    unittest.main()
