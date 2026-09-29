import os
import unittest

from fnc.entrada.lector import leer_archivo
from fnc.proceso import ErrorProceso, ProcesoFNC

CARPETA_EJEMPLOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ejemplos")


def proceso_con_ejemplo(nombre_archivo: str) -> ProcesoFNC:
    datos = leer_archivo(os.path.join(CARPETA_EJEMPLOS, nombre_archivo))
    proceso = ProcesoFNC()
    proceso.ingresar_gramatica(datos["variables"], datos["terminales"], datos["inicial"], datos["producciones"])
    return proceso


class PruebasProceso(unittest.TestCase):
    def test_no_permite_etapas_sin_validar(self):
        proceso = proceso_con_ejemplo("e1_nulas_unitarias.txt")
        with self.assertRaises(ErrorProceso):
            proceso.ejecutar_etapa("nulas")

    def test_validar_registra_el_primer_paso(self):
        proceso = proceso_con_ejemplo("e1_nulas_unitarias.txt")
        self.assertEqual(proceso.validar(), [])
        self.assertEqual(proceso.historial().pasos[0].nombre, "Validación de la gramática")
        self.assertEqual(proceso.siguiente_etapa(), "nulas")

    def test_gramatica_con_errores_no_avanza(self):
        proceso = proceso_con_ejemplo("e8_con_errores.txt")
        self.assertEqual(len(proceso.validar()), 3)
        self.assertFalse(proceso.gramatica_es_valida())
        with self.assertRaises(ErrorProceso):
            proceso.ejecutar_proceso_completo()

    def test_modo_paso_a_paso_respeta_el_orden(self):
        proceso = proceso_con_ejemplo("e1_nulas_unitarias.txt")
        proceso.validar()
        with self.assertRaisesRegex(ErrorProceso, "Eliminar producciones nulas"):
            proceso.ejecutar_etapa("unitarias")
        for etapa in ("nulas", "unitarias", "inutiles", "inalcanzables"):
            proceso.ejecutar_etapa(etapa)
            self.assertIsNone(proceso.gramatica_final())
        pasos_fnc = proceso.ejecutar_etapa("fnc")
        self.assertEqual(len(pasos_fnc), 3)
        self.assertTrue(proceso.proceso_terminado())
        self.assertIsNone(proceso.siguiente_etapa())

    def test_modo_automatico_e1(self):
        proceso = proceso_con_ejemplo("e1_nulas_unitarias.txt")
        pasos = proceso.ejecutar_proceso_completo()
        self.assertEqual([paso.numero for paso in pasos], list(range(1, 9)))
        self.assertEqual(proceso.gramatica_final().lineas_producciones(), [
            "S -> a | A S | A X2 | S A | X1 B",
            "A -> a | b | A S | A X2 | S A | X1 B",
            "B -> b",
            "X1 -> a",
            "X2 -> S A",
        ])
        self.assertEqual(pasos[-1].elementos_identificados,
                         {"Resultado": ["La gramática cumple la Forma Normal de Chomsky"]})

    def test_lenguaje_vacio_detiene_el_proceso(self):
        proceso = proceso_con_ejemplo("e7_lenguaje_vacio.txt")
        proceso.ejecutar_proceso_completo()
        self.assertTrue(proceso.lenguaje_vacio())
        self.assertIsNone(proceso.siguiente_etapa())
        self.assertIsNone(proceso.gramatica_final())
        with self.assertRaisesRegex(ErrorProceso, "vacío"):
            proceso.ejecutar_etapa("inalcanzables")

    def test_reiniciar_borra_todo(self):
        proceso = proceso_con_ejemplo("e3_inicial_anulable.txt")
        proceso.ejecutar_proceso_completo()
        proceso.reiniciar()
        self.assertTrue(proceso.historial().esta_vacio())
        self.assertIsNone(proceso.gramatica_original())
        self.assertFalse(proceso.gramatica_es_valida())

    def test_resultado_reproducible(self):
        finales = []
        for _ in range(2):
            proceso = proceso_con_ejemplo("e4_expresiones.txt")
            proceso.ejecutar_proceso_completo()
            finales.append(proceso.gramatica_final().a_texto())
        self.assertEqual(finales[0], finales[1])


if __name__ == "__main__":
    unittest.main()
