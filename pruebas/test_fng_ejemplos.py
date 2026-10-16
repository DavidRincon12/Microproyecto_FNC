import os
import unittest

from fnc.entrada.lector import leer_archivo
from fnc.validacion.validador import validar_fnc, validar_gramatica

CARPETA_EJEMPLOS_FNG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ejemplos_fng")

ARCHIVOS_EN_FNC = [
    "g1_sustituciones_recursividad.txt",
    "g2_sustitucion_regresiva.txt",
    "g3_recursividad_directa.txt",
    "g4_con_epsilon.txt",
    "g5_expresiones.txt",
    "g7_variables_inutiles.txt",
]


def gramatica_de_ejemplo(nombre_archivo: str):
    datos = leer_archivo(os.path.join(CARPETA_EJEMPLOS_FNG, nombre_archivo))
    return validar_gramatica(datos["variables"], datos["terminales"], datos["inicial"], datos["producciones"])


class PruebasArchivosEjemplo(unittest.TestCase):
    def test_estan_los_siete_archivos(self):
        self.assertEqual(len([n for n in os.listdir(CARPETA_EJEMPLOS_FNG) if n.endswith(".txt")]), 7)

    def test_ejemplos_en_fnc(self):
        for nombre in ARCHIVOS_EN_FNC:
            with self.subTest(nombre):
                resultado = gramatica_de_ejemplo(nombre)
                self.assertTrue(resultado.es_valida)
                self.assertEqual(resultado.producciones_descartadas, [])
                self.assertEqual(validar_fnc(resultado.gramatica), [])

    def test_g1_es_el_de_la_guia(self):
        gramatica = gramatica_de_ejemplo("g1_sustituciones_recursividad.txt").gramatica
        self.assertEqual(gramatica.lineas_producciones(), ["S -> A B", "A -> b | B S", "B -> a | S A"])

    def test_g6_no_esta_en_fnc(self):
        resultado = gramatica_de_ejemplo("g6_no_fnc.txt")
        self.assertTrue(resultado.es_valida)
        self.assertEqual(resultado.producciones_descartadas, [("B", ("b", "c"))])
        self.assertEqual(validar_fnc(resultado.gramatica), [
            "La producción S -> A no cumple la FNC: es una producción unitaria.",
            "La producción S -> a B no cumple la FNC: un cuerpo de longitud 2 debe tener dos variables.",
        ])


if __name__ == "__main__":
    unittest.main()
