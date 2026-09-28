"""Representación de una Gramática Libre de Contexto G = (V, T, P, S)."""

EPSILON = "ε"  # solo para mostrar; internamente ε es la tupla vacía ()

Cuerpo = tuple[str, ...]
Produccion = tuple[str, Cuerpo]


def _clave_orden(cuerpo: Cuerpo) -> tuple[int, Cuerpo]:
    """Orden canónico de los cuerpos: primero por longitud y luego alfabético."""
    return (len(cuerpo), cuerpo)


def _sin_repetidos(simbolos: list[str]) -> list[str]:
    """Quita repetidos conservando el orden en que se declararon."""
    resultado: list[str] = []
    for simbolo in simbolos:
        if simbolo not in resultado:
            resultado.append(simbolo)
    return resultado


class Gramatica:
    """Gramática libre de contexto.

    Las producciones se guardan como un diccionario variable -> conjunto de cuerpos.
    Al usar conjuntos no pueden existir producciones duplicadas (RNF08). Cada vez que
    el orden importa (mostrar la gramática o recorrerla en un algoritmo) se usa el
    orden canónico, para que una misma gramática produzca siempre el mismo resultado (RNF11).
    """

    def __init__(self, variables: list[str], terminales: list[str], simbolo_inicial: str) -> None:
        self.variables: list[str] = _sin_repetidos(variables)
        self.terminales: list[str] = _sin_repetidos(terminales)
        self.simbolo_inicial: str = simbolo_inicial
        self.producciones: dict[str, set[Cuerpo]] = {variable: set() for variable in self.variables}

    # ------------------------------------------------------------------ consultas

    def es_variable(self, simbolo: str) -> bool:
        return simbolo in self.producciones

    def es_terminal(self, simbolo: str) -> bool:
        return simbolo in self.terminales

    def variables_en_orden(self) -> list[str]:
        """El símbolo inicial primero y luego el resto en el orden de declaración."""
        resto = [variable for variable in self.variables if variable != self.simbolo_inicial]
        if self.simbolo_inicial in self.producciones:
            return [self.simbolo_inicial] + resto
        return resto

    def cuerpos_de(self, variable: str) -> list[Cuerpo]:
        """Cuerpos de la variable en orden canónico (longitud y luego alfabético)."""
        return sorted(self.producciones.get(variable, set()), key=_clave_orden)

    def lista_producciones(self) -> list[Produccion]:
        """Todas las producciones en orden canónico."""
        return [
            (variable, cuerpo)
            for variable in self.variables_en_orden()
            for cuerpo in self.cuerpos_de(variable)
        ]

    def cantidad_producciones(self) -> int:
        return sum(len(cuerpos) for cuerpos in self.producciones.values())

    # ------------------------------------------------------------ modificaciones

    def agregar_variable(self, variable: str) -> None:
        """Agrega la variable al final de la lista si todavía no existe."""
        if variable not in self.producciones:
            self.variables.append(variable)
            self.producciones[variable] = set()

    def definir_simbolo_inicial(self, variable: str) -> None:
        self.agregar_variable(variable)
        self.simbolo_inicial = variable

    def agregar_produccion(self, variable: str, cuerpo: Cuerpo) -> bool:
        """Agrega variable -> cuerpo. Devuelve False si la producción ya existía."""
        if variable not in self.producciones:
            raise ValueError(f"La variable {variable} no pertenece a la gramática.")
        cuerpo = tuple(cuerpo)
        if cuerpo in self.producciones[variable]:
            return False
        self.producciones[variable].add(cuerpo)
        return True

    def eliminar_produccion(self, variable: str, cuerpo: Cuerpo) -> bool:
        """Quita variable -> cuerpo. Devuelve False si la producción no existía."""
        cuerpos = self.producciones.get(variable)
        cuerpo = tuple(cuerpo)
        if cuerpos is None or cuerpo not in cuerpos:
            return False
        cuerpos.remove(cuerpo)
        return True

    def eliminar_variable(self, variable: str) -> list[Produccion]:
        """Quita la variable, sus producciones y toda producción que la use a la derecha.

        Devuelve las producciones eliminadas en orden canónico.
        """
        if variable not in self.producciones:
            return []
        eliminadas = [
            (izquierda, cuerpo)
            for izquierda, cuerpo in self.lista_producciones()
            if izquierda == variable or variable in cuerpo
        ]
        for izquierda, cuerpo in eliminadas:
            self.producciones[izquierda].discard(cuerpo)
        del self.producciones[variable]
        self.variables.remove(variable)
        return eliminadas

    def eliminar_terminal(self, terminal: str) -> None:
        if terminal in self.terminales:
            self.terminales.remove(terminal)

    def copiar(self) -> "Gramatica":
        """Copia independiente: modificar la copia no afecta a la original."""
        copia = Gramatica(self.variables, self.terminales, self.simbolo_inicial)
        copia.producciones = {variable: set(cuerpos) for variable, cuerpos in self.producciones.items()}
        return copia

    # --------------------------------------------------------------- presentación

    @staticmethod
    def cuerpo_a_texto(cuerpo: Cuerpo) -> str:
        """("a", "S", "b") -> "a S b";  () -> "ε"."""
        return " ".join(cuerpo) if cuerpo else EPSILON

    @staticmethod
    def produccion_a_texto(variable: str, cuerpo: Cuerpo) -> str:
        return f"{variable} -> {Gramatica.cuerpo_a_texto(cuerpo)}"

    def lineas_producciones(self) -> list[str]:
        """Una línea por variable con producciones, p. ej. "S -> a | A B"."""
        lineas = []
        for variable in self.variables_en_orden():
            cuerpos = self.cuerpos_de(variable)
            if cuerpos:
                alternativas = " | ".join(self.cuerpo_a_texto(cuerpo) for cuerpo in cuerpos)
                lineas.append(f"{variable} -> {alternativas}")
        return lineas

    def a_texto(self) -> str:
        """Gramática completa G = (V, T, P, S) lista para mostrar."""
        lineas = [
            "V = {" + ", ".join(self.variables_en_orden()) + "}",
            "T = {" + ", ".join(self.terminales) + "}",
            f"Inicial = {self.simbolo_inicial}",
            "P:",
        ]
        lineas += ["  " + linea for linea in self.lineas_producciones()]
        return "\n".join(lineas)

    def __str__(self) -> str:
        return self.a_texto()
