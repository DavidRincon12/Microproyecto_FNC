import unittest

from fnc.modelo.gramatica import Gramatica
from fng.algoritmos.recursividad import (
    detectar_recursividad_izquierda,
    eliminar_recursividad_izquierda,
    nombre_variable_auxiliar,
)
from utilidades_pruebas import gramatica_desde_lineas


class PruebasRecursividad(unittest.TestCase):
    def test_detectar_recursividad_izquierda(self):
        g = gramatica_desde_lineas("S", "S -> S A | a\nA -> b")
        recursivas_s = detectar_recursividad_izquierda(g, "S")
        self.assertEqual(recursivas_s, [("S", ("S", "A"))])

        recursivas_a = detectar_recursividad_izquierda(g, "A")
        self.assertEqual(recursivas_a, [])

    def test_nombre_variable_auxiliar(self):
        g = gramatica_desde_lineas("S", "S -> a")
        self.assertEqual(nombre_variable_auxiliar(g, "S"), "S'")

        # Si S' ya existe, debe usar S''
        g.agregar_variable("S'")
        self.assertEqual(nombre_variable_auxiliar(g, "S"), "S''")

    def test_eliminar_recursividad_g3(self):
        # G3: S -> S A | a, A -> b
        g = gramatica_desde_lineas("S", "S -> S A | a\nA -> b")
        paso = eliminar_recursividad_izquierda(g, "S", 1)

        self.assertEqual(paso.nombre, "Fase 1 · A1 = S: eliminación de recursividad izquierda")
        self.assertEqual(paso.elementos_identificados["Variable auxiliar creada"], ["S'"])
        self.assertEqual(paso.elementos_identificados["Producciones con recursividad izquierda"], ["S -> S A"])
        self.assertEqual(paso.elementos_identificados["Producciones sin recursividad (β)"], ["S -> a"])

        self.assertEqual(paso.producciones_eliminadas, [("S", ("S", "A"))])
        self.assertEqual(
            paso.producciones_agregadas,
            [("S", ("a", "S'")), ("S'", ("A",)), ("S'", ("A", "S'"))],
        )

        esperadas_s = {("a",), ("a", "S'")}
        esperadas_s_prima = {("A",), ("A", "S'")}
        self.assertEqual(paso.gramatica_resultante.producciones["S"], esperadas_s)
        self.assertEqual(paso.gramatica_resultante.producciones["S'"], esperadas_s_prima)

    def test_eliminar_recursividad_g1_variable_b(self):
        # En G1 tras las sustituciones hacia adelante: B -> a | b B A | B S B A
        g = gramatica_desde_lineas(
            "S",
            "S -> A B\n"
            "A -> B S | b\n"
            "B -> a | b B A | B S B A",
        )
        paso = eliminar_recursividad_izquierda(g, "B", 3)

        self.assertEqual(paso.nombre, "Fase 1 · A3 = B: eliminación de recursividad izquierda")
        self.assertEqual(paso.elementos_identificados["Variable auxiliar creada"], ["B'"])
        self.assertEqual(paso.producciones_eliminadas, [("B", ("B", "S", "B", "A"))])
        self.assertEqual(
            paso.producciones_agregadas,
            [
                ("B", ("a", "B'")),
                ("B", ("b", "B", "A", "B'")),
                ("B'", ("S", "B", "A")),
                ("B'", ("S", "B", "A", "B'")),
            ],
        )

    def test_sin_recursividad_no_cambia_gramatica(self):
        g = gramatica_desde_lineas("S", "S -> A B | a\nA -> a\nB -> b")
        paso = eliminar_recursividad_izquierda(g, "S", 1)
        self.assertEqual(paso.producciones_eliminadas, [])
        self.assertEqual(paso.producciones_agregadas, [])
        self.assertEqual(paso.elementos_identificados["Variable auxiliar creada"], [])
        self.assertTrue(any("No hay recursividad" in obs for obs in paso.observaciones))

    def test_no_modifica_gramatica_recibida(self):
        g = gramatica_desde_lineas("S", "S -> S A | a\nA -> b")
        original = list(g.lista_producciones())
        eliminar_recursividad_izquierda(g, "S", 1)
        self.assertEqual(list(g.lista_producciones()), original)


if __name__ == "__main__":
    unittest.main()
