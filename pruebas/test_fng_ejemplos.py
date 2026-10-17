import os
import unittest

from fnc.entrada.lector import leer_archivo
from fnc.validacion.validador import validar_fnc, validar_gramatica
from fng.proceso_fng import ProcesoFNG
from fng.validacion.greibach import validar_fng
from utilidades_pruebas_fng import cadenas_fng, comparar_lenguajes, texto_cadena

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


# Integración (RNF06): cada ejemplo de principio a fin y la gramática final debe generar
# las mismas cadenas que la de entrada. G8 es G1 con el orden B, A, S.
LONGITUD_EQUIVALENCIA = 7

CASOS_INTEGRACION = {
    "G1": ("g1_sustituciones_recursividad.txt", ""),
    "G2": ("g2_sustitucion_regresiva.txt", ""),
    "G3": ("g3_recursividad_directa.txt", ""),
    "G4": ("g4_con_epsilon.txt", ""),
    "G5": ("g5_expresiones.txt", ""),
    "G7": ("g7_variables_inutiles.txt", ""),
    "G8": ("g1_sustituciones_recursividad.txt", "B, A, S"),
}


def convertir_ejemplo(nombre_archivo: str, texto_orden: str = "", convertir_a_fnc: bool = False) -> ProcesoFNG:
    datos = leer_archivo(os.path.join(CARPETA_EJEMPLOS_FNG, nombre_archivo))
    proceso = ProcesoFNG()
    proceso.ingresar_gramatica(datos["variables"], datos["terminales"], datos["inicial"],
                               datos["producciones"], texto_orden)
    proceso.validar()
    if convertir_a_fnc:
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
        for clave, (nombre_archivo, texto_orden) in CASOS_INTEGRACION.items():
            with self.subTest(clave):
                self.comprobar_conversion(convertir_ejemplo(nombre_archivo, texto_orden))

    def test_g6_pasa_primero_por_el_microproyecto_1(self):
        self.comprobar_conversion(convertir_ejemplo("g6_no_fnc.txt", convertir_a_fnc=True))

    def test_el_orden_cambia_la_gramatica_pero_no_el_lenguaje(self):
        g1 = convertir_ejemplo("g1_sustituciones_recursividad.txt").gramatica_final()
        g8 = convertir_ejemplo("g1_sustituciones_recursividad.txt", "B, A, S").gramatica_final()
        self.assertNotEqual(g1.lineas_producciones(), g8.lineas_producciones())
        self.assertEqual(cadenas_fng(g1, LONGITUD_EQUIVALENCIA), cadenas_fng(g8, LONGITUD_EQUIVALENCIA))


if __name__ == "__main__":
    unittest.main()
