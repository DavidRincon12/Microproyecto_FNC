import unittest

from fnc.modelo.gramatica import Gramatica
from fnc.modelo.historial import Historial, Paso


def gramatica_e1() -> Gramatica:
    gramatica = Gramatica(["S", "A", "B"], ["a", "b"], "S")
    for variable, cuerpo in [("S", ("A", "S", "A")), ("S", ("a", "B")), ("A", ("B",)),
                             ("A", ("S",)), ("B", ("b",)), ("B", ())]:
        gramatica.agregar_produccion(variable, cuerpo)
    return gramatica


class PruebasGramatica(unittest.TestCase):
    def test_no_agrega_producciones_duplicadas(self):
        gramatica = gramatica_e1()
        self.assertFalse(gramatica.agregar_produccion("S", ("a", "B")))
        self.assertEqual(gramatica.cantidad_producciones(), 6)

    def test_agregar_produccion_a_variable_inexistente_falla(self):
        with self.assertRaises(ValueError):
            gramatica_e1().agregar_produccion("Z", ("a",))

    def test_cuerpos_en_orden_canonico(self):
        self.assertEqual(gramatica_e1().cuerpos_de("B"), [(), ("b",)])
        self.assertEqual(gramatica_e1().cuerpos_de("S"), [("a", "B"), ("A", "S", "A")])

    def test_copia_independiente(self):
        original = gramatica_e1()
        copia = original.copiar()
        copia.eliminar_produccion("B", ())
        copia.agregar_variable("C")
        self.assertIn((), original.producciones["B"])
        self.assertNotIn("C", original.variables)

    def test_eliminar_variable_borra_producciones_que_la_usan(self):
        gramatica = gramatica_e1()
        eliminadas = gramatica.eliminar_variable("B")
        self.assertEqual(eliminadas, [("S", ("a", "B")), ("A", ("B",)), ("B", ()), ("B", ("b",))])
        self.assertEqual(gramatica.lineas_producciones(), ["S -> A S A", "A -> S"])

    def test_nuevo_inicial_se_muestra_primero(self):
        gramatica = gramatica_e1()
        gramatica.definir_simbolo_inicial("S0")
        self.assertEqual(gramatica.variables_en_orden(), ["S0", "S", "A", "B"])

    def test_a_texto(self):
        esperado = (
            "V = {S, A, B}\nT = {a, b}\nInicial = S\nP:\n"
            "  S -> a B | A S A\n  A -> B | S\n  B -> ε | b"
        )
        self.assertEqual(gramatica_e1().a_texto(), esperado)


class PruebasHistorial(unittest.TestCase):
    def test_registrar_asigna_numeros_consecutivos(self):
        historial = Historial()
        gramatica = gramatica_e1()
        historial.registrar(Paso("Uno", gramatica, gramatica))
        historial.registrar(Paso("Dos", gramatica, gramatica))
        self.assertEqual([paso.numero for paso in historial.pasos], [1, 2])
        historial.limpiar()
        self.assertTrue(historial.esta_vacio())

    def test_paso_a_texto_muestra_todas_las_secciones(self):
        paso = Paso("Prueba", gramatica_e1(), gramatica_e1(), producciones_eliminadas=[("B", ())])
        texto = paso.a_texto()
        for seccion in ("Gramática inicial de la etapa:", "Elementos identificados:",
                        "Producciones eliminadas:", "  - B -> ε", "Producciones agregadas:",
                        "Observaciones:", "Gramática resultante:"):
            self.assertIn(seccion, texto)


if __name__ == "__main__":
    unittest.main()
