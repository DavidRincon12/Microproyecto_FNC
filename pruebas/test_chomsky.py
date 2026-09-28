import unittest

from fnc.algoritmos.chomsky import (
    generar_nombre_auxiliar,
    reducir_producciones_largas,
    sustituir_terminales,
)
from fnc.validacion.validador import validar_fnc
from utilidades_pruebas import gramatica_desde_texto


class PruebasChomsky(unittest.TestCase):
    def test_generar_nombre_auxiliar_unicos(self):
        gramatica = gramatica_desde_texto("S, A", "a, b", "S", "S -> a")
        self.assertEqual(generar_nombre_auxiliar(gramatica), "X1")

        # Si X1 ya existe en la gramática (E6), debe generar X2
        gramatica_con_x1 = gramatica_desde_texto("S, X1", "a, b", "S", "S -> a")
        self.assertEqual(generar_nombre_auxiliar(gramatica_con_x1), "X2")

    def test_sustitucion_terminales_e1(self):
        # E1 tras eliminación de unitarias
        gramatica = gramatica_desde_texto(
            "S, A, B",
            "a, b",
            "S",
            "S -> a | AS | SA | aB | ASA\n"
            "A -> a | b | AS | SA | aB | ASA\n"
            "B -> b",
        )
        paso = sustituir_terminales(gramatica)
        self.assertEqual(paso.elementos_identificados["Terminales sustituidos"], ["a → X1"])
        self.assertIn("X1", paso.gramatica_resultante.variables)
        self.assertIn(("X1", ("a",)), paso.gramatica_resultante.lista_producciones())
        self.assertIn(("S", ("X1", "B")), paso.gramatica_resultante.lista_producciones())
        self.assertIn(("A", ("X1", "B")), paso.gramatica_resultante.lista_producciones())
        self.assertNotIn(("S", ("a", "B")), paso.gramatica_resultante.lista_producciones())

    def test_reduccion_producciones_largas_e1(self):
        # E1 tras sustituir terminales
        gramatica = gramatica_desde_texto(
            "S, A, B, X1",
            "a, b",
            "S",
            "S -> a | AS | SA | X1B | ASA\n"
            "A -> a | b | AS | SA | X1B | ASA\n"
            "B -> b\n"
            "X1 -> a",
        )
        paso = reducir_producciones_largas(gramatica)
        self.assertEqual(paso.elementos_identificados["Variables auxiliares creadas"], ["X2 = S A"])
        self.assertIn("X2", paso.gramatica_resultante.variables)
        self.assertIn(("S", ("A", "X2")), paso.gramatica_resultante.lista_producciones())
        self.assertIn(("A", ("A", "X2")), paso.gramatica_resultante.lista_producciones())
        self.assertIn(("X2", ("S", "A")), paso.gramatica_resultante.lista_producciones())
        self.assertNotIn(("S", ("A", "S", "A")), paso.gramatica_resultante.lista_producciones())

        # La gramática resultante debe cumplir la FNC completamente
        errores_fnc = validar_fnc(paso.gramatica_resultante)
        self.assertEqual(errores_fnc, [])

    def test_e6_nombres_unicos_salta_x1(self):
        # E6: el usuario ya definió X1, las auxiliares deben ser X2, X3, etc.
        gramatica = gramatica_desde_texto(
            "S, X1",
            "a, b",
            "S",
            "S -> aX1b | ab\nX1 -> aX1 | a",
        )
        paso_sustitucion = sustituir_terminales(gramatica)
        # Se deben haber sustituido a y b creando X2 y X3
        self.assertEqual(
            paso_sustitucion.elementos_identificados["Terminales sustituidos"],
            ["a → X2", "b → X3"],
        )
        paso_largas = reducir_producciones_largas(paso_sustitucion.gramatica_resultante)
        self.assertEqual(
            paso_largas.elementos_identificados["Variables auxiliares creadas"],
            ["X4 = X1 X3"],
        )
        errores_fnc = validar_fnc(paso_largas.gramatica_resultante)
        self.assertEqual(errores_fnc, [])

    def test_gramatica_ya_en_fnc_no_cambia(self):
        gramatica = gramatica_desde_texto(
            "S, A, B",
            "a, b",
            "S",
            "S -> AB | a\nA -> a\nB -> b",
        )
        paso_sust = sustituir_terminales(gramatica)
        self.assertEqual(paso_sust.producciones_agregadas, [])
        paso_largas = reducir_producciones_largas(gramatica)
        self.assertEqual(paso_largas.producciones_agregadas, [])

    def test_no_modifica_gramatica_recibida(self):
        gramatica = gramatica_desde_texto(
            "S, A",
            "a, b",
            "S",
            "S -> aSb | ab\nA -> a",
        )
        original_prods = list(gramatica.lista_producciones())
        sustituir_terminales(gramatica)
        self.assertEqual(list(gramatica.lista_producciones()), original_prods)
        reducir_producciones_largas(gramatica)
        self.assertEqual(list(gramatica.lista_producciones()), original_prods)


if __name__ == "__main__":
    unittest.main()
