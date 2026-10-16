import unittest

from fng.algoritmos.orden import calcular_orden, ordenar_variables
from fng.algoritmos.sustitucion import sustituir_hacia_adelante
from utilidades_pruebas import gramatica_desde_lineas


def g1():
    return gramatica_desde_lineas("S", """
        S -> A B
        A -> B S | b
        B -> S A | a
    """)


def g4():
    return gramatica_desde_lineas("S0", """
        S0 -> ε | X1 X2 | X1 X3
        S -> X1 X2 | X1 X3
        X1 -> a
        X2 -> b
        X3 -> S X2
    """)


class PruebasOrden(unittest.TestCase):
    def test_orden_por_defecto(self):
        self.assertEqual(calcular_orden(g1()), (["S", "A", "B"], []))

    def test_orden_del_usuario(self):
        self.assertEqual(calcular_orden(g1(), ["B", "A", "S"]), (["B", "A", "S"], []))

    def test_orden_incompleto_y_variables_inexistentes(self):
        orden, advertencias = calcular_orden(g1(), ["B", "Z", "B"])
        self.assertEqual(orden, ["B", "S", "A"])
        self.assertEqual(advertencias, ["Advertencia: la variable Z del orden no existe en la gramática; se ignora."])

    def test_paso_de_ordenamiento(self):
        paso, orden = ordenar_variables(g1())
        self.assertEqual(paso.nombre, "Ordenamiento de variables")
        self.assertEqual(paso.elementos_identificados, {"Orden de las variables": ["A1 = S", "A2 = A", "A3 = B"]})
        self.assertEqual((paso.producciones_eliminadas, paso.producciones_agregadas), ([], []))

    def test_se_aparta_epsilon_del_inicial(self):
        gramatica = g4()
        paso, orden = ordenar_variables(gramatica)
        self.assertEqual(orden, ["S0", "S", "X1", "X2", "X3"])
        self.assertEqual(paso.producciones_eliminadas, [("S0", ())])
        self.assertEqual(paso.observaciones, ["Se aparta S0 -> ε; se reincorpora en la limpieza final."])
        self.assertIn((), gramatica.producciones["S0"])  # la gramática recibida no se modifica


class PruebasSustitucionHaciaAdelante(unittest.TestCase):
    def test_a1_y_a2_de_g1_no_requieren_sustituciones(self):
        orden = ["S", "A", "B"]
        for indice, variable in enumerate(orden[:2]):
            paso = sustituir_hacia_adelante(g1(), orden, indice)
            self.assertEqual(paso.elementos_identificados["Sustituciones realizadas"], [])
            self.assertEqual(paso.observaciones, [
                f"{variable} no tiene producciones que empiecen con una variable anterior; no requiere sustituciones."
            ])

    def test_sustituciones_sucesivas_de_g1(self):
        gramatica = g1()
        paso = sustituir_hacia_adelante(gramatica, ["S", "A", "B"], 2)
        self.assertEqual(paso.nombre, "Fase 1 · A3 = B: sustituciones")
        self.assertEqual(paso.elementos_identificados, {
            "Producciones analizadas": ["B -> a", "B -> S A"],
            "Sustituciones realizadas": ["B -> S A  ⇒  B -> A B A", "B -> A B A  ⇒  B -> b B A | B S B A"],
        })
        self.assertEqual(paso.producciones_eliminadas, [("B", ("S", "A"))])
        self.assertEqual(paso.producciones_agregadas, [("B", ("b", "B", "A")), ("B", ("B", "S", "B", "A"))])
        self.assertEqual(paso.observaciones, [])
        self.assertEqual(gramatica.cuerpos_de("B"), [("a",), ("S", "A")])  # no modifica la recibida

    def test_g4_x3(self):
        gramatica = g4()
        gramatica.eliminar_produccion("S0", ())
        paso = sustituir_hacia_adelante(gramatica, ["S0", "S", "X1", "X2", "X3"], 4)
        self.assertEqual(paso.elementos_identificados["Sustituciones realizadas"], [
            "X3 -> S X2  ⇒  X3 -> X1 X2 X2 | X1 X3 X2",
            "X3 -> X1 X2 X2  ⇒  X3 -> a X2 X2",
            "X3 -> X1 X3 X2  ⇒  X3 -> a X3 X2",
        ])
        self.assertEqual(paso.gramatica_resultante.lineas_producciones()[-1], "X3 -> a X2 X2 | a X3 X2")

    def test_orden_b_a_s(self):
        orden = ["B", "A", "S"]
        paso_a = sustituir_hacia_adelante(g1(), orden, 1)
        self.assertEqual(paso_a.elementos_identificados["Sustituciones realizadas"], ["A -> B S  ⇒  A -> a S | S A S"])
        paso_s = sustituir_hacia_adelante(paso_a.gramatica_resultante, orden, 2)
        self.assertEqual(paso_s.elementos_identificados["Sustituciones realizadas"],
                         ["S -> A B  ⇒  S -> b B | a S B | S A S B"])


if __name__ == "__main__":
    unittest.main()
