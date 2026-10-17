"""Archivos de gramática del Microproyecto 2.

Es el mismo formato del Microproyecto 1 con una línea opcional "ORDEN: S, A, B" para
el orden de las variables. Se escribe antes de PRODUCCIONES; si aparece después, se
reconoce igual y no se toma como producción.
"""

from fnc.entrada.lector import leer_archivo

CLAVE_ORDEN = "ORDEN"


def _es_linea_orden(linea: str) -> bool:
    clave, separador, _ = linea.strip().partition(":")
    return bool(separador) and clave.strip().upper() == CLAVE_ORDEN


def leer_archivo_fng(ruta: str) -> dict[str, str]:
    """Como leer_archivo del Microproyecto 1, más la clave "orden" ("" si no hay línea ORDEN)."""
    datos = leer_archivo(ruta)
    with open(ruta, encoding="utf-8-sig") as archivo:
        lineas_orden = [linea for linea in archivo.read().splitlines() if _es_linea_orden(linea)]
    datos["orden"] = lineas_orden[-1].partition(":")[2].strip() if lineas_orden else ""
    datos["producciones"] = "\n".join(
        linea for linea in datos["producciones"].splitlines() if not _es_linea_orden(linea)
    ).strip()
    return datos


def guardar_archivo_fng(ruta: str, datos: dict[str, str]) -> None:
    """Guarda la gramática en el formato que lee leer_archivo_fng (ORDEN solo si se indicó)."""
    orden = datos.get("orden", "").strip()
    contenido = (
        f"VARIABLES: {datos.get('variables', '').strip()}\n"
        f"TERMINALES: {datos.get('terminales', '').strip()}\n"
        f"INICIAL: {datos.get('inicial', '').strip()}\n"
        + (f"{CLAVE_ORDEN}: {orden}\n" if orden else "")
        + "PRODUCCIONES:\n"
        f"{datos.get('producciones', '').strip()}\n"
    )
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(contenido)
