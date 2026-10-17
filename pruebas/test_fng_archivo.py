import os
import tempfile
import unittest

from fng.archivo import guardar_archivo_fng, leer_archivo_fng

DATOS = {
    "variables": "S, A",
    "terminales": "a, b",
    "inicial": "S",
    "producciones": "S -> A S | a\nA -> b",
}


class PruebasArchivoFNG(unittest.TestCase):
    def setUp(self):
        carpeta = tempfile.mkdtemp()
        self.ruta = os.path.join(carpeta, "gramatica.txt")

    def escribir(self, contenido: str) -> None:
        with open(self.ruta, "w", encoding="utf-8") as archivo:
            archivo.write(contenido)

    def test_guardar_y_leer_con_orden(self):
        guardar_archivo_fng(self.ruta, {**DATOS, "orden": "A, S"})
        self.assertEqual(leer_archivo_fng(self.ruta), {**DATOS, "orden": "A, S"})

    def test_sin_orden_no_escribe_la_linea(self):
        guardar_archivo_fng(self.ruta, DATOS)
        with open(self.ruta, encoding="utf-8") as archivo:
            self.assertNotIn("ORDEN", archivo.read())
        self.assertEqual(leer_archivo_fng(self.ruta)["orden"], "")

    def test_orden_despues_de_producciones_no_es_produccion(self):
        self.escribir("VARIABLES: S\nTERMINALES: a\nINICIAL: S\nPRODUCCIONES:\nS -> a\norden: S\n")
        datos = leer_archivo_fng(self.ruta)
        self.assertEqual(datos["producciones"], "S -> a")
        self.assertEqual(datos["orden"], "S")


if __name__ == "__main__":
    unittest.main()
