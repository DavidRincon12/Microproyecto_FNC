import unittest

from fng.algoritmos.terminales import (
    convertir_variables_auxiliares,
    sustitucion_regresiva,
    verificar_variables_tras_terminal,
)
from utilidades_pruebas import gramatica_desde_lineas


class PruebasTerminales(unittest.TestCase):
    def test_sustitucion_regresiva_g1(self):
        # G1 tras terminar la Fase 1 (sustituciones hacia adelante y eliminación de recursividad en B)
        g = gramatica_desde_lineas(
            "S",
            "S -> A B\n"
            "A -> B S | b\n"
            "B -> a | a B' | b B A | b B A B'\n"
            "B' -> S B A | S B A B'",
        )
        paso = sustitucion_regresiva(g, ["S", "A", "B"])

        self.assertEqual(paso.nombre, "Fase 2: sustitución regresiva")
        self.assertEqual(
            paso.producciones_eliminadas,
            [("S", ("A", "B")), ("A", ("B", "S"))],
        )
        # S y A deben tener ahora solo producciones que empiezan con terminal
        for var in ("S", "A"):
            for cuerpo in paso.gramatica_resultante.cuerpos_de(var):
                self.assertTrue(paso.gramatica_resultante.es_terminal(cuerpo[0]))

    def test_convertir_variables_auxiliares_g1(self):
        # G1 tras la Fase 2 (sustitución regresiva)
        g = gramatica_desde_lineas(
            "S",
            "S -> b B | a S B | a B' S B | b B A S B | b B A B' S B\n"
            "A -> b | a S | a B' S | b B A S | b B A B' S\n"
            "B -> a | a B' | b B A | b B A B'\n"
            "B' -> S B A | S B A B'",
        )
        paso = convertir_variables_auxiliares(g, ["B'"])

        self.assertEqual(paso.nombre, "Fase 3: conversión de variables auxiliares")
        self.assertEqual(
            paso.producciones_eliminadas,
            [("B'", ("S", "B", "A")), ("B'", ("S", "B", "A", "B'"))],
        )
        self.assertEqual(len(paso.producciones_agregadas), 10)
        for cuerpo in paso.gramatica_resultante.cuerpos_de("B'"):
            self.assertTrue(paso.gramatica_resultante.es_terminal(cuerpo[0]))

    def test_sin_auxiliares_no_hay_cambios(self):
        g = gramatica_desde_lineas("S", "S -> a B\nB -> b")
        paso = convertir_variables_auxiliares(g, [])
        self.assertEqual(paso.producciones_eliminadas, [])
        self.assertEqual(paso.producciones_agregadas, [])
        self.assertTrue(any("No se crearon" in obs for obs in paso.observaciones))

    def test_verificar_variables_tras_terminal(self):
        g = gramatica_desde_lineas(
            "S",
            "S -> a B | b\nB -> b",
        )
        paso = verificar_variables_tras_terminal(g)
        self.assertEqual(paso.elementos_identificados["Producciones revisadas"], ["3"])
        self.assertEqual(paso.producciones_eliminadas, [])
        self.assertEqual(paso.producciones_agregadas, [])


if __name__ == "__main__":
    unittest.main()
