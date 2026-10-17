# Aplicativo para Depuración y Conversión de Gramáticas Libres de Contexto a Forma Normal de Chomsky

Microproyecto #1 — Teoría de la Computación (2026-II)  
Universidad Francisco de Paula Santander (UFPS)

> Este repositorio contiene los dos microproyectos de la materia. El **Microproyecto 2** (conversión a Forma Normal de Greibach) reutiliza el modelo y los algoritmos del Microproyecto 1; está descrito en la [sección 5](#5-microproyecto-2-conversión-a-forma-normal-de-greibach).

---

## 1. Descripción General

Este aplicativo permite ingresar, validar, depurar y transformar una Gramática Libre de Contexto (GLC) en una gramática equivalente expresada en **Forma Normal de Chomsky (FNC)**.

El sistema presenta al usuario de manera secuencial y detallada cada una de las transformaciones realizadas:
1. **Validación inicial:** comprobación formal de variables, terminales, símbolo inicial y producciones.
2. **Eliminación de producciones nulas ($A \to \varepsilon$):** cálculo de variables anulables por punto fijo y tratamiento especial de $\varepsilon$ si el inicial es anulable ($S_0 \to S \mid \varepsilon$).
3. **Eliminación de producciones unitarias ($A \to B$):** cálculo de cadenas y pares unitarios.
4. **Eliminación de variables inútiles:** cálculo de variables generadoras y detección de lenguaje vacío.
5. **Eliminación de variables inalcanzables:** recorrido en anchura (BFS) desde el símbolo inicial y depuración de terminales sin uso.
6. **Conversión a FNC:**
   - Sustitución de símbolos terminales en producciones de longitud $\ge 2$ mediante variables auxiliares ($X_n \to a$).
   - Reducción de producciones largas ($\ge 3$ símbolos) a pares binarios reutilizando sufijos auxiliares.
   - Validación automática de la gramática final contra las reglas de la Forma Normal de Chomsky.

---

## 2. Requisitos de Ejecución

* **Python 3.11 o superior** (incluyendo el módulo `tkinter`).
* En Windows, se puede ejecutar directamente desde la terminal o mediante el ejecutable compilado.

---

## 3. Instrucciones de Uso

### 3.1 Ejecutar desde el código fuente

Abrir una terminal en el directorio raíz del proyecto y ejecutar:

```bash
# En Windows:
python main.py
# o bien:
py main.py

# En Linux / macOS:
python3 main.py
```

### 3.2 Ejecutar las pruebas unitarias

El proyecto cuenta con una suite completa de pruebas unitarias automatizadas:

```bash
python -m unittest discover -s pruebas -v
```

### 3.3 Generar el ejecutable independiente (.exe)

Para generar `dist/DepuradorFNC.exe` (que funciona en cualquier PC con Windows sin necesidad de instalar Python):

1. Ejecutar el script por lotes:
   ```cmd
   construir_exe.bat
   ```
2. El archivo `.exe` resultante quedará disponible en la carpeta `dist/`.

---

## 4. Estructura del Código

```text
Microproyecto_FNC/
├── main.py                         Punto de entrada de la aplicación
├── README.md                       Documentación técnica y de uso
├── construir_exe.bat               Script de generación del ejecutable
├── ejemplos/                       Gramáticas de prueba canónicas (E1 a E8)
│   ├── e1_nulas_unitarias.txt
│   ├── e2_inutiles_inalcanzables.txt
│   ├── e3_inicial_anulable.txt
│   ├── e4_expresiones.txt
│   ├── e5_varias_anulables.txt
│   ├── e6_nombres_unicos.txt
│   ├── e7_lenguaje_vacio.txt
│   └── e8_con_errores.txt
├── fnc/
│   ├── modelo/                     Modelo de datos (Gramatica, Paso, Historial)
│   ├── entrada/                    Lector de cadenas y archivos .txt
│   ├── validacion/                 Validador inicial y validador de FNC
│   ├── algoritmos/                 Algoritmos de depuración y transformación
│   │   ├── nulas.py
│   │   ├── unitarias.py
│   │   ├── inutiles.py
│   │   ├── inalcanzables.py
│   │   └── chomsky.py
│   ├── proceso.py                  Controlador del flujo y etapas (ProcesoFNC)
│   └── interfaz/                   Interfaz gráfica de usuario con Tkinter
│       └── ventana_principal.py
└── pruebas/                        Suite de pruebas unitarias (unittest)
```

---

## 5. Microproyecto 2: Conversión a Forma Normal de Greibach

### 5.1 Descripción

El segundo aplicativo recibe una gramática en **Forma Normal de Chomsky (FNC)** y la transforma en una gramática equivalente en **Forma Normal de Greibach (FNG)**, donde toda producción tiene la forma $A \to a\,B_1 B_2 \dots B_k$ ($k \ge 0$): un terminal seguido únicamente de variables. Se admite $S \to \varepsilon$ solo para el símbolo inicial.

Se sigue el algoritmo clásico de Hopcroft y Ullman y cada etapa se muestra como un paso del historial (gramática antes y después, elementos identificados, producciones eliminadas y agregadas):

1. **Validación de la gramática:** misma política del Microproyecto 1. Solo detienen el proceso los errores de escritura; las producciones con símbolos no declarados se descartan con una advertencia.
2. **Validación de la FNC:** cada producción fuera de la FNC es un error. La aplicación ofrece **«Convertir primero a FNC»**, que aplica el Microproyecto 1 a la gramática ingresada.
3. **Depuración previa:** eliminación de variables inútiles e inalcanzables (algoritmos del Microproyecto 1).
4. **Ordenamiento de variables** $A_1, A_2, \dots, A_n$: por defecto el inicial primero y luego el orden de declaración; el usuario puede indicar otro. Si el inicial tiene $S \to \varepsilon$, esa producción se aparta y se reincorpora al final.
5. **Fase 1, hacia adelante:** para cada $A_i$ se sustituyen las producciones $A_i \to A_j\gamma$ con $j < i$, y luego se elimina la recursividad izquierda directa ($A \to A\alpha$) creando una variable auxiliar $A'$.
6. **Fase 2, sustitución regresiva:** desde $A_{n-1}$ hasta $A_1$, toda producción que empieza con una variable se sustituye hasta empezar con un terminal.
7. **Fase 3, variables auxiliares:** las producciones de las variables auxiliares se llevan a la misma forma.
8. **Verificación, limpieza final y validación de la FNG:** se comprueba que después del terminal solo haya variables, se eliminan las variables que quedaron inalcanzables y se valida el resultado.

### 5.2 Formato de entrada

Es el mismo del Microproyecto 1 (campos o archivo `.txt`), con un campo **opcional** adicional, «Orden de las variables», que es una lista separada por comas (por ejemplo `C, B, A, S`). Las variables que no se escriban se agregan al final en el orden por defecto, y las que no existan se ignoran con una advertencia. En los archivos, el orden va en una línea `ORDEN:` antes de `PRODUCCIONES`.

```text
# G8: G1 con orden personalizado
VARIABLES: S, A, B, C
TERMINALES: a, b, c
INICIAL: S
ORDEN: C, B, A, S
PRODUCCIONES:
S -> AB | b
A -> BC | a
B -> SA | b
C -> AS | c
```

Si la gramática no está en FNC, al validarla la aplicación pregunta si se desea convertir primero con el Microproyecto 1.

### 5.3 Ejecución

```bash
# Aplicación del Microproyecto 2
python main_fng.py          # Windows: py main_fng.py
python3 main_fng.py         # Linux / macOS

# Ejecutable para Windows (genera dist/ConversorFNG.exe)
construir_exe_fng.bat

# Pruebas de los dos microproyectos
python -m unittest discover -s pruebas -v
```

El Microproyecto 1 se sigue ejecutando igual (`python main.py`, `dist/DepuradorFNC.exe`).

### 5.4 Gramáticas de ejemplo (`ejemplos_fng/`)

| Archivo | Qué ilustra |
|---|---|
| `g1_sustituciones_recursividad.txt` | Recursividad izquierda indirecta: sustituciones sucesivas $B \to SA \to ABA \to BCBA$ |
| `g2_sustitucion_regresiva.txt` | Cinco variables sin recursividad: la fase 2 hace casi todo el trabajo |
| `g3_recursividad_directa.txt` | Recursividad izquierda directa en las tres variables (tres variables auxiliares) |
| `g4_con_epsilon.txt` | Gramática general con $\varepsilon$ ($S \to aSb \mid bSa \mid SS \mid \varepsilon$); pasa antes por el Microproyecto 1 |
| `g5_expresiones.txt` | Expresiones con suma, resta, producto, paréntesis y signo negativo; pasa antes por el Microproyecto 1 |
| `g6_no_fnc.txt` | Gramática general con símbolos no declarados ($B$, $Q$), $\varepsilon$, unitarias y variables inútiles |
| `g7_variables_inutiles.txt` | Variables inútiles e inalcanzables y símbolos no declarados en la depuración previa |
| `g8_orden_personalizado.txt` | G1 con el orden `C, B, A, S`: otra gramática resultante con el mismo lenguaje |

### 5.5 Verificación de la equivalencia

Las pruebas comprueban que la gramática final genera exactamente las mismas cadenas que la de entrada hasta una longitud dada (`pruebas/utilidades_pruebas_fng.py`):

- Para la gramática en FNC, las cadenas se calculan con la programación dinámica del algoritmo CYK.
- Para la gramática en FNG, se usan derivaciones por la izquierda. Cada paso agrega exactamente un terminal, así que la búsqueda siempre termina.

### 5.6 Estructura del código

```text
├── main_fng.py                     Punto de entrada del Microproyecto 2
├── construir_exe_fng.bat           Script de generación de ConversorFNG.exe
├── ejemplos_fng/                   Gramáticas de prueba G1 a G8
├── fng/
│   ├── archivo.py                  Lectura y guardado de archivos (con la línea ORDEN)
│   ├── utilidades.py               Sustitución de la primera variable y armado de pasos
│   ├── validacion/
│   │   ├── entrada.py              Validación de la entrada (escritura, símbolos y FNC)
│   │   └── greibach.py             Validación de la Forma Normal de Greibach
│   ├── algoritmos/
│   │   ├── orden.py                Ordenamiento de variables y ε del inicial
│   │   ├── sustitucion.py          Fase 1: sustituciones hacia adelante
│   │   ├── recursividad.py         Fase 1: eliminación de recursividad izquierda
│   │   └── terminales.py           Fases 2 y 3 y verificación
│   ├── proceso_fng.py              Controlador del flujo (ProcesoFNG)
│   └── interfaz/
│       └── ventana_fng.py          Interfaz gráfica con Tkinter
└── pruebas/test_fng_*.py           Pruebas del Microproyecto 2
```
