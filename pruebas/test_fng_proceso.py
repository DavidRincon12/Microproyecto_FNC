import os
import unittest

from fng.archivo import leer_archivo_fng
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
    "G8": "g8_orden_personalizado.txt",
    "G9": "g9_ceros_y_unos.txt",
}

# G4, G5, G6 y G9 no están en FNC: primero pasan por el Microproyecto 1.
GENERALES = {"G4", "G5", "G6", "G9"}

# (número total de pasos, número de producciones de la gramática final)
ESPERADOS = {
    "G1": (15, 45),
    "G2": (15, 22),
    "G3": (16, 18),
    "G4": (17, 51),
    "G5": (22, 36),
    "G6": (20, 54),
    "G7": (14, 17),
    "G8": (15, 46),
    "G9": (17, 14),
}

FINALES = {
    "G2": [
        "S -> 0 | 0 B | 2 D | 1 D B | 2 A B | 3 A D | 2 D D B | 3 A A B | 3 B D B | 3 A D D B",
        "A -> 0 | 1 D | 2 A | 2 D D | 3 A A | 3 B D | 3 A D D",
        "B -> 1 | 2 D | 3 B | 3 A D",
        "D -> 3",
    ],
    "G3": [
        "S -> 0 | 0 S' | 2 S | 2 B' S | 2 S S' | 2 B' S S'",
        "S' -> 1 | 1 A' | 1 S' | 1 A' S'",
        "A' -> 2 | 2 A' | 2 B' | 2 B' A'",
        "B' -> 1 | 1 A' | 1 B' | 1 A' B'",
    ],
    "G7": [
        "S -> 0 | 0 B",
        "B -> 1 | 0 B | 1 B' | 0 B B | 0 B B' | 0 B B B'",
        "B' -> 1 | 0 B | 1 B' | 0 B B | 0 B B' | 1 B' B' | 0 B B B' | 0 B B' B' | 0 B B B' B'",
    ],
    "G9": [
        "S -> 0 B | 1 A",
        "A -> 0 | 0 S | 1 X3",
        "B -> 1 | 0 X4 | 1 S",
        "X3 -> 0 A | 0 S A | 1 X3 A",
        "X4 -> 1 B | 0 X4 B | 1 S B",
    ],
}


def proceso_con_ejemplo(clave: str, convertir: bool = True) -> ProcesoFNG:
    """Proceso con el ejemplo ingresado (sin validar). Los generales llegan ya convertidos a FNC."""
    datos = leer_archivo_fng(os.path.join(CARPETA_EJEMPLOS_FNG, ARCHIVOS[clave]))
    proceso = ProcesoFNG()
    proceso.ingresar_gramatica(datos["variables"], datos["terminales"], datos["inicial"],
                               datos["producciones"], datos["orden"])
    if convertir and clave in GENERALES:
        proceso.convertir_entrada_con_microproyecto1()
    return proceso


