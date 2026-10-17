import unittest

from pruebas.utilidades_pruebas import gramatica_desde_lineas
from pruebas.utilidades_pruebas_fng import cadenas_fnc, cadenas_fng, comparar_lenguajes, texto_cadena

# L = { a^n b^n : n ≥ 1 } en las dos formas normales
ANBN_FNC = """
S -> A X | A B
X -> S B
A -> a
B -> b
"""
ANBN_FNG = """
S -> a B | a S B
B -> b
"""


def cadenas(*textos):
    return {tuple(texto.split()) for texto in textos}


class PruebasCadenasFNC(unittest.TestCase):
    def test_anbn(self):
        self.assertEqual(cadenas_fnc(gramatica_desde_lineas("S", ANBN_FNC), 6),
                         cadenas("a b", "a a b b", "a a a b b b"))

    def test_epsilon_del_inicial(self):
        gramatica = gramatica_desde_lineas("S0", "S0 -> ε | A B\nA -> a\nB -> b")
        self.assertEqual(cadenas_fnc(gramatica, 3), cadenas("", "a b"))

    def test_variable_inutil_no_genera_nada(self):
        gramatica = gramatica_desde_lineas("S", "S -> A B | a\nA -> A B\nB -> b")
        self.assertEqual(cadenas_fnc(gramatica, 5), cadenas("a"))


class PruebasCadenasFNG(unittest.TestCase):
    def test_anbn(self):
        self.assertEqual(cadenas_fng(gramatica_desde_lineas("S", ANBN_FNG), 6),
                         cadenas("a b", "a a b b", "a a a b b b"))

    def test_recursividad_a_la_derecha_termina(self):
        gramatica = gramatica_desde_lineas("S", "S -> a | a S")
        self.assertEqual(cadenas_fng(gramatica, 3), cadenas("a", "a a", "a a a"))

    def test_epsilon_del_inicial(self):
        gramatica = gramatica_desde_lineas("S", "S -> ε | a B\nB -> b")
        self.assertEqual(cadenas_fng(gramatica, 2), cadenas("", "a b"))


class PruebasComparacion(unittest.TestCase):
    def test_gramaticas_equivalentes(self):
        faltantes, sobrantes = comparar_lenguajes(
            gramatica_desde_lineas("S", ANBN_FNC), gramatica_desde_lineas("S", ANBN_FNG), 8)
        self.assertEqual((faltantes, sobrantes), (set(), set()))

    def test_detecta_cadenas_sobrantes(self):
        fng = gramatica_desde_lineas("S", "S -> a | a B | a S B\nB -> b")
        faltantes, sobrantes = comparar_lenguajes(gramatica_desde_lineas("S", ANBN_FNC), fng, 4)
        self.assertEqual(faltantes, set())
        self.assertIn(("a",), sobrantes)

    def test_detecta_epsilon_faltante(self):
        fnc = gramatica_desde_lineas("S0", "S0 -> ε | A B\nA -> a\nB -> b")
        fng = gramatica_desde_lineas("S0", "S0 -> a B\nB -> b")
        self.assertEqual(comparar_lenguajes(fnc, fng, 3), (cadenas(""), set()))

    def test_texto_cadena(self):
        self.assertEqual(texto_cadena(("a", "b", "a")), "a b a")
        self.assertEqual(texto_cadena(()), "ε")


if __name__ == "__main__":
    unittest.main()
