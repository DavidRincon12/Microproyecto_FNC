"""Interfaz gráfica del aplicativo de Depuración y FNC (RNF01, RF01-RF20, sección 12)."""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from fnc.entrada.lector import guardar_archivo, leer_archivo, leer_simbolos

# Se importa ProcesoFNC y ErrorProceso de forma tolerante si aún no se ha integrado D9
try:
    from fnc.proceso import ErrorProceso, ProcesoFNC
except ImportError:
    ProcesoFNC = None
    class ErrorProceso(Exception):
        pass


def ruta_recurso(relativa: str) -> str:
    """Obtiene la ruta absoluta para recursos, compatible con PyInstaller y ejecución normal."""
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        # Raíz del proyecto (tres niveles arriba desde fnc/interfaz)
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, relativa)


class VentanaPrincipal(tk.Tk):
    """Ventana principal del aplicativo de Depuración y Conversión a FNC."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Depuración y Forma Normal de Chomsky")
        self.minsize(1050, 680)
        self.geometry("1100x720")

        # Controlador del proceso
        self.proceso = ProcesoFNC() if ProcesoFNC is not None else None

        # Configuración de estilos
        self._configurar_estilos()

        # Construcción de la interfaz
        self._crear_paneles_principales()
        self._crear_panel_entrada()
        self._crear_panel_acciones()
        self._crear_panel_visualizacion()
        self._crear_barra_estado()

        # Actualizar estado inicial de controles
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
        style.configure("Titulo.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Estado.TLabel", font=("Segoe UI", 9))

    def _crear_paneles_principales(self) -> None:
        self.contenedor_principal = ttk.Frame(self, padding=8)
        self.contenedor_principal.pack(fill=tk.BOTH, expand=True)

        # Panel izquierdo (Entrada y Botones de acción)
        self.frame_izquierdo = ttk.Frame(self.contenedor_principal, width=420)
        self.frame_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 6))

        # Panel derecho (Resultados con pestañas)
        self.frame_derecho = ttk.Frame(self.contenedor_principal)
        self.frame_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def _crear_panel_entrada(self) -> None:
        grupo_entrada = ttk.LabelFrame(self.frame_izquierdo, text="Gramática de entrada", padding=10)
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

        # Producciones
        ttk.Label(grupo_entrada, text="Reglas de producción:").grid(row=3, column=0, sticky=tk.NW, pady=(6, 2))
        self.texto_producciones = ScrolledText(grupo_entrada, width=32, height=6, font=("Consolas", 10))
        self.texto_producciones.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(0, 4))

        # Línea de ayuda de formato
        ttk.Label(
            grupo_entrada,
            text="Formato: S -> aSb | ε   (V en mayúscula, T en minúscula)",
            font=("Segoe UI", 8, "italic"),
            foreground="#555555",
        ).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 6))

        # Botones de utilidad para la entrada
        frame_utilidades = ttk.Frame(grupo_entrada)
        frame_utilidades.grid(row=6, column=0, columnspan=2, sticky=tk.EW)

        btn_epsilon = ttk.Button(frame_utilidades, text="Insertar ε", command=self._insertar_epsilon, width=10)
        btn_epsilon.pack(side=tk.LEFT, padx=(0, 4))

        btn_abrir = ttk.Button(frame_utilidades, text="Abrir...", command=self._abrir_archivo, width=9)
        btn_abrir.pack(side=tk.LEFT, padx=2)

        btn_guardar = ttk.Button(frame_utilidades, text="Guardar...", command=self._guardar_archivo, width=9)
        btn_guardar.pack(side=tk.LEFT, padx=2)

        # Menú de ejemplos
        ttk.Label(frame_utilidades, text="Ejemplo:").pack(side=tk.LEFT, padx=(8, 2))
        self.combo_ejemplos = ttk.Combobox(
            frame_utilidades,
            values=["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"],
            width=5,
            state="readonly",
        )
        self.combo_ejemplos.pack(side=tk.LEFT)
        self.combo_ejemplos.bind("<<ComboboxSelected>>", self._cargar_ejemplo_seleccionado)

        grupo_entrada.columnconfigure(1, weight=1)

    def _crear_panel_acciones(self) -> None:
        grupo_acciones = ttk.LabelFrame(self.frame_izquierdo, text="Acciones del proceso", padding=10)
        grupo_acciones.pack(fill=tk.BOTH, expand=True)

        # Botón 1 y 3 (Entrada y Validación)
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
            text="3. Validar gramática",
            command=self._accion_validar,
            style="Destacado.TButton",
        )
        self.btn_validar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

        # Paso a paso
        lbl_paso = ttk.Label(grupo_acciones, text="Modo paso a paso (secuencial):", font=("Segoe UI", 9, "bold"))
        lbl_paso.pack(anchor=tk.W, pady=(6, 2))

        self.lbl_siguiente = ttk.Label(
            grupo_acciones,
            text="Siguiente etapa: (requiere validar)",
            foreground="#0055aa",
            font=("Segoe UI", 9, "italic"),
        )
        self.lbl_siguiente.pack(anchor=tk.W, pady=(0, 4))

        # Botones de etapas individuales
        self.btn_etapas = {}

        self.btn_etapas["nulas"] = ttk.Button(
            grupo_acciones,
            text="4. Eliminar producciones nulas",
            command=lambda: self._accion_etapa("nulas"),
        )
        self.btn_etapas["nulas"].pack(fill=tk.X, pady=2)

        self.btn_etapas["unitarias"] = ttk.Button(
            grupo_acciones,
            text="5. Eliminar producciones unitarias",
            command=lambda: self._accion_etapa("unitarias"),
        )
        self.btn_etapas["unitarias"].pack(fill=tk.X, pady=2)

        self.btn_etapas["inutiles"] = ttk.Button(
            grupo_acciones,
            text="6. Eliminar variables inútiles",
            command=lambda: self._accion_etapa("inutiles"),
        )
        self.btn_etapas["inutiles"].pack(fill=tk.X, pady=2)

        self.btn_etapas["inalcanzables"] = ttk.Button(
            grupo_acciones,
            text="7. Eliminar variables inalcanzables",
            command=lambda: self._accion_etapa("inalcanzables"),
        )
        self.btn_etapas["inalcanzables"].pack(fill=tk.X, pady=2)

        self.btn_etapas["fnc"] = ttk.Button(
            grupo_acciones,
            text="8. Convertir a Forma Normal de Chomsky",
            command=lambda: self._accion_etapa("fnc"),
        )
        self.btn_etapas["fnc"].pack(fill=tk.X, pady=2)

        # Modo automático
        ttk.Separator(grupo_acciones, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

        self.btn_automatico = ttk.Button(
            grupo_acciones,
            text="9. Ejecutar proceso completo (automático)",
            command=self._accion_automatico,
            style="Destacado.TButton",
        )
        self.btn_automatico.pack(fill=tk.X, pady=2)

        # Acciones de consulta y reinicio
        frame_inferior = ttk.Frame(grupo_acciones)
        frame_inferior.pack(fill=tk.X, pady=(6, 0))

        self.btn_original = ttk.Button(
            frame_inferior,
            text="2. Gramática original",
            command=self._accion_mostrar_original,
            width=18,
        )
        self.btn_original.grid(row=0, column=0, padx=2, pady=2, sticky=tk.EW)

        self.btn_reiniciar = ttk.Button(
            frame_inferior,
            text="12. Nueva gramática",
            command=self._accion_nueva_gramatica,
            width=18,
        )
        self.btn_reiniciar.grid(row=0, column=1, padx=2, pady=2, sticky=tk.EW)

        self.btn_salir = ttk.Button(
            frame_inferior,
            text="13. Salir",
            command=self._accion_salir,
            width=18,
        )
        self.btn_salir.grid(row=1, column=0, columnspan=2, padx=2, pady=4, sticky=tk.EW)

        frame_inferior.columnconfigure(0, weight=1)
        frame_inferior.columnconfigure(1, weight=1)

    def _crear_panel_visualizacion(self) -> None:
        self.notebook = ttk.Notebook(self.frame_derecho)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Pestaña 1: Resultado del paso
        self.tab_paso = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_paso, text="10. Resultado del paso")
        self.texto_paso = self._crear_area_texto_resultado(self.tab_paso)

        # Pestaña 2: Historial completo
        self.tab_historial = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_historial, text="Historial completo")
        self.texto_historial = self._crear_area_texto_resultado(self.tab_historial)

        # Pestaña 3: Gramática final
        self.tab_final = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_final, text="11. Gramática final (FNC)")
        self.texto_final = self._crear_area_texto_resultado(self.tab_final)

    def _crear_area_texto_resultado(self, contenedor: ttk.Frame) -> ScrolledText:
        area = ScrolledText(
            contenedor,
            wrap=tk.WORD,
            font=("Consolas", 10),
            padx=10,
            pady=10,
            background="#FFFFFF",
        )
        area.pack(fill=tk.BOTH, expand=True)

        # Configuración de tags de color para presentación agradable
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
            text="Listo. Ingrese una gramática o cargue un ejemplo para comenzar.",
            style="Estado.TLabel",
        )
        self.lbl_estado.pack(side=tk.LEFT)

    # ------------------------------------------------------------- Lógica de interfaz

    def _actualizar_texto(self, area: ScrolledText, texto: str) -> None:
        """Actualiza un área de texto de solo lectura coloreando líneas según su contenido."""
        area.config(state=tk.NORMAL)
        area.delete("1.0", tk.END)

        for linea in texto.split("\n"):
            linea_con_salto = linea + "\n"
            if linea.startswith("===") or linea.startswith("Paso ") or "Forma Normal de Chomsky" in linea:
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
            elif "cumple la FNC" in linea or "válida" in linea:
                area.insert(tk.END, linea_con_salto, "exito")
            else:
                area.insert(tk.END, linea_con_salto)

        area.config(state=tk.DISABLED)

    def _al_cambiar_variables(self, *_) -> None:
        """Actualiza las opciones del Combobox de símbolo inicial a partir de las variables escritas."""
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
        seleccion = self.combo_ejemplos.get().lower()
        nombres = {
            "e1": "e1_nulas_unitarias.txt",
            "e2": "e2_inutiles_inalcanzables.txt",
            "e3": "e3_inicial_anulable.txt",
            "e4": "e4_expresiones.txt",
            "e5": "e5_varias_anulables.txt",
            "e6": "e6_nombres_unicos.txt",
            "e7": "e7_lenguaje_vacio.txt",
            "e8": "e8_con_errores.txt",
        }
        archivo = nombres.get(seleccion)
        if not archivo:
            return

        ruta = ruta_recurso(os.path.join("ejemplos", archivo))
        if not os.path.exists(ruta):
            # Probar también con ruta local directa
            ruta = os.path.join("ejemplos", archivo)

        if os.path.exists(ruta):
            try:
                datos = leer_archivo(ruta)
                self._cargar_datos_en_formulario(datos)
                self.lbl_estado.config(text=f"Ejemplo {seleccion.upper()} cargado correctamente.")
            except Exception as e:
                messagebox.showerror("Error al cargar", f"No se pudo cargar el ejemplo: {e}")
        else:
            messagebox.showwarning("Archivo no encontrado", f"No se encontró el archivo: {ruta}")

    def _abrir_archivo(self) -> None:
        ruta = filedialog.askopenfilename(
            title="Abrir archivo de gramática",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
        )
        if not ruta:
            return
        try:
            datos = leer_archivo(ruta)
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
        }
        try:
            guardar_archivo(ruta, datos)
            messagebox.showinfo("Guardado", f"Gramática guardada exitosamente en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo: {e}")

    def _cargar_datos_en_formulario(self, datos: dict[str, str]) -> None:
        self.var_variables.set(datos.get("variables", ""))
        self.var_terminales.set(datos.get("terminales", ""))
        self._al_cambiar_variables()
        self.var_inicial.set(datos.get("inicial", ""))
        self.texto_producciones.delete("1.0", tk.END)
        self.texto_producciones.insert("1.0", datos.get("producciones", ""))
        if self.proceso:
            self.proceso.reiniciar()
        self._actualizar_estado_botones()

    def _actualizar_estado_botones(self) -> None:
        """Habilita o deshabilita botones según el estado actual del proceso."""
        if not self.proceso or not self.proceso.gramatica_es_valida():
            for btn in self.btn_etapas.values():
                btn.config(state=tk.DISABLED)
            self.btn_automatico.config(state=tk.DISABLED)
            self.lbl_siguiente.config(text="Siguiente etapa: (requiere validar)", foreground="#777777")
            return

        siguiente = self.proceso.siguiente_etapa()
        for clave, btn in self.btn_etapas.items():
            if clave == siguiente:
                btn.config(state=tk.NORMAL)
            else:
                btn.config(state=tk.DISABLED)

        if siguiente is not None:
            self.btn_automatico.config(state=tk.NORMAL)
            nombres = {
                "nulas": "4. Eliminar producciones nulas",
                "unitarias": "5. Eliminar producciones unitarias",
                "inutiles": "6. Eliminar variables inútiles",
                "inalcanzables": "7. Eliminar variables inalcanzables",
                "fnc": "8. Convertir a Forma Normal de Chomsky",
            }
            self.lbl_siguiente.config(text=f"Siguiente etapa: {nombres.get(siguiente, siguiente)}", foreground="#0055AA")
        elif self.proceso.lenguaje_vacio():
            self.btn_automatico.config(state=tk.DISABLED)
            self.lbl_siguiente.config(text="Proceso detenido: el lenguaje es vacío.", foreground="#B00020")
        else:
            self.btn_automatico.config(state=tk.DISABLED)
            self.lbl_siguiente.config(text="Proceso completado.", foreground="#2E7D32")

    # ------------------------------------------------------------- Acciones del menú

    def _accion_registrar(self) -> None:
        v = self.var_variables.get().strip()
        t = self.var_terminales.get().strip()
        s = self.var_inicial.get().strip()
        p = self.texto_producciones.get("1.0", tk.END).strip()

        if self.proceso:
            self.proceso.ingresar_gramatica(v, t, s, p)
            self.lbl_estado.config(text="Gramática registrada. Presione 'Validar gramática' para comprobarla.")
        else:
            self.lbl_estado.config(text="Gramática registrada en el formulario.")
        self._actualizar_estado_botones()

    def _accion_validar(self) -> None:
        self._accion_registrar()
        if not self.proceso:
            messagebox.showinfo("Validación", "El módulo de control (ProcesoFNC) se conectará al completarse D9.")
            return

        errores = self.proceso.validar()
        if errores:
            mensaje = "\n".join(errores)
            self._actualizar_texto(self.texto_paso, f"Errores de validación:\n\n{mensaje}")
            self.notebook.select(self.tab_paso)
            messagebox.showerror("Errores de validación", f"La gramática contiene errores:\n\n{mensaje}")
            self.lbl_estado.config(text="La gramática contiene errores. Corríjalos para continuar.")
        else:
            paso_val = self.proceso.historial().pasos[-1]
            self._actualizar_texto(self.texto_paso, paso_val.a_texto())
            self._actualizar_texto(self.texto_historial, self.proceso.historial().a_texto())
            self.notebook.select(self.tab_paso)
            self.lbl_estado.config(text="Gramática validada correctamente. Puede iniciar el proceso.")

        self._actualizar_estado_botones()

    def _accion_etapa(self, etapa: str) -> None:
        if not self.proceso:
            return
        try:
            pasos = self.proceso.ejecutar_etapa(etapa)
            texto_resultado = "\n\n".join(p.a_texto() for p in pasos)
            self._actualizar_texto(self.texto_paso, texto_resultado)
            self._actualizar_texto(self.texto_historial, self.proceso.historial().a_texto())

            if self.proceso.proceso_terminado():
                g_final = self.proceso.gramatica_final()
                if g_final:
                    self._actualizar_texto(self.texto_final, g_final.a_texto())
                self.notebook.select(self.tab_final)
                self.lbl_estado.config(text="Transformación a FNC completada exitosamente.")
            else:
                self.notebook.select(self.tab_paso)
                self.lbl_estado.config(text=f"Etapa '{etapa}' ejecutada correctamente.")
                self._avisar_si_lenguaje_vacio()

        except ErrorProceso as err:
            messagebox.showwarning("Atención", str(err))
            self.lbl_estado.config(text=str(err))
        except Exception as e:
            messagebox.showerror("Error", f"Error en la ejecución de la etapa: {e}")

        self._actualizar_estado_botones()

    def _accion_automatico(self) -> None:
        if not self.proceso:
            return
        try:
            pasos = self.proceso.ejecutar_proceso_completo()
            if pasos:
                texto_resultado = "\n\n".join(p.a_texto() for p in pasos)
                self._actualizar_texto(self.texto_paso, texto_resultado)
                self._actualizar_texto(self.texto_historial, self.proceso.historial().a_texto())

            if self.proceso.proceso_terminado():
                g_final = self.proceso.gramatica_final()
                if g_final:
                    self._actualizar_texto(self.texto_final, g_final.a_texto())
                self.notebook.select(self.tab_final)
                self.lbl_estado.config(text="Proceso completo ejecutado con éxito.")
            else:
                self.notebook.select(self.tab_paso)
                self._avisar_si_lenguaje_vacio()
        except ErrorProceso as err:
            messagebox.showwarning("Atención", str(err))
            self.lbl_estado.config(text=str(err))
        except Exception as e:
            messagebox.showerror("Error", f"Error en la ejecución automática: {e}")

        self._actualizar_estado_botones()

    def _avisar_si_lenguaje_vacio(self) -> None:
        """Informa que el proceso se detuvo porque el símbolo inicial no genera cadenas."""
        if self.proceso and self.proceso.lenguaje_vacio():
            mensaje = "El lenguaje de la gramática es vacío: el símbolo inicial no genera ninguna cadena. El proceso se detuvo."
            self.lbl_estado.config(text=mensaje)
            messagebox.showwarning("Lenguaje vacío", mensaje)

    def _accion_mostrar_original(self) -> None:
        if not self.proceso or not self.proceso.gramatica_original():
            messagebox.showinfo("Gramática original", "Aún no se ha validado ninguna gramática.")
            return
        g = self.proceso.gramatica_original()
        self._actualizar_texto(self.texto_paso, f"Gramática original:\n\n{g.a_texto()}")
        self.notebook.select(self.tab_paso)
        self.lbl_estado.config(text="Mostrando gramática original.")

    def _accion_nueva_gramatica(self) -> None:
        if messagebox.askyesno("Nueva gramática", "¿Desea limpiar los campos y comenzar una nueva gramática?"):
            self.var_variables.set("")
            self.var_terminales.set("")
            self.var_inicial.set("")
            self.combo_inicial["values"] = []
            self.texto_producciones.delete("1.0", tk.END)
            self._actualizar_texto(self.texto_paso, "")
            self._actualizar_texto(self.texto_historial, "")
            self._actualizar_texto(self.texto_final, "")
            if self.proceso:
                self.proceso.reiniciar()
            self._actualizar_estado_botones()
            self.lbl_estado.config(text="Campos reiniciados. Ingrese una nueva gramática.")

    def _accion_salir(self) -> None:
        if messagebox.askyesno("Salir", "¿Está seguro de que desea salir del aplicativo?"):
            self.destroy()
