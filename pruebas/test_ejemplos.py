"""Pruebas de integración completa de los ejemplos E1 a E8 (RNF06, RNF11, RNF12).

Verifica que cada ejemplo de la especificación se procese de principio a fin,
que las gramáticas finales cumplan la Forma Normal de Chomsky y que las ejecuciones
sean completamente reproducibles y deterministas.
"""

import os
import unittest

from fnc.entrada.lector import leer_archivo
from fnc.proceso import ProcesoFNC
from fnc.validacion.validador import validar_fnc


def ruta_ejemplo(nombre: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "ejemplos", nombre)


class PruebasEjemplosIntegracion(unittest.TestCase):
    def test_e1_nulas_unitarias_completo(self):
        datos = leer_archivo(ruta_ejemplo("e1_nulas_unitarias.txt"))
        proceso = ProcesoFNC()
        proceso.ingresar_gramatica(
            datos["variables"], datos["terminales"], datos["inicial"], datos["producciones"]
        )
        errores = proceso.validar()
        self.assertEqual(errores, [])

        pasos = proceso.ejecutar_proceso_completo()
        self.assertTrue(proceso.proceso_terminado())

        g_final = proceso.gramatica_final()
        self.assertIsNotNone(g_final)
        self.assertEqual(validar_fnc(g_final), [])

        # Comprobación de producciones esperadas de E1
        producciones_texto = [f"{v} -> {g_final.cuerpo_a_texto(c)}" for v, c in g_final.lista_producciones()]
        self.assertIn("S -> a", producciones_texto)
        self.assertIn("S -> A S", producciones_texto)
        self.assertIn("S -> A X2", producciones_texto)
        self.assertIn("S -> S A", producciones_texto)
        self.assertIn("S -> X1 B", producciones_texto)
        self.assertIn("B -> b", producciones_texto)
        self.assertIn("X1 -> a", producciones_texto)
        self.assertIn("X2 -> S A", producciones_texto)

    def test_e2_inutiles_inalcanzables_completo(self):
        datos = leer_archivo(ruta_ejemplo("e2_inutiles_inalcanzables.txt"))
        proceso = ProcesoFNC()
        proceso.ingresar_gramatica(
            datos["variables"], datos["terminales"], datos["inicial"], datos["producciones"]
        )
        self.assertEqual(proceso.validar(), [])

        proceso.ejecutar_proceso_completo()
        self.assertTrue(proceso.proceso_terminado())

        g_final = proceso.gramatica_final()
        self.assertEqual(validar_fnc(g_final), [])
        self.assertEqual(g_final.variables, ["S"])
        self.assertEqual(g_final.terminales, ["a"])
        self.assertEqual(g_final.lista_producciones(), [("S", ("a",))])

    def test_e3_inicial_anulable_completo(self):
        datos = leer_archivo(ruta_ejemplo("e3_inicial_anulable.txt"))
        proceso = ProcesoFNC()
        proceso.ingresar_gramatica(
            datos["variables"], datos["terminales"], datos["inicial"], datos["producciones"]
        )
        self.assertEqual(proceso.validar(), [])

        proceso.ejecutar_proceso_completo()
        self.assertTrue(proceso.proceso_terminado())

        g_final = proceso.gramatica_final()
        self.assertEqual(validar_fnc(g_final), [])
        self.assertEqual(g_final.simbolo_inicial, "S0")
        producciones_texto = [f"{v} -> {g_final.cuerpo_a_texto(c)}" for v, c in g_final.lista_producciones()]
        self.assertIn("S0 -> ε", producciones_texto)
        self.assertIn("S0 -> X1 X2", producciones_texto)
        self.assertIn("S0 -> X1 X3", producciones_texto)
        self.assertIn("S -> X1 X2", producciones_texto)
        self.assertIn("S -> X1 X3", producciones_texto)
        self.assertIn("X1 -> a", producciones_texto)
        self.assertIn("X2 -> b", producciones_texto)
        self.assertIn("X3 -> S X2", producciones_texto)

    def test_e4_expresiones_aritmeticas_completo(self):
        datos = leer_archivo(ruta_ejemplo("e4_expresiones.txt"))
        proceso = ProcesoFNC()
        proceso.ingresar_gramatica(
            datos["variables"], datos["terminales"], datos["inicial"], datos["producciones"]
        )
        self.assertEqual(proceso.validar(), [])

        proceso.ejecutar_proceso_completo()
        self.assertTrue(proceso.proceso_terminado())

        g_final = proceso.gramatica_final()
        self.assertEqual(validar_fnc(g_final), [])

    def test_e5_varias_anulables_y_largas_completo(self):
        datos = leer_archivo(ruta_ejemplo("e5_varias_anulables.txt"))
        proceso = ProcesoFNC()
        proceso.ingresar_gramatica(
            datos["variables"], datos["terminales"], datos["inicial"], datos["producciones"]
        )
        self.assertEqual(proceso.validar(), [])

        proceso.ejecutar_proceso_completo()
        self.assertTrue(proceso.proceso_terminado())

        g_final = proceso.gramatica_final()
        self.assertEqual(validar_fnc(g_final), [])

    def test_e6_nombres_unicos_salta_x1_completo(self):
        datos = leer_archivo(ruta_ejemplo("e6_nombres_unicos.txt"))
        proceso = ProcesoFNC()
        proceso.ingresar_gramatica(
            datos["variables"], datos["terminales"], datos["inicial"], datos["producciones"]
        )
        self.assertEqual(proceso.validar(), [])

        proceso.ejecutar_proceso_completo()
        self.assertTrue(proceso.proceso_terminado())

        g_final = proceso.gramatica_final()
        self.assertEqual(validar_fnc(g_final), [])
        # Las auxiliares deben ser X2, X3, X4 porque X1 ya fue declarada por el usuario
        self.assertIn("X1", g_final.variables)
        self.assertIn("X2", g_final.variables)
        self.assertIn("X3", g_final.variables)
        self.assertIn("X4", g_final.variables)

    def test_e7_lenguaje_vacio_detiene_proceso(self):
        datos = leer_archivo(ruta_ejemplo("e7_lenguaje_vacio.txt"))
        proceso = ProcesoFNC()
        proceso.ingresar_gramatica(
            datos["variables"], datos["terminales"], datos["inicial"], datos["producciones"]
        )
        self.assertEqual(proceso.validar(), [])

        pasos = proceso.ejecutar_proceso_completo()
        self.assertTrue(proceso.lenguaje_vacio())
        self.assertFalse(proceso.proceso_terminado())
        # El proceso debe haberse detenido en la etapa de inútiles (paso de nulas, unitarias e inútiles)
        nombres_pasos = [p.nombre for p in pasos]
        self.assertIn("Eliminación de variables inútiles", nombres_pasos)
        self.assertNotIn("Convertir a Forma Normal de Chomsky", nombres_pasos)

    def test_e8_con_errores_no_inicia_proceso(self):
        datos = leer_archivo(ruta_ejemplo("e8_con_errores.txt"))
        proceso = ProcesoFNC()
        proceso.ingresar_gramatica(
            datos["variables"], datos["terminales"], datos["inicial"], datos["producciones"]
        )
        errores = proceso.validar()
        self.assertEqual(len(errores), 3)
        self.assertFalse(proceso.gramatica_es_valida())

    def test_rnf11_reproducibilidad_dos_ejecuciones(self):
        """Verifica que ejecutar el proceso dos veces sobre cada gramática produce resultados idénticos."""
        for nombre in [
            "e1_nulas_unitarias.txt",
            "e2_inutiles_inalcanzables.txt",
            "e3_inicial_anulable.txt",
            "e4_expresiones.txt",
            "e5_varias_anulables.txt",
            "e6_nombres_unicos.txt",
        ]:
            datos = leer_archivo(ruta_ejemplo(nombre))

            p1 = ProcesoFNC()
            p1.ingresar_gramatica(datos["variables"], datos["terminales"], datos["inicial"], datos["producciones"])
            p1.validar()
            p1.ejecutar_proceso_completo()

            p2 = ProcesoFNC()
            p2.ingresar_gramatica(datos["variables"], datos["terminales"], datos["inicial"], datos["producciones"])
            p2.validar()
            p2.ejecutar_proceso_completo()

            self.assertEqual(
                p1.gramatica_final().a_texto(),
                p2.gramatica_final().a_texto(),
                f"El resultado para {nombre} no fue determinista entre ejecuciones.",
            )


if __name__ == "__main__":
    unittest.main()
