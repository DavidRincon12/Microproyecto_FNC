"""Lectura del texto ingresado por el usuario y de los archivos .txt de gramáticas."""

import re
from dataclasses import dataclass

from fnc.modelo.gramatica import Cuerpo

SIMBOLOS_EPSILON = ("ε", "λ", "eps")
FLECHAS = ("->", "→")
PATRON_VARIABLE = re.compile(r"[A-Z][0-9']*")

CLAVES_ARCHIVO = {
    "VARIABLES": "variables",
    "TERMINALES": "terminales",
    "INICIAL": "inicial",
    "PRODUCCIONES": "producciones",
}


@dataclass
class ProduccionLeida:
    """Una alternativa de una línea de producciones, tal como la escribió el usuario."""

    izquierda: str
    texto_derecho: str
    cuerpo: Cuerpo
    numero_linea: int


def leer_simbolos(texto: str) -> list[str]:
    """Separa por comas y/o espacios y quita repetidos: "S, A B" -> ["S", "A", "B"]."""
    simbolos: list[str] = []
    for simbolo in re.split(r"[,\s]+", texto.strip()):
        if simbolo and simbolo not in simbolos:
            simbolos.append(simbolo)
    return simbolos


def _es_epsilon(texto: str) -> bool:
    return texto.strip() in SIMBOLOS_EPSILON


def _contiene_epsilon(texto: str) -> bool:
    """Detecta ε mezclada con otros símbolos, p. ej. "aεb" o "a eps b"."""
    return "ε" in texto or "λ" in texto or "eps" in texto.split()


def tokenizar(texto: str, declarados: list[str]) -> Cuerpo:
    """Parte el lado derecho en símbolos.

    Primero separa por espacios y luego, en cada trozo, toma siempre el símbolo
    declarado más largo que coincida. Si ninguno coincide, toma una variable no
    declarada (mayúscula seguida de dígitos o apóstrofos) o un solo carácter como
    terminal no declarado; el validador se encarga de reportarlos.
    """
    if _es_epsilon(texto):
        return ()
    ordenados = sorted(declarados, key=len, reverse=True)
    simbolos: list[str] = []
    for trozo in texto.split():
        posicion = 0
        while posicion < len(trozo):
            coincidencia = next((s for s in ordenados if trozo.startswith(s, posicion)), None)
            if coincidencia is None:
                variable = PATRON_VARIABLE.match(trozo, posicion)
                coincidencia = variable.group(0) if variable else trozo[posicion]
            simbolos.append(coincidencia)
            posicion += len(coincidencia)
    return tuple(simbolos)


def _separar_flecha(linea: str) -> tuple[str, str] | None:
    for flecha in FLECHAS:
        if flecha in linea:
            izquierda, derecha = linea.split(flecha, 1)
            return izquierda.strip(), derecha
    return None


def leer_producciones(texto: str, declarados: list[str]) -> tuple[list[ProduccionLeida], list[str]]:
    """Lee las líneas "A -> α1 | α2" y devuelve (producciones leídas, errores de estructura)."""
    producciones: list[ProduccionLeida] = []
    errores: list[str] = []
    for numero_linea, linea in enumerate(texto.splitlines(), start=1):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        partes = _separar_flecha(linea)
        if partes is None:
            errores.append(f"Error: la línea {numero_linea} ('{linea}') no tiene el símbolo '->'.")
            continue
        izquierda, derecha = partes
        for alternativa in derecha.split("|"):
            alternativa = alternativa.strip()
            if not alternativa:
                errores.append(
                    f"Error: la producción '{linea}' tiene una alternativa vacía; use ε para la cadena vacía."
                )
                continue
            if not _es_epsilon(alternativa) and _contiene_epsilon(alternativa):
                errores.append(f"Error: en la producción {izquierda} -> {alternativa}, ε debe aparecer sola.")
                continue
            cuerpo = tokenizar(alternativa, declarados)
            producciones.append(ProduccionLeida(izquierda, alternativa, cuerpo, numero_linea))
    return producciones, errores


def leer_archivo(ruta: str) -> dict[str, str]:
    """Lee un .txt con las secciones VARIABLES, TERMINALES, INICIAL y PRODUCCIONES."""
    with open(ruta, encoding="utf-8-sig") as archivo:
        lineas = archivo.read().splitlines()

    datos: dict[str, str] = {}
    lineas_producciones: list[str] = []
    en_producciones = False
    for linea in lineas:
        limpia = linea.strip()
        clave, _, valor = limpia.partition(":")
        clave = clave.strip().upper()
        if clave in CLAVES_ARCHIVO and not limpia.startswith("#"):
            en_producciones = clave == "PRODUCCIONES"
            datos[CLAVES_ARCHIVO[clave]] = valor.strip()
            if en_producciones and valor.strip():
                lineas_producciones.append(valor.strip())
        elif en_producciones:
            lineas_producciones.append(linea)

    faltantes = [nombre for nombre, clave in CLAVES_ARCHIVO.items() if clave not in datos]
    if faltantes:
        raise ValueError(
            "El archivo no tiene el formato esperado; faltan las secciones: " + ", ".join(faltantes) + "."
        )
    datos["producciones"] = "\n".join(lineas_producciones).strip()
    return datos


def guardar_archivo(ruta: str, datos: dict[str, str]) -> None:
    """Guarda la gramática en el mismo formato que lee leer_archivo."""
    contenido = (
        f"VARIABLES: {datos.get('variables', '').strip()}\n"
        f"TERMINALES: {datos.get('terminales', '').strip()}\n"
        f"INICIAL: {datos.get('inicial', '').strip()}\n"
        "PRODUCCIONES:\n"
        f"{datos.get('producciones', '').strip()}\n"
    )
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(contenido)
