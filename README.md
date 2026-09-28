# Aplicativo para Depuración y Conversión de Gramáticas Libres de Contexto a Forma Normal de Chomsky

Microproyecto #1 — Teoría de la Computación (2026-II)  
Universidad Francisco de Paula Santander (UFPS)

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
