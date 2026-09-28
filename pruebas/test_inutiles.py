import unittest

from fnc.algoritmos.inutiles import calcular_variables_generadoras, eliminar_variables_inutiles
from utilidades_pruebas import gramatica_desde_texto


class PruebasInutiles(unittest.TestCase):
    def test_e2_variables_inutiles(self):
        # E2: B -> BC no puede derivar terminales; B es inútil (no generadora)
        gramatica = gramatica_desde_texto(
            "S, A, B, C, D",
            "a, b, c, d",
            "S",
            "S -> AB | a\nA -> b\nB -> BC\nC -> c\nD -> d",
        )
        generadoras = calcular_variables_generadoras(gramatica)
        self.assertEqual(generadoras, ["S", "A", "C", "D"])

        paso = eliminar_variables_inutiles(gramatica)
        self.assertEqual(paso.elementos_identificados["Variables generadoras"], ["S", "A", "C", "D"])
        self.assertEqual(paso.elementos_identificados["Variables no generadoras (inútiles)"], ["B"])
        self.assertEqual(paso.producciones_eliminadas, [("S", ("A", "B")), ("B", ("B", "C"))])
        self.assertNotIn("B", paso.gramatica_resultante.variables)
        self.assertNotIn(("S", ("A", "B")), paso.gramatica_resultante.lista_producciones())

    def test_e7_lenguaje_vacio_inicial_no_generador(self):
        # E7: S -> AS, A -> a. S no es generadora, L(G) es vacío
        gramatica = gramatica_desde_texto(
            "S, A",
            "a",
            "S",
            "S -> AS\nA -> a",
        )
        generadoras = calcular_variables_generadoras(gramatica)
        self.assertEqual(generadoras, ["A"])

        paso = eliminar_variables_inutiles(gramatica)
        self.assertEqual(paso.elementos_identificados["Variables no generadoras (inútiles)"], ["S"])
        self.assertTrue(any("el lenguaje es vacío" in obs for obs in paso.observaciones))

    def test_todas_generadoras_no_hay_cambios(self):
        gramatica = gramatica_desde_texto(
            "S, A",
            "a, b",
            "S",
            "S -> aA | b\nA -> a",
        )
        paso = eliminar_variables_inutiles(gramatica)
        self.assertEqual(paso.elementos_identificados["Variables no generadoras (inútiles)"], [])
        self.assertEqual(paso.producciones_eliminadas, [])
        self.assertEqual(paso.gramatica_resultante.variables, gramatica.variables)

    def test_epsilon_cuenta_como_generadora(self):
        gramatica = gramatica_desde_texto(
            "S, A",
            "a",
            "S",
            "S -> A\nA -> ε",
        )
        generadoras = calcular_variables_generadoras(gramatica)
        self.assertEqual(generadoras, ["S", "A"])

    def test_no_modifica_gramatica_recibida(self):
        gramatica = gramatica_desde_texto(
            "S, A, B",
            "a",
            "S",
            "S -> A | B\nA -> a\nB -> B",
        )
        original_prods = list(gramatica.lista_producciones())
        eliminar_variables_inutiles(gramatica)
        self.assertEqual(list(gramatica.lista_producciones()), original_prods)


if __name__ == "__main__":
    unittest.main()
