import os
import unittest

from fnc.entrada.lector import leer_archivo
from fng.validacion.entrada import SUGERENCIA_FNC, validar_entrada
from test_fng_ejemplos import CARPETA_EJEMPLOS_FNG


def validar_ejemplo(nombre_archivo: str):
    datos = leer_archivo(os.path.join(CARPETA_EJEMPLOS_FNG, nombre_archivo))
    return validar_entrada(datos["variables"], datos["terminales"], datos["inicial"], datos["producciones"])


class PruebasValidacionEntrada(unittest.TestCase):
    def test_gramatica_en_fnc_es_valida(self):
        resultado = validar_ejemplo("g1_sustituciones_recursividad.txt")
        self.assertTrue(resultado.es_valida)
        self.assertEqual(resultado.errores_fnc, [])
        self.assertEqual(resultado.gramatica.lineas_producciones(), ["S -> A B", "A -> b | B S", "B -> a | S A"])

    def test_epsilon_del_inicial_es_valida(self):
        resultado = validar_ejemplo("g4_con_epsilon.txt")
        self.assertTrue(resultado.es_valida)

    def test_g6_no_esta_en_fnc(self):
        resultado = validar_ejemplo("g6_no_fnc.txt")
        self.assertFalse(resultado.es_valida)
        self.assertIsNone(resultado.gramatica)
        self.assertEqual(resultado.errores_fnc, [
            "La producción S -> A no cumple la FNC: es una producción unitaria.",
            "La producción S -> a B no cumple la FNC: un cuerpo de longitud 2 debe tener dos variables.",
        ])
        self.assertEqual(resultado.errores, resultado.errores_fnc + [SUGERENCIA_FNC])
        self.assertEqual(resultado.producciones_descartadas, [("B", ("b", "c"))])

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