class PruebasResultadosDeLosEjemplos(unittest.TestCase):
    def test_numero_de_pasos_y_producciones(self):
        for clave, (numero_pasos, numero_producciones) in ESPERADOS.items():
            with self.subTest(clave):
                proceso = proceso_con_ejemplo(clave)
                proceso.ejecutar_todo()
                self.assertEqual(len(proceso.historial().pasos), numero_pasos)
                self.assertEqual(proceso.gramatica_final().cantidad_producciones(), numero_producciones)
                self.assertEqual(proceso.historial().pasos[-1].elementos_identificados,
                                 {"Resultado": ["La gramática cumple la Forma Normal de Greibach"]})

    def test_gramaticas_finales(self):
        for clave, final in FINALES.items():
            with self.subTest(clave):
                proceso = proceso_con_ejemplo(clave)
                proceso.ejecutar_todo()
                self.assertEqual(proceso.gramatica_final().lineas_producciones(), final)

    def test_g8_es_g1_con_otro_orden(self):
        proceso = proceso_con_ejemplo("G8")
        proceso.ejecutar_todo()
        self.assertEqual(proceso.orden_variables(), ["C", "B", "A", "S"])
        self.assertEqual(proceso.gramatica_final().lineas_producciones()[0],
                         "S -> 1 | 0 B | 1 S' | 0 B S' | 1 C B | 1 C B S'")

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
            "Fase 1 · A4 = C: sustituciones",
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

    def test_g1_sustituciones_sucesivas_en_b(self):
        proceso = proceso_con_ejemplo("G1")
        proceso.ejecutar_todo()
        pasos = {paso.nombre: paso for paso in proceso.historial().pasos}
        self.assertEqual(pasos["Fase 1 · A3 = B: sustituciones"].elementos_identificados["Sustituciones realizadas"], [
            "B -> S A  ⇒  B -> 1 A | A B A",
            "B -> A B A  ⇒  B -> 0 B A | B C B A",
        ])

    def test_g4_reincorpora_epsilon(self):
        proceso = proceso_con_ejemplo("G4")
        proceso.ejecutar_todo()
        limpieza = proceso.historial().pasos[-2]
        self.assertEqual(limpieza.nombre, "Limpieza final")
        self.assertIn("Se reincorpora la producción ε del símbolo inicial.", limpieza.observaciones)
        self.assertIn(("S0", ()), limpieza.producciones_agregadas)

    def test_g7_depuracion_previa(self):
        proceso = proceso_con_ejemplo("G7")
        proceso.ejecutar_todo()
        pasos = proceso.historial().pasos
        self.assertIn("Se eliminaron 2 variable(s) no generadora(s) y sus producciones: C, E.", pasos[2].observaciones)
        self.assertIn("Se eliminaron 1 variable(s) inalcanzable(s): D.", pasos[3].observaciones)


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
        self.assertEqual(len(proceso.historial().pasos), 16)
        with self.assertRaises(ErrorProcesoFNG):
            proceso.siguiente_paso()

    def test_orden_disponible_despues_del_ordenamiento(self):
        proceso = proceso_con_ejemplo("G1")
        proceso.validar()
        self.assertEqual(proceso.orden_variables(), [])
        for _ in range(3):
            proceso.siguiente_paso()
        self.assertEqual(proceso.orden_variables(), ["S", "A", "B", "C"])

    def test_no_avanza_sin_validar(self):
        proceso = proceso_con_ejemplo("G1")
        with self.assertRaises(ErrorProcesoFNG):
            proceso.siguiente_paso()

    def test_automatico_valida_y_devuelve_todos_los_pasos(self):
        proceso = proceso_con_ejemplo("G2")
        pasos = proceso.ejecutar_todo()
        self.assertEqual(len(pasos), 15)
        self.assertEqual(pasos[0].nombre, "Validación de la gramática")

    def test_automatico_despues_de_algunos_pasos(self):
        proceso = proceso_con_ejemplo("G2")
        proceso.validar()
        proceso.siguiente_paso()
        restantes = proceso.ejecutar_todo()
        self.assertEqual(len(restantes), 12)
        self.assertEqual(len(proceso.historial().pasos), 15)

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
        proceso = proceso_con_ejemplo("G6", convertir=False)
        errores = proceso.validar()
        self.assertEqual(len(errores), 7)  # 6 producciones fuera de la FNC y la sugerencia
        self.assertTrue(proceso.errores_son_de_fnc())
        self.assertEqual(len(proceso.advertencias()), 5)
        self.assertEqual(len(proceso.errores_fnc()), 6)
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
        proceso = proceso_con_ejemplo("G6", convertir=False)
        proceso.validar()
        textos = proceso.convertir_entrada_con_microproyecto1()
        self.assertEqual(textos["variables"], "E, C, D, X1, X2, X3, X4, X5")
        self.assertEqual(textos["producciones"].splitlines()[0], "E -> 2 | C X1 | D X2")
        self.assertEqual(proceso.validar(), [])
        self.assertEqual(proceso.advertencias(), [])
        proceso.ejecutar_todo()
        self.assertEqual(proceso.gramatica_final().cantidad_producciones(), 54)

    def test_la_conversion_conserva_el_orden(self):
        proceso = ProcesoFNG()
        proceso.ingresar_gramatica("S, A", "a, b", "S", "S -> aA | b\nA -> a", "A, S")
        textos = proceso.convertir_entrada_con_microproyecto1()
        self.assertEqual(textos["orden"], "A, S")
        proceso.ejecutar_todo()
        self.assertEqual(proceso.orden_variables()[:2], ["A", "S"])

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
