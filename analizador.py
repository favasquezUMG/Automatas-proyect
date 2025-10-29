import re
import sys
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, PanedWindow, messagebox, font

class Analizador: 

    def __init__(self, master):
        """
        Constructor de la aplicación.
        Inicializa la GUI y configura los widgets con el nuevo diseño.
        """
        self.master = master
        master.title("Analizador Léxico (v1.0)")
        master.geometry("1100x750")

        # --- Paleta de Colores (Tema Oscuro/Azul) ---
        self.COLOR_FONDO_VENTANA = "#2c3e50"
        self.COLOR_FONDO_FRAME = "#34495e"
        self.COLOR_TEXTO_TITULO = "#ecf0f1"
        self.COLOR_TEXTO_NORMAL = "#000000"
        # --- CAMBIO AQUÍ ---
        self.COLOR_FONDO_WIDGET = "#f0f0f0" # <-- Gris pálido
        
        self.COLOR_BOTON_CARGAR = "#3498db" # Azul
        self.COLOR_BOTON_ANALIZAR = "#2ecc71" # Verde
        self.COLOR_BOTON_LIMPIAR = "#e74c3c" # Rojo
        self.COLOR_TEXTO_BOTON = "#ffffff"
        
        self.COLOR_FONDO_ERROR = "#fdedec" # Rosa pálido
        self.COLOR_TEXTO_ERROR = "#c0392b" # Rojo oscuro
        self.COLOR_FONDO_EXITO = "#eafaf1" # Verde pálido
        self.COLOR_TEXTO_EXITO = "#27ae60" # Verde oscuro

        # Configurar color de fondo de la ventana principal
        master.configure(bg=self.COLOR_FONDO_VENTANA)

        # --- Definición de Patrones de Tokens ---
        self.token_patterns = [
            ('COMENTARIO', r'//.*'),
            ('PALABRA_RESERVADA', r'\b(entero|flotante|cadena|mientras|mostrar|comparar|si|sino)\b'),
            ('OP_LOGICO', r'(&&|\|\||!)'),
            ('OP_RELACIONAL', r'(==|!=|<=|>=|<|>)'),
            ('ASIGNACION', r'='),
            ('OP_ARITMETICO', r'[\+\-\*\/]'),
            ('LIT_CADENA', r"'[^']*'"),
            ('LIT_FLOTANTE', r'\d+\.\d+'),
            ('LIT_ENTERO', r'\d+'),
            ('IDENTIFICADOR', r'[a-zA-Z_]\w*'),
            ('DELIMITADOR', r'[\(\)\{\}\,]'),
            ('ESPACIO', r'\s+'),
            ('ERROR', r'.'),
        ]
        
        # --- Configuración de la GUI ---
        
        # Fuente estándar para los cuadros de texto
        self.default_font = font.Font(family="Consolas", size=11)
        # Fuente para los botones
        self.font_boton = font.Font(family="Arial", size=10, weight="bold")
        
        # --- Panel de Botones Superiores ---
        frame_botones = tk.Frame(master, pady=10, bg=self.COLOR_FONDO_VENTANA)
        frame_botones.pack(fill=tk.X)
        
        self.btn_browse = tk.Button(frame_botones, text="Cargar Archivo", 
                                    command=self.cargar_archivo, 
                                    bg=self.COLOR_BOTON_CARGAR, fg=self.COLOR_TEXTO_BOTON,
                                    font=self.font_boton, relief=tk.FLAT, borderwidth=0,
                                    padx=10, pady=5)
        self.btn_browse.pack(side=tk.LEFT, padx=(10, 5))
        
        self.btn_analyze = tk.Button(frame_botones, text="Analizar Código", 
                                     command=self.ejecutar_analisis, 
                                     bg=self.COLOR_BOTON_ANALIZAR, fg=self.COLOR_TEXTO_BOTON,
                                     font=self.font_boton, relief=tk.FLAT, borderwidth=0,
                                     padx=10, pady=5)
        self.btn_analyze.pack(side=tk.LEFT, padx=5)

        # --- Botón de Limpiar ---
        self.btn_clear = tk.Button(frame_botones, text="Limpiar", 
                                   command=self.limpiar_campos, 
                                   bg=self.COLOR_BOTON_LIMPIAR, fg=self.COLOR_TEXTO_BOTON,
                                   font=self.font_boton, relief=tk.FLAT, borderwidth=0,
                                   padx=10, pady=5)
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        # --- Panel Principal (Dividido HORIZONTALMENTE) ---
        self.paned_window_horizontal = PanedWindow(master, orient=tk.HORIZONTAL, 
                                                   sashrelief=tk.RAISED, bg=self.COLOR_FONDO_FRAME,
                                                   borderwidth=0)
        self.paned_window_horizontal.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # --- Panel Izquierdo (Dividido VERTICALMENTE) ---
        frame_izquierdo_vertical = PanedWindow(self.paned_window_horizontal, orient=tk.VERTICAL, 
                                               sashrelief=tk.RAISED, bg=self.COLOR_FONDO_FRAME,
                                               borderwidth=0)
        self.paned_window_horizontal.add(frame_izquierdo_vertical, width=550)

        # --- Panel Izquierdo-Superior (Código Fuente) ---
        frame_codigo_fuente = tk.Frame(frame_izquierdo_vertical, bg=self.COLOR_FONDO_FRAME,
                                       padx=5, pady=5)
        tk.Label(frame_codigo_fuente, text="Código Fuente", 
                 font=("Arial", 12, "bold"), 
                 bg=self.COLOR_FONDO_FRAME, fg=self.COLOR_TEXTO_TITULO).pack(pady=(0, 5))
        # Se aplica el color de fondo aquí
        self.text_input = scrolledtext.ScrolledText(frame_codigo_fuente, wrap=tk.WORD, 
                                                    font=self.default_font, undo=True,
                                                    bg=self.COLOR_FONDO_WIDGET, fg=self.COLOR_TEXTO_NORMAL,
                                                    insertbackground=self.COLOR_TEXTO_NORMAL, 
                                                    borderwidth=0, highlightthickness=0)
        self.text_input.pack(fill=tk.BOTH, expand=True)
        frame_izquierdo_vertical.add(frame_codigo_fuente, height=400)

        # --- Panel Izquierdo-Inferior (Errores Léxicos) ---
        frame_errores = tk.Frame(frame_izquierdo_vertical, bg=self.COLOR_FONDO_FRAME,
                                 padx=5, pady=5)
        tk.Label(frame_errores, text="Errores Léxicos", 
                 font=("Arial", 12, "bold"), 
                 bg=self.COLOR_FONDO_FRAME, fg=self.COLOR_BOTON_LIMPIAR).pack(pady=(0, 5))
        self.text_errores = scrolledtext.ScrolledText(frame_errores, wrap=tk.WORD, 
                                                      font=self.default_font, 
                                                      bg=self.COLOR_FONDO_ERROR, fg=self.COLOR_TEXTO_ERROR, 
                                                      state=tk.DISABLED,
                                                      borderwidth=0, highlightthickness=0)
        self.text_errores.pack(fill=tk.BOTH, expand=True)
        frame_izquierdo_vertical.add(frame_errores)

        # --- Panel Derecho (Log de Tokens) ---
        frame_log = tk.Frame(self.paned_window_horizontal, bg=self.COLOR_FONDO_FRAME,
                             padx=5, pady=5)
        tk.Label(frame_log, text="Log de Tokens", 
                 font=("Arial", 12, "bold"),
                 bg=self.COLOR_FONDO_FRAME, fg=self.COLOR_TEXTO_TITULO).pack(pady=(0, 5))
        # Se aplica el color de fondo aquí
        self.text_log = scrolledtext.ScrolledText(frame_log, wrap=tk.WORD, 
                                                  font=self.default_font, 
                                                  bg=self.COLOR_FONDO_WIDGET, fg="#333333", 
                                                  state=tk.DISABLED,
                                                  borderwidth=0, highlightthickness=0)
        self.text_log.pack(fill=tk.BOTH, expand=True)
        self.paned_window_horizontal.add(frame_log)

    # --- Métodos de la Aplicación ---

    def cargar_archivo(self):
        """
        Abre un diálogo para que el usuario seleccione un archivo.
        """
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo de código fuente",
            filetypes=(("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*"))
        )
        if not filepath:
            return
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                contenido = f.read()
                self.text_input.delete("1.0", tk.END) 
                self.text_input.insert("1.0", contenido) 
                self.limpiar_campos(limpiar_input=False) # Limpia solo los resultados
        except Exception as e:
            messagebox.showerror("Error al leer archivo", f"No se pudo leer el archivo:\n{e}")

    def limpiar_campos(self, limpiar_input=True):
        """
        Limpia el contenido de todas las áreas de texto.
        """
        if limpiar_input:
            self.text_input.delete("1.0", tk.END)

        # Habilitar, limpiar y deshabilitar
        self.text_log.config(state=tk.NORMAL)
        self.text_log.delete("1.0", tk.END)
        self.text_log.config(state=tk.DISABLED)
        
        self.text_errores.config(state=tk.NORMAL)
        self.text_errores.delete("1.0", tk.END)
        # Resetear al color de error por defecto al limpiar
        self.text_errores.config(bg=self.COLOR_FONDO_ERROR, fg=self.COLOR_TEXTO_ERROR)
        self.text_errores.config(state=tk.DISABLED)


    def ejecutar_analisis(self):
        """
        Función principal que se llama al presionar el botón "Analizar".
        """
        # Habilitar los campos de texto
        self.text_log.config(state=tk.NORMAL)
        self.text_errores.config(state=tk.NORMAL)
        
        # Limpiar resultados anteriores
        self.text_log.delete("1.0", tk.END)
        self.text_errores.delete("1.0", tk.END)
        
        # --- RESETEAR COLOR DE ERRORES ---
        self.text_errores.config(bg=self.COLOR_FONDO_ERROR, fg=self.COLOR_TEXTO_ERROR)
        
        codigo_fuente = self.text_input.get("1.0", "end-1c")
        
        if not codigo_fuente.strip():
            messagebox.showwarning("Entrada Vacía", "No hay código fuente para analizar.")
            self.text_log.config(state=tk.DISABLED)
            self.text_errores.config(state=tk.DISABLED)
            return

        # Ejecutar el análisis
        log_salida, errores_encontrados = self.analizar(codigo_fuente)
        
        # Mostrar resultados en los cuadros de texto
        if log_salida:
            self.text_log.insert(tk.END, '\n'.join(log_salida))
        else:
            self.text_log.insert(tk.END, "No se generaron tokens.")
            
        if errores_encontrados:
            self.text_errores.insert(tk.END, '\n'.join(errores_encontrados))
        else:
            # --- CAMBIO: Aplicar color de éxito ---
            self.text_errores.config(bg=self.COLOR_FONDO_EXITO, fg=self.COLOR_TEXTO_EXITO)
            self.text_errores.insert(tk.END, "Análisis completado sin errores léxicos.")
        
        # Deshabilitar edición
        self.text_log.config(state=tk.DISABLED)
        self.text_errores.config(state=tk.DISABLED)


    # --- Lógica del Analizador (Sin cambios) ---

    def tokenize(self, codigo_fuente, token_patterns):
        """
        Generador de tokens.
        """
        regex_combinado = re.compile('|'.join(f'(?P<{tipo}>{patron})' for tipo, patron in token_patterns))
        linea_actual = 1
        
        for match in regex_combinado.finditer(codigo_fuente):
            tipo_token = match.lastgroup 
            valor_token = match.group() 

            if tipo_token == 'ESPACIO':
                linea_actual += valor_token.count('\n')
                continue 
            
            yield tipo_token, valor_token, linea_actual

    def analizar(self, codigo_fuente):
        """
        Analizador Léxico principal.
        """
        log_salida = []
        errores_encontrados = []

        for tipo_token, valor_token, linea_num in self.tokenize(codigo_fuente, self.token_patterns):
            
            log_entry = f"Línea {linea_num}: [Tipo: {tipo_token}, Valor: '{valor_token}']"
            log_salida.append(log_entry)

            if tipo_token == 'ERROR':
                error_msg = f"Error Léxico en línea {linea_num}: Carácter inesperado '{valor_token}' no reconocido."
                errores_encontrados.append(error_msg)
        
        return log_salida, errores_encontrados


if __name__ == "__main__":
    """
    Punto de entrada principal para iniciar la aplicación GUI.
    """
    root = tk.Tk()
    app = Analizador(root)
    root.mainloop() 