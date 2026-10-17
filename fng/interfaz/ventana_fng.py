"""Interfaz gráfica del aplicativo de Conversión a Forma Normal de Greibach (RNF01, RF19, RF20, sección 7.12)."""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from fnc.entrada.lector import leer_simbolos
from fng.archivo import guardar_archivo_fng, leer_archivo_fng
from fng.proceso_fng import ErrorProcesoFNG, ProcesoFNG

CARPETA_EJEMPLOS = "ejemplos_fng"


def ruta_recurso(relativa: str) -> str:
    """Obtiene la ruta absoluta para recursos, compatible con PyInstaller y ejecución directa."""
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, relativa)


def listar_ejemplos() -> dict[str, str]:
    """{"G1 · descripción": ruta} con los .txt de ejemplos_fng, tomando la descripción de su primera línea."""
    carpeta = ruta_recurso(CARPETA_EJEMPLOS)
    if not os.path.isdir(carpeta):
        return {}
    ejemplos: dict[str, str] = {}
    for nombre in sorted(os.listdir(carpeta)):
        if not nombre.endswith(".txt"):
            continue
        ruta = os.path.join(carpeta, nombre)
        with open(ruta, encoding="utf-8-sig") as archivo:
            primera = archivo.readline().strip()
        clave, _, descripcion = primera.lstrip("# ").partition(":")
        if not descripcion:
            clave, descripcion = nombre[:2].upper(), nombre[3:-4].replace("_", " ")
        ejemplos[f"{clave.strip()} · {descripcion.strip()}"] = ruta
    return ejemplos


