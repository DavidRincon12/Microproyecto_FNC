import os
import unittest

from fnc.entrada.lector import leer_archivo
from fng.proceso_fng import ErrorProcesoFNG, ProcesoFNG
from test_fng_ejemplos import CARPETA_EJEMPLOS_FNG

ARCHIVOS = {
    "G1": "g1_sustituciones_recursividad.txt",
    "G2": "g2_sustitucion_regresiva.txt",
    "G3": "g3_recursividad_directa.txt",
    "G4": "g4_con_epsilon.txt",
    "G5": "g5_expresiones.txt",
    "G6": "g6_no_fnc.txt",
    "G7": "g7_variables_inutiles.txt",
}

# Resultados esperados de la sección 8 de la guía: (número total de pasos, gramática final).
ESPERADOS = {
    "G1": (14, [
        "S -> b B | a S B | a B' S B | b B A S B | b B A B' S B",
        "A -> b | a S | a B' S | b B A S | b B A B' S",
        "B -> a | a B' | b B A | b B A B'",
        "B' -> b B B A | a S B B A | b B B A B' | a B' S B B A | a S B B A B' | a B' S B B A B' "
        "| b B A S B B A | b B A B' S B B A | b B A S B B A B' | b B A B' S B B A B'",
    ]),
    "G2": (13, ["S -> a | a B", "B -> b"]),
    "G3": (13, ["S -> a | a S'", "S' -> b | b S'"]),
    "G4": (15, ["S0 -> ε | a X2 | a X3", "X2 -> b", "X3 -> a X2 X2 | a X3 X2"]),
    "G5": (22, [
        "E -> a | ( X7 | a E' | a X6 | ( X7 E' | ( X7 X6 | a T' X6 | a X6 E' | ( X7 T' X6 | ( X7 X6 E' "
        "| a T' X6 E' | ( X7 T' X6 E'",
        "T -> a | ( X7 | a T' | ( X7 T'",
        "F -> a | ( X7",
        "X2 -> )",
        "X6 -> * F",
        "X7 -> a X2 | ( X7 X2 | a E' X2 | a X6 X2 | ( X7 E' X2 | ( X7 X6 X2 | a T' X6 X2 | a X6 E' X2 "
        "| ( X7 T' X6 X2 | ( X7 X6 E' X2 | a T' X6 E' X2 | ( X7 T' X6 E' X2",
        "E' -> + T | + T E'",
        "T' -> * F | * F T'",
    ]),
    "G7": (13, ["S -> a | a B", "B -> b"]),
}


def proceso_con_ejemplo(clave: str, texto_orden: str = "") -> ProcesoFNG:
    datos = leer_archivo(os.path.join(CARPETA_EJEMPLOS_FNG, ARCHIVOS[clave]))
    proceso = ProcesoFNG()
    proceso.ingresar_gramatica(datos["variables"], datos["terminales"], datos["inicial"],
                               datos["producciones"], texto_orden)
    return proceso


