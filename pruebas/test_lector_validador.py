import os
import tempfile
import unittest

from fnc.entrada.lector import guardar_archivo, leer_archivo, leer_simbolos, tokenizar
from fnc.validacion.validador import validar_fnc, validar_gramatica
from utilidades_pruebas import gramatica_desde_lineas


class PruebasLector(unittest.TestCase):
    def test_leer_simbolos_con_comas_y_espacios(self):
        self.assertEqual(leer_simbolos(" S, A  B,,B1 "), ["S", "A", "B", "B1"])

    def test_tokenizar_toma_el_simbolo_mas_largo(self):
        self.assertEqual(tokenizar("aX1b", ["S", "X1", "a", "b"]), ("a", "X1", "b"))
        self.assertEqual(tokenizar("a X1 b", ["S", "X1", "a", "b"]), ("a", "X1", "b"))

    def test_tokenizar_epsilon(self):
        for epsilon in ("ε", "λ", "eps"):
            self.assertEqual(tokenizar(epsilon, ["S"]), ())

    def test_tokenizar_simbolos_no_declarados(self):
        self.assertEqual(tokenizar("AD'c", ["A"]), ("A", "D'", "c"))

    def test_guardar_y_leer_archivo(self):
        datos = {"variables": "S, A", "terminales": "a, b", "inicial": "S",
                 "producciones": "S -> aA | ε\nA -> b"}
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "gramatica.txt")
            guardar_archivo(ruta, datos)
            self.assertEqual(leer_archivo(ruta), datos)

    def test_archivo_sin_formato(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "malo.txt")
            with open(ruta, "w", encoding="utf-8") as archivo:
                archivo.write("S -> a\n")
            with self.assertRaises(ValueError):
                leer_archivo(ruta)


class PruebasValidacionInicial(unittest.TestCase):
    def test_gramatica_valida(self):
        resultado = validar_gramatica("S, A, B", "a, b", "S", "S -> ASA | aB\nA -> B | S\nB -> b | ε")
        self.assertTrue(resultado.es_valida)
        self.assertEqual(resultado.gramatica.cantidad_producciones(), 6)

    def test_simbolos_no_declarados_se_descartan_sin_bloquear(self):
        resultado = validar_gramatica("S, A", "a, b", "S", "S -> AD | aSc | aA\nA -> a | B\nB -> b")
        self.assertTrue(resultado.es_valida)
        self.assertEqual(resultado.producciones_descartadas, [
            ("S", ("A", "D")), ("S", ("a", "S", "c")), ("A", ("B",)), ("B", ("b",)),
        ])
        self.assertEqual(resultado.gramatica.lineas_producciones(), ["S -> a A", "A -> a"])
        self.assertIn("Advertencia: la producción S -> AD usa la variable D, que no fue declarada; "
                      "se descarta por ser inútil.", resultado.advertencias)
        self.assertIn("Advertencia: la producción S -> aSc usa el símbolo c, que no fue declarado "
                      "como terminal; se descarta.", resultado.advertencias)
        self.assertIn("Advertencia: la variable B no fue declarada; se descartan sus producciones.",
                      resultado.advertencias)

    def test_gramatica_ingresada_conserva_lo_escrito(self):
        resultado = validar_gramatica("S", "a", "S", "S -> a | B\nB -> b")
        self.assertEqual(resultado.gramatica_ingresada.lineas_producciones(), ["S -> B | a", "B -> b"])
        self.assertEqual(resultado.gramatica.lineas_producciones(), ["S -> a"])

    def test_inicial_no_declarado_es_advertencia(self):
        resultado = validar_gramatica("S, A", "a", "X", "S -> a\nA -> a")
        self.assertTrue(resultado.es_valida)
        self.assertTrue(any("símbolo inicial X no pertenece" in a for a in resultado.advertencias))

    def test_componentes_vacios(self):
        resultado = validar_gramatica("", "", "", "")
        self.assertEqual(resultado.errores, [
            "Error: debe declarar al menos una variable.",
            "Error: debe indicar el símbolo inicial.",
            "Error: debe registrar al menos una producción.",
        ])
        self.assertEqual(resultado.advertencias, ["Advertencia: no se declaró ningún terminal."])

    def test_formatos_invalidos(self):
        errores = validar_gramatica("S, ab", "a, B, eps", "S", "S -> a").errores
        self.assertIn("Error: la variable 'ab' no es válida; las variables deben iniciar con letra "
                      "mayúscula (ej.: S, A, B1).", errores)
        self.assertEqual(sum("no es válido" in error for error in errores), 2)

    def test_errores_de_estructura_bloquean(self):
        resultado = validar_gramatica("S", "a, b", "S", "S = aB\nS -> a | | b\nS -> aεb\naB -> b")
        errores = resultado.errores
        self.assertFalse(resultado.es_valida)
        self.assertIn("Error: la línea 1 ('S = aB') no tiene el símbolo '->'.", errores)
        self.assertIn("Error: la producción 'S -> a | | b' tiene una alternativa vacía; "
                      "use ε para la cadena vacía.", errores)
        self.assertIn("Error: en la producción S -> aεb, ε debe aparecer sola.", errores)
        self.assertIn("Error: el lado izquierdo de la producción 'aB -> b' no es una variable válida.", errores)

    def test_advertencia_variable_sin_producciones(self):
        resultado = validar_gramatica("S, C", "a", "S", "S -> a")
        self.assertTrue(resultado.es_valida)
        self.assertEqual(resultado.advertencias, ["Advertencia: la variable C no tiene producciones."])


class PruebasValidacionFnc(unittest.TestCase):
    def test_acepta_gramatica_final_e3_con_epsilon_en_el_inicial(self):
        gramatica = gramatica_desde_lineas("S0", """
            S0 -> ε | X1 X2 | X1 X3
            S -> X1 X2 | X1 X3
            X1 -> a
            X2 -> b
            X3 -> S X2
        """)
        self.assertEqual(validar_fnc(gramatica), [])

    def test_acepta_gramatica_final_e4(self):
        gramatica = gramatica_desde_lineas("E", """
            E -> a | E X5 | T X6 | X1 X7
            T -> a | T X6 | X1 X7
            F -> a | X1 X7
            X1 -> (
            X2 -> )
            X3 -> +
            X4 -> *
            X5 -> X3 T
            X6 -> X4 F
            X7 -> E X2
        """)
        self.assertEqual(validar_fnc(gramatica), [])

    def test_rechaza_producciones_fuera_de_la_fnc(self):
        gramatica = gramatica_desde_lineas("S", """
            S -> a B | B | B C D | a
            B -> ε | b
            C -> c
            D -> d
        """)
        self.assertEqual(validar_fnc(gramatica), [
            "La producción S -> B no cumple la FNC: es una producción unitaria.",
            "La producción S -> a B no cumple la FNC: un cuerpo de longitud 2 debe tener dos variables.",
            "La producción S -> B C D no cumple la FNC: tiene más de dos símbolos.",
            "La producción B -> ε no cumple la FNC: solo el símbolo inicial puede producir ε "
            "y no debe aparecer a la derecha.",
        ])


if __name__ == "__main__":
    unittest.main()
