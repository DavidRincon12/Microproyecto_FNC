import unittest

from fnc.modelo.gramatica import Gramatica
from fng.utilidades import (aplicar_sustitucion, calcular_cambios, crear_paso, empieza_con_variable,
                            reemplazar_cabeza, texto_sustitucion)


def gramatica_g1() -> Gramatica:
    gramatica = Gramatica(["S", "A", "B"], ["a", "b"], "S")
    for variable, cuerpo in [("S", ("A", "B")), ("A", ("B", "S")), ("A", ("b",)),
                             ("B", ("S", "A")), ("B", ("a",))]:
        gramatica.agregar_produccion(variable, cuerpo)
    return gramatica


class PruebasReemplazarCabeza(unittest.TestCase):
    def test_ejemplo_del_contrato(self):
        self.assertEqual(reemplazar_cabeza(("S", "A"), [("A", "B"), ("b",)]),
                         [("A", "B", "A"), ("b", "A")])

    def test_cuerpo_de_un_solo_simbolo(self):
        self.assertEqual(reemplazar_cabeza(("A",), [("a",), ("B", "C")]), [("a",), ("B", "C")])

    def test_sin_reemplazos_no_quedan_cuerpos(self):
        self.assertEqual(reemplazar_cabeza(("A", "B"), []), [])

    def test_cuerpo_vacio_es_un_error(self):
        with self.assertRaises(ValueError):
            reemplazar_cabeza((), [("a",)])


class PruebasSustitucion(unittest.TestCase):
    def test_empieza_con_variable(self):
        gramatica = gramatica_g1()
        self.assertTrue(empieza_con_variable(gramatica, ("S", "A")))
        self.assertFalse(empieza_con_variable(gramatica, ("a",)))
        self.assertFalse(empieza_con_variable(gramatica, ()))

    def test_texto_sustitucion(self):
        self.assertEqual(texto_sustitucion("B", ("S", "A"), [("A", "B", "A")]), "B -> S A  ⇒  B -> A B A")
        self.assertEqual(texto_sustitucion("B", ("A", "B", "A"), [("b", "B", "A"), ("B", "S", "B", "A")]),
                         "B -> A B A  ⇒  B -> b B A | B S B A")

    def test_aplicar_sustitucion_modifica_la_gramatica(self):
        gramatica = gramatica_g1()
        texto = aplicar_sustitucion(gramatica, "B", ("S", "A"))
        self.assertEqual(texto, "B -> S A  ⇒  B -> A B A")
        self.assertEqual(gramatica.cuerpos_de("B"), [("a",), ("A", "B", "A")])

    def test_sustituciones_sucesivas_de_g1(self):
        gramatica = gramatica_g1()
        aplicar_sustitucion(gramatica, "B", ("S", "A"))
        texto = aplicar_sustitucion(gramatica, "B", ("A", "B", "A"))
        self.assertEqual(texto, "B -> A B A  ⇒  B -> b B A | B S B A")
        self.assertEqual(gramatica.lineas_producciones()[-1], "B -> a | b B A | B S B A")


class PruebasPasos(unittest.TestCase):
    def test_calcular_cambios_es_el_cambio_neto(self):
        antes = gramatica_g1()
        despues = antes.copiar()
        aplicar_sustitucion(despues, "B", ("S", "A"))
        aplicar_sustitucion(despues, "B", ("A", "B", "A"))
        eliminadas, agregadas = calcular_cambios(antes, despues)
        # B -> A B A se creó y se eliminó dentro del mismo paso: no aparece en ninguna lista.
        self.assertEqual(eliminadas, [("B", ("S", "A"))])
        self.assertEqual(agregadas, [("B", ("b", "B", "A")), ("B", ("B", "S", "B", "A"))])

    def test_sin_cambios(self):
        gramatica = gramatica_g1()
        self.assertEqual(calcular_cambios(gramatica, gramatica.copiar()), ([], []))

    def test_crear_paso(self):
        antes = gramatica_g1()
        despues = antes.copiar()
        aplicar_sustitucion(despues, "B", ("S", "A"))
        paso = crear_paso("Fase 1 · A3 = B: sustituciones", antes, despues,
                          {"Sustituciones realizadas": ["B -> S A  ⇒  B -> A B A"]}, ["Observación"])
        self.assertEqual(paso.nombre, "Fase 1 · A3 = B: sustituciones")
        self.assertEqual(paso.producciones_eliminadas, [("B", ("S", "A"))])
        self.assertEqual(paso.producciones_agregadas, [("B", ("A", "B", "A"))])
        self.assertEqual(paso.observaciones, ["Observación"])
        self.assertIn("Sustituciones realizadas: B -> S A  ⇒  B -> A B A", paso.a_texto())

    def test_crear_paso_guarda_copias(self):
        antes = gramatica_g1()
        despues = antes.copiar()
        paso = crear_paso("Paso", antes, despues, {})
        despues.agregar_produccion("S", ("a",))
        antes.eliminar_produccion("S", ("A", "B"))
        self.assertEqual(paso.gramatica_inicial.cuerpos_de("S"), [("A", "B")])
        self.assertEqual(paso.gramatica_resultante.cuerpos_de("S"), [("A", "B")])


if __name__ == "__main__":
    unittest.main()
