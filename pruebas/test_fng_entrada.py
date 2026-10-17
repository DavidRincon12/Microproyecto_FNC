import os
import unittest

from fng.archivo import leer_archivo_fng
from fng.validacion.entrada import SUGERENCIA_FNC, validar_entrada
from test_fng_ejemplos import CARPETA_EJEMPLOS_FNG


def validar_ejemplo(nombre_archivo: str):
    datos = leer_archivo_fng(os.path.join(CARPETA_EJEMPLOS_FNG, nombre_archivo))
    return validar_entrada(datos["variables"], datos["terminales"], datos["inicial"], datos["producciones"])


class PruebasValidacionEntrada(unittest.TestCase):
    def test_gramatica_en_fnc_es_valida(self):
        resultado = validar_ejemplo("g1_sustituciones_recursividad.txt")
        self.assertTrue(resultado.es_valida)
        self.assertEqual(resultado.errores_fnc, [])
        self.assertEqual(resultado.gramatica.lineas_producciones(),
                         ["S -> b | A B", "A -> a | B C", "B -> b | S A", "C -> c | A S"])

    def test_epsilon_del_inicial_es_valida(self):
        resultado = validar_entrada("S0, S, A, B", "a, b", "S0", "S0 -> ε | A B\nS -> A B\nA -> a\nB -> b | S B")
        self.assertTrue(resultado.es_valida)

    def test_g6_no_esta_en_fnc(self):
        resultado = validar_ejemplo("g6_no_fnc.txt")
        self.assertFalse(resultado.es_valida)
        self.assertIsNone(resultado.gramatica)
        self.assertEqual(resultado.errores_fnc, [
            "La producción E -> D no cumple la FNC: es una producción unitaria.",
            "La producción E -> D 0 no cumple la FNC: un cuerpo de longitud 2 debe tener dos variables.",
            "La producción C -> ε no cumple la FNC: solo el símbolo inicial puede producir ε y no debe aparecer a la derecha.",
            "La producción C -> D no cumple la FNC: es una producción unitaria.",
            "La producción C -> D 1 D 2 no cumple la FNC: tiene más de dos símbolos.",
            "La producción D -> C 2 no cumple la FNC: un cuerpo de longitud 2 debe tener dos variables.",
        ])
        self.assertEqual(resultado.errores, resultado.errores_fnc + [SUGERENCIA_FNC])
        self.assertEqual(len(resultado.producciones_descartadas), 5)
        self.assertIn("Advertencia: la variable B no fue declarada; se descartan sus producciones.",
                      resultado.advertencias)

    def test_errores_de_escritura_no_son_de_fnc(self):
        resultado = validar_entrada("S", "a", "S", "S = a")
        self.assertFalse(resultado.es_valida)
        self.assertEqual(resultado.errores_fnc, [])
        self.assertEqual(resultado.errores, ["Error: la línea 1 ('S = a') no tiene el símbolo '->'."])

    def test_simbolos_no_declarados_se_descartan(self):
        resultado = validar_entrada("S, A", "a", "S", "S -> AB | AA\nA -> a")
        self.assertTrue(resultado.es_valida)
        self.assertEqual(resultado.producciones_descartadas, [("S", ("A", "B"))])
        self.assertEqual(resultado.gramatica.lineas_producciones(), ["S -> A A", "A -> a"])


if __name__ == "__main__":
    unittest.main()