class PruebasResultadosDeLaGuia(unittest.TestCase):
    def test_numero_de_pasos_y_gramatica_final(self):
        for clave, (numero_pasos, final) in ESPERADOS.items():
            with self.subTest(clave):
                proceso = proceso_con_ejemplo(clave)
                proceso.ejecutar_todo()
                self.assertEqual(len(proceso.historial().pasos), numero_pasos)
                self.assertEqual(proceso.gramatica_final().lineas_producciones(), final)
                self.assertEqual(proceso.historial().pasos[-1].elementos_identificados,
                                 {"Resultado": ["La gramática cumple la Forma Normal de Greibach"]})

    def test_g8_es_g1_con_otro_orden(self):
        proceso = proceso_con_ejemplo("G1", "B, A, S")
        proceso.ejecutar_todo()
        self.assertEqual(proceso.orden_variables(), ["B", "A", "S"])
        self.assertEqual(len(proceso.historial().pasos), 14)
        self.assertEqual(proceso.gramatica_final().cantidad_producciones(), 27)
        self.assertEqual(proceso.gramatica_final().lineas_producciones()[0], "S -> b B | a S B | b B S' | a S B S'")

    def test_nombres_de_los_pasos_de_g1(self):
        proceso = proceso_con_ejemplo("G1")
        proceso.ejecutar_todo()
        self.assertEqual([paso.nombre for paso in proceso.historial().pasos], [
            "Validación de la gramática",
            "Validación de la Forma Normal de Chomsky",
            "Depuración previa: eliminación de variables inútiles",
            "Depuración previa: eliminación de variables inalcanzables",
            "Ordenamiento de variables",
            "Fase 1 · A1 = S: sustituciones",
            "Fase 1 · A2 = A: sustituciones",
            "Fase 1 · A3 = B: sustituciones",
            "Fase 1 · A3 = B: eliminación de recursividad izquierda",
            "Fase 2: sustitución regresiva",
            "Fase 3: conversión de variables auxiliares",
            "Verificación: solo variables después del terminal",
            "Limpieza final",
            "Validación de la Forma Normal de Greibach",
        ])

    def test_observacion_de_recursividad_en_la_fase_1(self):
        proceso = proceso_con_ejemplo("G1")
        proceso.ejecutar_todo()
        pasos = {paso.nombre: paso for paso in proceso.historial().pasos}
        self.assertIn("No hay recursividad izquierda directa en S.",
                      pasos["Fase 1 · A1 = S: sustituciones"].observaciones)
        self.assertNotIn("No hay recursividad izquierda directa en B.",
                         pasos["Fase 1 · A3 = B: sustituciones"].observaciones)

    def test_g4_reincorpora_epsilon(self):
        proceso = proceso_con_ejemplo("G4")
        proceso.ejecutar_todo()
        limpieza = proceso.historial().pasos[-2]
        self.assertEqual(limpieza.nombre, "Limpieza final")
        self.assertIn("Se reincorpora la producción ε del símbolo inicial.", limpieza.observaciones)
        self.assertIn(("S0", ()), limpieza.producciones_agregadas)


class PruebasModos(unittest.TestCase):
    def test_modo_paso_a_paso(self):
        proceso = proceso_con_ejemplo("G3")
        self.assertEqual(proceso.validar(), [])
        self.assertEqual(len(proceso.historial().pasos), 2)
        primero = proceso.siguiente_paso()
        self.assertEqual(primero.nombre, "Depuración previa: eliminación de variables inútiles")
        self.assertEqual(primero.numero, 3)
        while proceso.hay_siguiente_paso():
            proceso.siguiente_paso()
        self.assertTrue(proceso.proceso_terminado())
        self.assertEqual(len(proceso.historial().pasos), 13)
        with self.assertRaises(ErrorProcesoFNG):
            proceso.siguiente_paso()

    def test_orden_disponible_despues_del_ordenamiento(self):
        proceso = proceso_con_ejemplo("G1")
        proceso.validar()
        self.assertEqual(proceso.orden_variables(), [])
        for _ in range(3):
            proceso.siguiente_paso()
        self.assertEqual(proceso.orden_variables(), ["S", "A", "B"])

    def test_no_avanza_sin_validar(self):
        proceso = proceso_con_ejemplo("G1")
        with self.assertRaises(ErrorProcesoFNG):
            proceso.siguiente_paso()

    def test_automatico_valida_y_devuelve_todos_los_pasos(self):
        proceso = proceso_con_ejemplo("G2")
        pasos = proceso.ejecutar_todo()
        self.assertEqual(len(pasos), 13)
        self.assertEqual(pasos[0].nombre, "Validación de la gramática")

    def test_automatico_despues_de_algunos_pasos(self):
        proceso = proceso_con_ejemplo("G2")
        proceso.validar()
        proceso.siguiente_paso()
        restantes = proceso.ejecutar_todo()
        self.assertEqual(len(restantes), 10)
        self.assertEqual(len(proceso.historial().pasos), 13)

    def test_reproducible(self):
        finales = []
        for _ in range(2):
            proceso = proceso_con_ejemplo("G5")
            proceso.ejecutar_todo()
            finales.append(proceso.gramatica_final().a_texto())
        self.assertEqual(finales[0], finales[1])

    def test_reiniciar(self):
        proceso = proceso_con_ejemplo("G1")
        proceso.ejecutar_todo()
        proceso.reiniciar()
        self.assertTrue(proceso.historial().esta_vacio())
        self.assertIsNone(proceso.gramatica_final())
        self.assertFalse(proceso.hay_siguiente_paso())


