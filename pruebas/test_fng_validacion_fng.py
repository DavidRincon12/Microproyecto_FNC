import unittest

from fnc.modelo.gramatica import Gramatica
from fng.validacion.greibach import validar_fng


class PruebasValidacionFNG(unittest.TestCase):
    def test_gramatica_valida_en_fng(self):
        g = Gramatica(["S", "B"], ["a", "b"], "S")
        g.agregar_produccion("S", ("a",))
        g.agregar_produccion("S", ("a", "B"))
        g.agregar_produccion("B", ("b",))
        self.assertEqual(validar_fng(g), [])

    def test_epsilon_en_inicial_valido(self):
        g = Gramatica(["S0", "B"], ["a", "b"], "S0")
        g.agregar_produccion("S0", ())
        g.agregar_produccion("S0", ("a", "B"))
        g.agregar_produccion("B", ("b",))
        self.assertEqual(validar_fng(g), [])

    def test_rechaza_no_comienza_con_terminal(self):
        # Caso 1: A -> B c
        g = Gramatica(["S", "A", "B"], ["b", "c"], "S")
        g.agregar_produccion("S", ("b",))
        g.agregar_produccion("A", ("B", "c"))
        g.agregar_produccion("B", ("b",))
        errores = validar_fng(g)
        self.assertIn("La producción A -> B c no cumple la FNG: debe comenzar con un terminal.", errores)

    def test_rechaza_terminal_despues_de_cabeza(self):
        # Caso 2: A -> a b
        g = Gramatica(["S", "A"], ["a", "b"], "S")
        g.agregar_produccion("S", ("a",))
        g.agregar_produccion("A", ("a", "b"))
        errores = validar_fng(g)
        self.assertIn("La producción A -> a b no cumple la FNG: después del terminal solo puede haber variables.", errores)

    def test_rechaza_epsilon_en_variable_no_inicial_o_que_aparece_a_la_derecha(self):
        # Caso 3: A -> ε
        g = Gramatica(["S", "A"], ["a"], "S")
        g.agregar_produccion("S", ("a", "A"))
        g.agregar_produccion("A", ())
        errores = validar_fng(g)
        self.assertIn(
            "La producción A -> ε no cumple la FNG: solo el símbolo inicial puede producir ε y no debe aparecer a la derecha.",
            errores,
        )


if __name__ == "__main__":
    unittest.main()