class VentanaFNG(tk.Tk):
    """Ventana principal del aplicativo de Conversión de FNC a FNG."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Conversión de FNC a Forma Normal de Greibach")
        self.minsize(1050, 700)
        self.geometry("1120x740")

        self.proceso = ProcesoFNG()

        self._configurar_estilos()
        self._crear_paneles_principales()
        self._crear_panel_entrada()
        self._crear_panel_acciones()
        self._crear_panel_visualizacion()
        self._crear_barra_estado()

        self._actualizar_estado_botones()

    def _configurar_estilos(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TLabel", font=("Segoe UI", 9))
        style.configure("TButton", font=("Segoe UI", 9))
        style.configure("Accion.TButton", font=("Segoe UI", 9))
        style.configure("Destacado.TButton", font=("Segoe UI", 9, "bold"))
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("Estado.TLabel", font=("Segoe UI", 9))

    def _crear_paneles_principales(self) -> None:
        self.contenedor_principal = ttk.Frame(self, padding=8)
        self.contenedor_principal.pack(fill=tk.BOTH, expand=True)

        self.frame_izquierdo = ttk.Frame(self.contenedor_principal, width=430)
        self.frame_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 6))

        self.frame_derecho = ttk.Frame(self.contenedor_principal)
        self.frame_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def _crear_panel_entrada(self) -> None:
        grupo_entrada = ttk.LabelFrame(self.frame_izquierdo, text="Gramática de entrada (FNC)", padding=10)
        grupo_entrada.pack(fill=tk.X, pady=(0, 6))

        # Variables
        ttk.Label(grupo_entrada, text="Variables (no terminales):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.var_variables = tk.StringVar()
        self.var_variables.trace_add("write", self._al_cambiar_variables)
        self.entry_variables = ttk.Entry(grupo_entrada, textvariable=self.var_variables)
        self.entry_variables.grid(row=0, column=1, sticky=tk.EW, pady=2, padx=(4, 0))

        # Terminales
        ttk.Label(grupo_entrada, text="Terminales:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.var_terminales = tk.StringVar()
        self.entry_terminales = ttk.Entry(grupo_entrada, textvariable=self.var_terminales)
        self.entry_terminales.grid(row=1, column=1, sticky=tk.EW, pady=2, padx=(4, 0))

        # Símbolo inicial
        ttk.Label(grupo_entrada, text="Símbolo inicial:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.var_inicial = tk.StringVar()
        self.combo_inicial = ttk.Combobox(grupo_entrada, textvariable=self.var_inicial, state="readonly", width=10)
        self.combo_inicial.grid(row=2, column=1, sticky=tk.W, pady=2, padx=(4, 0))

        # Orden de variables (opcional)
        ttk.Label(grupo_entrada, text="Orden de variables (opcional):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.var_orden = tk.StringVar()
        self.entry_orden = ttk.Entry(grupo_entrada, textvariable=self.var_orden)
        self.entry_orden.grid(row=3, column=1, sticky=tk.EW, pady=2, padx=(4, 0))

        ttk.Label(
            grupo_entrada,
            text="Ej.: S, A, B  (vacío = orden de declaración)",
            font=("Segoe UI", 8, "italic"),
            foreground="#555555",
        ).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))

        # Producciones
        ttk.Label(grupo_entrada, text="Reglas de producción:").grid(row=5, column=0, sticky=tk.NW, pady=(4, 2))
        self.texto_producciones = ScrolledText(grupo_entrada, width=32, height=6, font=("Consolas", 10))
        self.texto_producciones.grid(row=6, column=0, columnspan=2, sticky=tk.EW, pady=(0, 4))

        # Botones de utilidad
        frame_utilidades = ttk.Frame(grupo_entrada)
        frame_utilidades.grid(row=7, column=0, columnspan=2, sticky=tk.EW)

        btn_epsilon = ttk.Button(frame_utilidades, text="Insertar ε", command=self._insertar_epsilon, width=10)
        btn_epsilon.pack(side=tk.LEFT, padx=(0, 4))

        btn_abrir = ttk.Button(frame_utilidades, text="Abrir...", command=self._abrir_archivo, width=9)
        btn_abrir.pack(side=tk.LEFT, padx=2)

        btn_guardar = ttk.Button(frame_utilidades, text="Guardar...", command=self._guardar_archivo, width=9)
        btn_guardar.pack(side=tk.LEFT, padx=2)

        frame_ejemplos = ttk.Frame(grupo_entrada)
        frame_ejemplos.grid(row=8, column=0, columnspan=2, sticky=tk.EW, pady=(6, 0))
        ttk.Label(frame_ejemplos, text="Ejemplo:").pack(side=tk.LEFT, padx=(0, 4))
        self.ejemplos = listar_ejemplos()
        self.combo_ejemplos = ttk.Combobox(
            frame_ejemplos,
            values=list(self.ejemplos),
            state="readonly",
        )
        self.combo_ejemplos.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.combo_ejemplos.bind("<<ComboboxSelected>>", self._cargar_ejemplo_seleccionado)

        grupo_entrada.columnconfigure(1, weight=1)

    def _crear_panel_acciones(self) -> None:
        grupo_acciones = ttk.LabelFrame(self.frame_izquierdo, text="Acciones del proceso", padding=10)
        grupo_acciones.pack(fill=tk.BOTH, expand=True)

        frame_top = ttk.Frame(grupo_acciones)
        frame_top.pack(fill=tk.X, pady=(0, 4))

        self.btn_registrar = ttk.Button(
            frame_top,
            text="1. Registrar gramática",
            command=self._accion_registrar,
            style="Accion.TButton",
        )
        self.btn_registrar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        self.btn_validar = ttk.Button(
            frame_top,
            text="2. Validar FNC",
            command=self._accion_validar,
            style="Destacado.TButton",
        )
        self.btn_validar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

        # Botón para convertir primero a FNC si la gramática no cumple
        self.btn_convertir_fnc = ttk.Button(
            grupo_acciones,
            text="⚡ Convertir primero a FNC",
            command=self._accion_convertir_primero_a_fnc,
        )
        self.btn_convertir_fnc.pack(fill=tk.X, pady=(2, 6))

        # Modos de ejecución
        ttk.Separator(grupo_acciones, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=4)

        self.btn_siguiente = ttk.Button(
            grupo_acciones,
            text="3. Siguiente paso ▶",
            command=self._accion_siguiente_paso,
            style="Destacado.TButton",
        )
        self.btn_siguiente.pack(fill=tk.X, pady=3)

        self.btn_automatico = ttk.Button(
            grupo_acciones,
            text="4. Conversión automática",
            command=self._accion_automatico,
            style="Destacado.TButton",
        )
        self.btn_automatico.pack(fill=tk.X, pady=3)

        # Información de avance
        self.lbl_pasos_ejecutados = ttk.Label(
            grupo_acciones,
            text="Pasos ejecutados: 0",
            font=("Segoe UI", 9, "bold"),
            foreground="#333333",
        )
        self.lbl_pasos_ejecutados.pack(anchor=tk.W, pady=(6, 2))

        self.lbl_orden_actual = ttk.Label(
            grupo_acciones,
            text="Orden: (se define al ordenar)",
            font=("Segoe UI", 8, "italic"),
            foreground="#0055AA",
        )
        self.lbl_orden_actual.pack(anchor=tk.W, pady=(0, 6))

        # Botones secundarios
        ttk.Separator(grupo_acciones, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=4)

        frame_inferior = ttk.Frame(grupo_acciones)
        frame_inferior.pack(fill=tk.X, pady=(4, 0))

        self.btn_original = ttk.Button(
            frame_inferior,
            text="Gramática original",
            command=self._accion_mostrar_original,
            width=18,
        )
        self.btn_original.grid(row=0, column=0, padx=2, pady=2, sticky=tk.EW)

        self.btn_reiniciar = ttk.Button(
            frame_inferior,
            text="Nueva gramática",
            command=self._accion_nueva_gramatica,
            width=18,
        )
        self.btn_reiniciar.grid(row=0, column=1, padx=2, pady=2, sticky=tk.EW)

        self.btn_salir = ttk.Button(
            frame_inferior,
            text="Salir",
            command=self._accion_salir,
            width=18,
        )
        self.btn_salir.grid(row=1, column=0, columnspan=2, padx=2, pady=4, sticky=tk.EW)

        frame_inferior.columnconfigure(0, weight=1)
        frame_inferior.columnconfigure(1, weight=1)

    def _crear_panel_visualizacion(self) -> None:
        self.notebook = ttk.Notebook(self.frame_derecho)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_paso = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_paso, text="Paso actual")
        self.texto_paso = self._crear_area_texto(self.tab_paso)

        self.tab_historial = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_historial, text="Historial completo")
        self.texto_historial = self._crear_area_texto(self.tab_historial)

        self.tab_final = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_final, text="Gramática final (FNG)")
        self.texto_final = self._crear_area_texto(self.tab_final)

    def _crear_area_texto(self, contenedor: ttk.Frame) -> ScrolledText:
        area = ScrolledText(
            contenedor,
            wrap=tk.WORD,
            font=("Consolas", 10),
            padx=10,
            pady=10,
            background="#FFFFFF",
        )
        area.pack(fill=tk.BOTH, expand=True)

        area.tag_configure("titulo", font=("Consolas", 11, "bold"), foreground="#003366")
        area.tag_configure("subtitulo", font=("Consolas", 10, "bold"), foreground="#222222")
        area.tag_configure("eliminada", foreground="#B00020", font=("Consolas", 10, "bold"))
        area.tag_configure("agregada", foreground="#1B5E20", font=("Consolas", 10, "bold"))
        area.tag_configure("observacion", foreground="#424242", font=("Consolas", 10, "italic"))
        area.tag_configure("error", foreground="#C62828", font=("Consolas", 10, "bold"))
        area.tag_configure("exito", foreground="#2E7D32", font=("Consolas", 10, "bold"))
        area.config(state=tk.DISABLED)
        return area

    def _crear_barra_estado(self) -> None:
        frame_estado = ttk.Frame(self, relief=tk.SUNKEN, padding=(6, 3))
        frame_estado.pack(side=tk.BOTTOM, fill=tk.X)
        self.lbl_estado = ttk.Label(
            frame_estado,
            text="Listo. Ingrese una gramática en FNC o seleccione un ejemplo.",
            style="Estado.TLabel",
        )
        self.lbl_estado.pack(side=tk.LEFT)

    # ------------------------------------------------------------- Lógica de interfaz

    def _actualizar_texto(self, area: ScrolledText, texto: str) -> None:
        area.config(state=tk.NORMAL)
        area.delete("1.0", tk.END)

        for linea in texto.split("\n"):
            linea_con_salto = linea + "\n"
            if linea.startswith("===") or linea.startswith("Paso ") or "Forma Normal" in linea:
                area.insert(tk.END, linea_con_salto, "titulo")
            elif linea.endswith(":") and not linea.startswith(" "):
                area.insert(tk.END, linea_con_salto, "subtitulo")
            elif linea.strip().startswith("- "):
                area.insert(tk.END, linea_con_salto, "eliminada")
            elif linea.strip().startswith("+ "):
                area.insert(tk.END, linea_con_salto, "agregada")
            elif "Observaciones:" in linea or linea.startswith("  * ") or "lenguaje es vacío" in linea:
                area.insert(tk.END, linea_con_salto, "observacion")
            elif "Error:" in linea or "errores" in linea.lower():
                area.insert(tk.END, linea_con_salto, "error")
            elif "cumple la FNG" in linea or "válida" in linea or "cumple la FNC" in linea:
                area.insert(tk.END, linea_con_salto, "exito")
            else:
                area.insert(tk.END, linea_con_salto)

        area.config(state=tk.DISABLED)

    def _al_cambiar_variables(self, *_) -> None:
        texto = self.var_variables.get()
        simbolos = [s for s in leer_simbolos(texto) if s and s[0].isupper()]
        actual = self.var_inicial.get()
        self.combo_inicial["values"] = simbolos
        if actual not in simbolos and simbolos:
            self.var_inicial.set(simbolos[0])

    def _insertar_epsilon(self) -> None:
        self.texto_producciones.insert(tk.INSERT, "ε")
        self.texto_producciones.focus_set()

    def _cargar_ejemplo_seleccionado(self, *_) -> None:
        seleccion = self.combo_ejemplos.get()
        ruta = self.ejemplos.get(seleccion)
        if not ruta:
            return
        if not os.path.exists(ruta):
            messagebox.showwarning("Archivo no encontrado", f"No se encontró: {ruta}")
            return
        try:
            self._cargar_datos_en_formulario(leer_archivo_fng(ruta))
            self.lbl_estado.config(text=f"Ejemplo {seleccion.split(' · ')[0]} cargado.")
        except Exception as e:
            messagebox.showerror("Error al cargar", f"No se pudo cargar el ejemplo: {e}")

    def _abrir_archivo(self) -> None:
        ruta = filedialog.askopenfilename(
            title="Abrir gramática FNC",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
        )
        if not ruta:
            return
        try:
            datos = leer_archivo_fng(ruta)
            self._cargar_datos_en_formulario(datos)
            self.lbl_estado.config(text=f"Archivo '{os.path.basename(ruta)}' cargado.")
        except Exception as e:
            messagebox.showerror("Error de lectura", f"No se pudo leer el archivo: {e}")

    def _guardar_archivo(self) -> None:
        ruta = filedialog.asksaveasfilename(
            title="Guardar gramática",
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt")],
        )
        if not ruta:
            return
        datos = {
            "variables": self.var_variables.get().strip(),
            "terminales": self.var_terminales.get().strip(),
            "inicial": self.var_inicial.get().strip(),
            "producciones": self.texto_producciones.get("1.0", tk.END).strip(),
            "orden": self.var_orden.get().strip(),
        }
        try:
            guardar_archivo_fng(ruta, datos)
            messagebox.showinfo("Guardado", f"Guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def _cargar_datos_en_formulario(self, datos: dict[str, str]) -> None:
        self.var_variables.set(datos.get("variables", ""))
        self.var_terminales.set(datos.get("terminales", ""))
        self._al_cambiar_variables()
        self.var_inicial.set(datos.get("inicial", ""))
        self.var_orden.set(datos.get("orden", ""))
        self.texto_producciones.delete("1.0", tk.END)
        self.texto_producciones.insert("1.0", datos.get("producciones", ""))
        self.proceso.reiniciar()
        self._actualizar_estado_botones()

    def _actualizar_estado_botones(self) -> None:
        valida = self.proceso.gramatica_es_valida()
        hay_sig = self.proceso.hay_siguiente_paso()

        self.btn_siguiente.config(state=tk.NORMAL if (valida and hay_sig) else tk.DISABLED)
        self.btn_automatico.config(state=tk.NORMAL if (valida and hay_sig) else tk.DISABLED)

        # Botón para convertir primero a FNC
        if self.proceso.errores_son_de_fnc():
            self.btn_convertir_fnc.config(state=tk.NORMAL)
        else:
            self.btn_convertir_fnc.config(state=tk.DISABLED)

        n_pasos = len(self.proceso.historial().pasos)
        self.lbl_pasos_ejecutados.config(text=f"Pasos ejecutados: {n_pasos}")

        orden = self.proceso.orden_variables()
        if orden:
            texto_orden = ", ".join(f"A{i+1}={v}" for i, v in enumerate(orden))
            self.lbl_orden_actual.config(text=f"Orden: {texto_orden}")
        else:
            self.lbl_orden_actual.config(text="Orden: (se define al ordenar)")

    # ------------------------------------------------------------- Acciones

    def _accion_registrar(self) -> None:
        v = self.var_variables.get().strip()
        t = self.var_terminales.get().strip()
        s = self.var_inicial.get().strip()
        p = self.texto_producciones.get("1.0", tk.END).strip()
        o = self.var_orden.get().strip()

        self.proceso.ingresar_gramatica(v, t, s, p, o)
        self.lbl_estado.config(text="Gramática registrada. Presione 'Validar FNC'.")
        self._actualizar_estado_botones()

    def _accion_validar(self) -> None:
        self._accion_registrar()
        errores = self.proceso.validar()
        advertencias = self.proceso.advertencias()
        if errores:
            mensaje = "\n".join(errores)
            texto = f"Errores de validación:\n\n{mensaje}"
            if advertencias:
                texto += "\n\nAdvertencias:\n\n" + "\n".join(advertencias)
            self._actualizar_texto(self.texto_paso, texto)
            self.notebook.select(self.tab_paso)
            self.lbl_estado.config(text="La gramática contiene errores.")
            self._actualizar_estado_botones()
            if self.proceso.errores_son_de_fnc():
                # La gramática está bien escrita pero no en FNC: se ofrece el Microproyecto 1.
                aviso = "\n\nAdvertencias:\n" + "\n".join(advertencias) if advertencias else ""
                if messagebox.askyesno(
                    "La gramática no está en FNC",
                    f"{mensaje}{aviso}\n\n¿Desea convertirla primero a FNC con el Microproyecto 1?",
                ):
                    self._accion_convertir_primero_a_fnc()
                    return
            else:
                messagebox.showwarning("Atención", f"La gramática no puede procesarse:\n\n{mensaje}")
        else:
            pasos = self.proceso.historial().pasos
            texto_res = "\n\n".join(p.a_texto() for p in pasos)
            self._actualizar_texto(self.texto_paso, texto_res)
            self._actualizar_texto(self.texto_historial, self.proceso.historial().a_texto())
            self.notebook.select(self.tab_paso)
            if advertencias:
                self.lbl_estado.config(text="Gramática en FNC validada con advertencias. Puede iniciar la conversión.")
                messagebox.showwarning(
                    "Advertencias de validación",
                    "La gramática se puede procesar, pero se encontró lo siguiente:\n\n" + "\n".join(advertencias),
                )
            else:
                self.lbl_estado.config(text="Gramática en FNC válida. Puede iniciar la conversión a FNG.")

        self._actualizar_estado_botones()

    def _accion_convertir_primero_a_fnc(self) -> None:
        try:
            datos_fnc = self.proceso.convertir_entrada_con_microproyecto1()
            self._cargar_datos_en_formulario(datos_fnc)
            messagebox.showinfo(
                "Convertida a FNC",
                "La gramática fue transformada a Forma Normal de Chomsky con el Microproyecto 1.\n"
                "Ahora puede validar y continuar la conversión a FNG.",
            )
            self._accion_validar()
        except ErrorProcesoFNG as err:
            messagebox.showerror("Error al convertir a FNC", str(err))
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")

    def _accion_siguiente_paso(self) -> None:
        try:
            paso = self.proceso.siguiente_paso()
            self._actualizar_texto(self.texto_paso, paso.a_texto())
            self._actualizar_texto(self.texto_historial, self.proceso.historial().a_texto())
            self.notebook.select(self.tab_paso)

            if self.proceso.lenguaje_vacio():
                messagebox.showinfo("Lenguaje vacío", "El lenguaje de la gramática es vacío; el proceso concluye.")
                self.lbl_estado.config(text="El lenguaje es vacío.")
            elif self.proceso.proceso_terminado():
                g_final = self.proceso.gramatica_final()
                if g_final:
                    self._actualizar_texto(self.texto_final, g_final.a_texto())
                self.notebook.select(self.tab_final)
                self.lbl_estado.config(text="Conversión a Forma Normal de Greibach completada.")
            else:
                self.lbl_estado.config(text=f"Paso ejecutado: {paso.nombre}")
        except ErrorProcesoFNG as err:
            messagebox.showwarning("Atención", str(err))
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar el paso: {e}")

        self._actualizar_estado_botones()

    def _accion_automatico(self) -> None:
        try:
            pasos = self.proceso.ejecutar_todo()
            self._actualizar_texto(self.texto_paso, "\n\n".join(p.a_texto() for p in pasos[-3:]))
            self._actualizar_texto(self.texto_historial, self.proceso.historial().a_texto())

            if self.proceso.lenguaje_vacio():
                messagebox.showinfo("Lenguaje vacío", "El lenguaje de la gramática es vacío; el proceso concluye.")
                self.lbl_estado.config(text="El lenguaje es vacío.")
            elif self.proceso.proceso_terminado():
                g_final = self.proceso.gramatica_final()
                if g_final:
                    self._actualizar_texto(self.texto_final, g_final.a_texto())
                self.notebook.select(self.tab_final)
                self.lbl_estado.config(text="Conversión a FNG completada exitosamente.")
        except ErrorProcesoFNG as err:
            messagebox.showwarning("Atención", str(err))
        except Exception as e:
            messagebox.showerror("Error", f"Error en ejecución automática: {e}")

        self._actualizar_estado_botones()

    def _accion_mostrar_original(self) -> None:
        g = self.proceso.gramatica_original()
        if not g:
            messagebox.showinfo("Gramática original", "Aún no se ha validado ninguna gramática.")
            return
        self._actualizar_texto(self.texto_paso, f"Gramática original:\n\n{g.a_texto()}")
        self.notebook.select(self.tab_paso)

    def _accion_nueva_gramatica(self) -> None:
        if messagebox.askyesno("Nueva gramática", "¿Desea limpiar los campos y comenzar otra gramática?"):
            self.var_variables.set("")
            self.var_terminales.set("")
            self.var_inicial.set("")
            self.var_orden.set("")
            self.combo_inicial["values"] = []
            self.texto_producciones.delete("1.0", tk.END)
            self._actualizar_texto(self.texto_paso, "")
            self._actualizar_texto(self.texto_historial, "")
            self._actualizar_texto(self.texto_final, "")
            self.proceso.reiniciar()
            self._actualizar_estado_botones()
            self.lbl_estado.config(text="Campos reiniciados.")

    def _accion_salir(self) -> None:
        if messagebox.askyesno("Salir", "¿Desea cerrar el aplicativo?"):
            self.destroy()