class PruebasErroresYCasosLimite(unittest.TestCase):
    def test_g6_no_esta_en_fnc(self):
        proceso = proceso_con_ejemplo("G6")
        errores = proceso.validar()
        self.assertEqual(len(errores), 3)
        self.assertTrue(proceso.errores_son_de_fnc())
        self.assertFalse(proceso.gramatica_es_valida())
        with self.assertRaises(ErrorProcesoFNG):
            proceso.ejecutar_todo()

    def test_error_de_escritura_no_ofrece_convertir(self):
        proceso = ProcesoFNG()
        proceso.ingresar_gramatica("S", "a", "S", "S = a")
        self.assertEqual(len(proceso.validar()), 1)
        self.assertFalse(proceso.errores_son_de_fnc())

    def test_lenguaje_vacio(self):
        proceso = ProcesoFNG()
        proceso.ingresar_gramatica("S, A", "a", "S", "S -> A S\nA -> a")
        pasos = proceso.ejecutar_todo()
        self.assertTrue(proceso.lenguaje_vacio())
        self.assertTrue(proceso.proceso_terminado())
        self.assertIsNone(proceso.gramatica_final())
        self.assertEqual(pasos[-1].nombre, "Depuración previa: eliminación de variables inútiles")


class PruebasConvertirConMicroproyecto1(unittest.TestCase):
    def test_g6_se_convierte_y_luego_pasa_a_fng(self):
        proceso = proceso_con_ejemplo("G6")
        proceso.validar()
        textos = proceso.convertir_entrada_con_microproyecto1()
        self.assertEqual(textos, {"variables": "S", "terminales": "a", "inicial": "S", "producciones": "S -> a"})
        self.assertEqual(proceso.validar(), [])
        proceso.ejecutar_todo()
        self.assertEqual(proceso.gramatica_final().lineas_producciones(), ["S -> a"])

    def test_gramatica_general_pasa_por_los_dos_microproyectos(self):
        proceso = ProcesoFNG()
        proceso.ingresar_gramatica("S", "a, b", "S", "S -> aSb | ε")
        self.assertTrue(proceso.validar())
        proceso.convertir_entrada_con_microproyecto1()
        proceso.ejecutar_todo()
        self.assertEqual(proceso.gramatica_final().lineas_producciones(),
                         ["S0 -> ε | a X2 | a X3", "X2 -> b", "X3 -> a X2 X2 | a X3 X2"])

    def test_error_de_escritura_no_se_puede_convertir(self):
        proceso = ProcesoFNG()
        proceso.ingresar_gramatica("S", "a", "S", "S = a")
        with self.assertRaises(ErrorProcesoFNG):
            proceso.convertir_entrada_con_microproyecto1()

    def test_lenguaje_vacio_no_se_puede_convertir(self):
        proceso = ProcesoFNG()
        proceso.ingresar_gramatica("S, A", "a", "S", "S -> AS | A\nA -> AA")
        with self.assertRaises(ErrorProcesoFNG):
            proceso.convertir_entrada_con_microproyecto1()


if __name__ == "__main__":
    unittest.main()
