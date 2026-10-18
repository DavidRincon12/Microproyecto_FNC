import os
import unittest

from fnc.validacion.validador import validar_fnc, validar_gramatica
from fng.archivo import leer_archivo_fng
from fng.proceso_fng import ProcesoFNG
from fng.validacion.greibach import validar_fng
from utilidades_pruebas_fng import cadenas_fng, comparar_lenguajes, texto_cadena

CARPETA_EJEMPLOS_FNG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ejemplos_fng")

ARCHIVOS_EN_FNC = [
    "g1_sustituciones_recursividad.txt",
    "g2_sustitucion_regresiva.txt",
    "g3_recursividad_directa.txt",
    "g7_variables_inutiles.txt",
    "g8_orden_personalizado.txt",
]

ARCHIVOS_GENERALES = [
    "g4_con_epsilon.txt",
    "g5_expresiones.txt",
    "g6_no_fnc.txt",
    "g9_ceros_y_unos.txt",
]


def gramatica_de_ejemplo(nombre_archivo: str):
    datos = leer_archivo_fng(os.path.join(CARPETA_EJEMPLOS_FNG, nombre_archivo))
    return validar_gramatica(datos["variables"], datos["terminales"], datos["inicial"], datos["producciones"])


class PruebasArchivosEjemplo(unittest.TestCase):
    def test_estan_los_nueve_archivos(self):
        self.assertEqual(len([n for n in os.listdir(CARPETA_EJEMPLOS_FNG) if n.endswith(".txt")]), 9)

    def test_ejemplos_en_fnc(self):
        for nombre in ARCHIVOS_EN_FNC:
            with self.subTest(nombre):
                resultado = gramatica_de_ejemplo(nombre)
                self.assertTrue(resultado.es_valida)
                self.assertEqual(validar_fnc(resultado.gramatica), [])

    def test_terminales_numericos(self):
        for nombre in ARCHIVOS_EN_FNC + ARCHIVOS_GENERALES:
            with self.subTest(nombre):
                self.assertTrue(all(t.isdigit() for t in gramatica_de_ejemplo(nombre).gramatica.terminales))

    def test_ejemplos_generales_no_estan_en_fnc(self):
        for nombre in ARCHIVOS_GENERALES:
            with self.subTest(nombre):
                resultado = gramatica_de_ejemplo(nombre)
                self.assertTrue(resultado.es_valida)
                self.assertNotEqual(validar_fnc(resultado.gramatica), [])

    def test_g1(self):
        gramatica = gramatica_de_ejemplo("g1_sustituciones_recursividad.txt").gramatica
        self.assertEqual(gramatica.lineas_producciones(),
                         ["S -> 1 | A B", "A -> 0 | B C", "B -> 1 | S A", "C -> 2 | A S"])

    def test_g6_descarta_los_simbolos_no_declarados(self):
        resultado = gramatica_de_ejemplo("g6_no_fnc.txt")
        self.assertEqual(resultado.producciones_descartadas, [
            ("B", ("C", "D", "1")), ("B", ("C",)), ("B", ("0",)), ("D", ("B",)), ("D", ("D", "Q")),
        ])

    def test_g7_descarta_los_simbolos_no_declarados(self):
        resultado = gramatica_de_ejemplo("g7_variables_inutiles.txt")
        self.assertEqual(resultado.producciones_descartadas, [("B", ("1", "9")), ("F", ("0",))])

    def test_g8_trae_su_orden(self):
        datos = leer_archivo_fng(os.path.join(CARPETA_EJEMPLOS_FNG, "g8_orden_personalizado.txt"))
        self.assertEqual(datos["orden"], "C, B, A, S")
        self.assertNotIn("ORDEN", datos["producciones"])


# Integración (RNF06): cada ejemplo de principio a fin y la gramática final debe generar
# las mismas cadenas que la gramática en FNC con que empieza la conversión.
LONGITUD_EQUIVALENCIA = 7


def convertir_ejemplo(nombre_archivo: str) -> ProcesoFNG:
    """Convierte el ejemplo de principio a fin; los generales pasan antes por el Microproyecto 1."""
    datos = leer_archivo_fng(os.path.join(CARPETA_EJEMPLOS_FNG, nombre_archivo))
    proceso = ProcesoFNG()
    proceso.ingresar_gramatica(datos["variables"], datos["terminales"], datos["inicial"],
                               datos["producciones"], datos["orden"])
    if proceso.validar():
        proceso.convertir_entrada_con_microproyecto1()
        proceso.validar()
    proceso.ejecutar_todo()
    return proceso


class PruebasIntegracion(unittest.TestCase):
    def comprobar_conversion(self, proceso: ProcesoFNG):
        self.assertTrue(proceso.proceso_terminado())
        final = proceso.gramatica_final()
        self.assertEqual(validar_fng(final), [])

        faltantes, sobrantes = comparar_lenguajes(proceso.gramatica_original(), final, LONGITUD_EQUIVALENCIA)
        self.assertEqual(faltantes, set(), "La FNG no genera: " + ", ".join(sorted(map(texto_cadena, faltantes))))
        self.assertEqual(sobrantes, set(), "La FNG genera de más: " + ", ".join(sorted(map(texto_cadena, sobrantes))))

        # Cada paso parte de la gramática con que terminó el anterior (historial continuo).
        pasos = proceso.historial().pasos
        for anterior, siguiente in zip(pasos, pasos[1:]):
            self.assertEqual(siguiente.gramatica_inicial.lineas_producciones(),
                             anterior.gramatica_resultante.lineas_producciones(), siguiente.nombre)
        self.assertEqual(pasos[-1].gramatica_resultante.lineas_producciones(), final.lineas_producciones())

    def test_ejemplos_equivalentes_y_en_fng(self):
        for nombre in ARCHIVOS_EN_FNC + ARCHIVOS_GENERALES:
            with self.subTest(nombre):
                self.comprobar_conversion(convertir_ejemplo(nombre))

    def test_el_orden_cambia_la_gramatica_pero_no_el_lenguaje(self):
        g1 = convertir_ejemplo("g1_sustituciones_recursividad.txt").gramatica_final()
        g8 = convertir_ejemplo("g8_orden_personalizado.txt").gramatica_final()
        self.assertNotEqual(g1.lineas_producciones(), g8.lineas_producciones())
        self.assertEqual(cadenas_fng(g1, LONGITUD_EQUIVALENCIA), cadenas_fng(g8, LONGITUD_EQUIVALENCIA))


if __name__ == "__main__":
    unittest.main()
