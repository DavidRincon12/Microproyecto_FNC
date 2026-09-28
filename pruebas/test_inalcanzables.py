import unittest

from fnc.algoritmos.inalcanzables import calcular_variables_alcanzables, eliminar_variables_inalcanzables
from utilidades_pruebas import gramatica_desde_texto


class PruebasInalcanzables(unittest.TestCase):
    def test_e2_variables_inalcanzables(self):
        # E2 tras haber eliminado la variable inútil B
        gramatica = gramatica_desde_texto(
            "S, A, C, D",
            "a, b, c, d",
            "S",
            "S -> a\nA -> b\nC -> c\nD -> d",
        )
        alcanzables = calcular_variables_alcanzables(gramatica)
        self.assertEqual(alcanzables, ["S"])

        paso = eliminar_variables_inalcanzables(gramatica)
        self.assertEqual(paso.elementos_identificados["Variables alcanzables"], ["S"])
        self.assertEqual(paso.elementos_identificados["Variables inalcanzables"], ["A", "C", "D"])
        self.assertEqual(paso.elementos_identificados["Terminales que dejan de usarse"], ["b", "c", "d"])
        self.assertEqual(
            paso.producciones_eliminadas,
            [("A", ("b",)), ("C", ("c",)), ("D", ("d",))],
        )
        self.assertEqual(paso.gramatica_resultante.variables, ["S"])
        self.assertEqual(paso.gramatica_resultante.terminales, ["a"])
        self.assertEqual(paso.gramatica_resultante.lista_producciones(), [("S", ("a",))])

    def test_todas_alcanzables(self):
        gramatica = gramatica_desde_texto(
            "S, A, B",
            "a, b",
            "S",
            "S -> AB\nA -> a\nB -> b",
        )
        paso = eliminar_variables_inalcanzables(gramatica)
        self.assertEqual(paso.elementos_identificados["Variables inalcanzables"], [])
        self.assertEqual(paso.elementos_identificados["Terminales que dejan de usarse"], [])
        self.assertEqual(paso.producciones_eliminadas, [])
        self.assertEqual(paso.gramatica_resultante.variables, gramatica.variables)

    def test_cadena_de_alcanzables_orden_bfs(self):
        gramatica = gramatica_desde_texto(
            "S, A, B, C",
            "a, c",
            "S",
            "S -> A\nA -> B\nB -> a\nC -> c",
        )
        alcanzables = calcular_variables_alcanzables(gramatica)
        self.assertEqual(alcanzables, ["S", "A", "B"])

        paso = eliminar_variables_inalcanzables(gramatica)
        self.assertEqual(paso.elementos_identificados["Variables inalcanzables"], ["C"])
        self.assertEqual(paso.elementos_identificados["Terminales que dejan de usarse"], ["c"])

    def test_no_modifica_gramatica_recibida(self):
        gramatica = gramatica_desde_texto(
            "S, A",
            "a, b",
            "S",
            "S -> a\nA -> b",
        )
        original_vars = list(gramatica.variables)
        original_prods = list(gramatica.lista_producciones())
        eliminar_variables_inalcanzables(gramatica)
        self.assertEqual(gramatica.variables, original_vars)
        self.assertEqual(list(gramatica.lista_producciones()), original_prods)


if __name__ == "__main__":
    unittest.main()
