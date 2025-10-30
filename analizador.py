import re
import sys
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, PanedWindow, messagebox, font

class Analizador: 

    def __init__(self, master):
        self.master = master
        master.title("Analizador Léxico (v1.0)")
        master.geometry("1100x750")

        self.COLOR_FONDO_VENTANA = "#2c3e50"
        self.COLOR_FONDO_FRAME = "#34495e"
        self.COLOR_TEXTO_TITULO = "#ecf0f1"
        self.COLOR_TEXTO_NORMAL = "#000000"
        self.COLOR_FONDO_WIDGET = "#f0f0f0"
        self.COLOR_BOTON_CARGAR = "#3498db"
        self.COLOR_BOTON_ANALIZAR = "#2ecc71"
        self.COLOR_BOTON_LIMPIAR = "#e74c3c"
        self.COLOR_TEXTO_BOTON = "#ffffff"
        self.COLOR_FONDO_ERROR = "#fdedec"
        self.COLOR_TEXTO_ERROR = "#c0392b"
        self.COLOR_FONDO_EXITO = "#eafaf1"
        self.COLOR_TEXTO_EXITO = "#27ae60"

        master.configure(bg=self.COLOR_FONDO_VENTANA)

        self.token_patterns = [
            ('COMENTARIO', r'//.*'), # Se filtran del log
            ('PALABRA_RESERVADA', r'\b(entero|flotante|cadena|mientras|mostrar|comparar|si|sino)\b'),
            ('OP_LOGICO', r'(&&|\|\||!)'),
            ('OP_RELACIONAL', r'(==|>=|<=|!=|''|>|<|=)'), #se filtra del log las ''
            ('OP_ARITMETICO', r'[\+\-\*\/\^]'),
            ('LIT_CADENA', r"'[^']*'"), 
            ('LIT_FLOTANTE', r'\d+\.\d+'),
            ('LIT_ENTERO', r'\d+'),
            ('IDENTIFICADOR', r'[a-zA-Z_]\w*'),
            ('DELIMITADOR', r'[\(\)\{\}\,]'),
            ('ESPACIO', r'\s+'), 
            #Para marcar cualquier "palabra" que no sea una palabra reservada
            ('ERROR_PALABRA', r'[a-zA-Z_]\w*'),  
            #Para marcar cualquier otro signo reconocido
            ('ERROR_SIMBOLO', r'.'), 
        ]
        
        #Empieza lo del Frontend
        self.default_font = font.Font(family="Consolas", size=11)
        self.font_boton = font.Font(family="Arial", size=10, weight="bold")
        
        
        #Para tener una guardada de resultados dinámica
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        self.ruta_resultados = os.path.join(application_path, 'Resultados')

        self.default_filename = "analisis_manual"
        self.current_filename_base = self.default_filename

        #Botones
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

        self.btn_clear = tk.Button(frame_botones, text="Limpiar", 
                                command=self.limpiar_campos, 
                                bg=self.COLOR_BOTON_LIMPIAR, fg=self.COLOR_TEXTO_BOTON,
                                font=self.font_boton, relief=tk.FLAT, borderwidth=0,
                                padx=10, pady=5)
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        #Paneles
        self.paned_window_horizontal = PanedWindow(master, orient=tk.HORIZONTAL, 
                                                    sashrelief=tk.RAISED, bg=self.COLOR_FONDO_FRAME,
                                                    borderwidth=0)
        self.paned_window_horizontal.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        frame_izquierdo_vertical = PanedWindow(self.paned_window_horizontal, orient=tk.VERTICAL, 
                                                sashrelief=tk.RAISED, bg=self.COLOR_FONDO_FRAME,
                                                borderwidth=0)
        self.paned_window_horizontal.add(frame_izquierdo_vertical, width=550)

        frame_codigo_fuente = tk.Frame(frame_izquierdo_vertical, bg=self.COLOR_FONDO_FRAME,
                                        padx=5, pady=5)
        tk.Label(frame_codigo_fuente, text="Código Fuente", 
                    font=("Arial", 12, "bold"), 
                    bg=self.COLOR_FONDO_FRAME, fg=self.COLOR_TEXTO_TITULO).pack(pady=(0, 5))
        self.text_input = scrolledtext.ScrolledText(frame_codigo_fuente, wrap=tk.WORD, 
                                                    font=self.default_font, undo=True,
                                                    bg=self.COLOR_FONDO_WIDGET, fg=self.COLOR_TEXTO_NORMAL,
                                                    insertbackground=self.COLOR_TEXTO_NORMAL, 
                                                    borderwidth=0, highlightthickness=0)
        self.text_input.pack(fill=tk.BOTH, expand=True)
        frame_izquierdo_vertical.add(frame_codigo_fuente, height=400)

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

        frame_log = tk.Frame(self.paned_window_horizontal, bg=self.COLOR_FONDO_FRAME,
                                padx=5, pady=5)
        tk.Label(frame_log, text="Log de Tokens", 
                    font=("Arial", 12, "bold"),
                    bg=self.COLOR_FONDO_FRAME, fg=self.COLOR_TEXTO_TITULO).pack(pady=(0, 5))
        self.text_log = scrolledtext.ScrolledText(frame_log, wrap=tk.WORD, 
                                                    font=self.default_font, 
                                                    bg=self.COLOR_FONDO_WIDGET, fg="#333333", 
                                                    state=tk.DISABLED,
                                                    borderwidth=0, highlightthickness=0)
        self.text_log.pack(fill=tk.BOTH, expand=True)
        self.paned_window_horizontal.add(frame_log)


    #Metodos
    def cargar_archivo(self):
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
                self.limpiar_campos(limpiar_input=False)
                
                base_name = os.path.basename(filepath) 
                file_name_without_ext = os.path.splitext(base_name)[0]
                self.current_filename_base = file_name_without_ext

        except Exception as e:
            messagebox.showerror("Error al leer archivo", f"No se pudo leer el archivo:\n{e}")

    def limpiar_campos(self, limpiar_input=True): #Limpia toda la interfaz
        if limpiar_input:
            self.text_input.delete("1.0", tk.END)
            self.current_filename_base = self.default_filename

        self.text_log.config(state=tk.NORMAL)
        self.text_log.delete("1.0", tk.END)
        self.text_log.config(state=tk.DISABLED)
        
        self.text_errores.config(state=tk.NORMAL)
        self.text_errores.delete("1.0", tk.END)
        self.text_errores.config(bg=self.COLOR_FONDO_ERROR, fg=self.COLOR_TEXTO_ERROR)
        self.text_errores.config(state=tk.DISABLED)


    def ejecutar_analisis(self):
        self.text_log.config(state=tk.NORMAL)
        self.text_errores.config(state=tk.NORMAL)
        self.text_log.delete("1.0", tk.END)
        self.text_errores.delete("1.0", tk.END)
        self.text_errores.config(bg=self.COLOR_FONDO_ERROR, fg=self.COLOR_TEXTO_ERROR)
        
        codigo_fuente = self.text_input.get("1.0", "end-1c")
        
        if not codigo_fuente.strip():
            messagebox.showwarning("Entrada Vacía", "No hay código fuente para analizar.")
            self.text_log.config(state=tk.DISABLED)
            self.text_errores.config(state=tk.DISABLED)
            return

        log_salida, errores_encontrados = self.analizar(codigo_fuente)
        
        # Guardar resultados con los nombres dinámicos
        msg_guardado = ""
        try:
            os.makedirs(self.ruta_resultados, exist_ok=True)
            
            log_filename = f"{self.current_filename_base}_tokens.txt"
            errores_filename = f"{self.current_filename_base}_errores.txt"

            ruta_log = os.path.join(self.ruta_resultados, log_filename)
            ruta_errores = os.path.join(self.ruta_resultados, errores_filename)

            texto_log = '\n'.join(log_salida) if log_salida else "No se generaron tokens."
            with open(ruta_log, 'w', encoding='utf-8') as f_log:
                f_log.write(texto_log)
            
            if errores_encontrados:
                texto_errores = '\n'.join(errores_encontrados)
            else:
                texto_errores = "Análisis completado sin errores léxicos."
                
            with open(ruta_errores, 'w', encoding='utf-8') as f_err:
                f_err.write(texto_errores)
            
            msg_guardado = f"\n\n[Guardado como: {log_filename} y {errores_filename}]"

        except Exception as e:
            msg_guardado = f"\n\n[ERROR AL GUARDAR ARCHIVOS: {e}]"
            messagebox.showerror("Error al guardar archivos", 
                                f"No se pudieron guardar los resultados en:\n{self.ruta_resultados}\n\nError: {e}")
        
        # Mostrar resultados en los ventanas
        if log_salida:
            self.text_log.insert(tk.END, '\n'.join(log_salida))
        else:
            self.text_log.insert(tk.END, "No se generaron tokens.")
        
        self.text_log.insert(tk.END, msg_guardado) 
            
        if errores_encontrados:
            self.text_errores.insert(tk.END, '\n'.join(errores_encontrados))
        else:
            self.text_errores.config(bg=self.COLOR_FONDO_EXITO, fg=self.COLOR_TEXTO_EXITO)
            self.text_errores.insert(tk.END, "Análisis completado sin errores léxicos.")
        
        self.text_errores.insert(tk.END, msg_guardado) 

        self.text_log.config(state=tk.DISABLED)
        self.text_errores.config(state=tk.DISABLED)


    #Logica para realizar los tokens

    def tokenize(self, codigo_fuente, token_patterns):
        regex_combinado = re.compile('|'.join(f'(?P<{tipo}>{patron})' for tipo, patron in token_patterns))
        linea_actual = 1
        
        for match in regex_combinado.finditer(codigo_fuente):
            tipo_token = match.lastgroup 
            valor_token = match.group() 

            if tipo_token == 'ESPACIO':
                linea_actual += valor_token.count('\n')
                continue 
            
            yield tipo_token, valor_token, linea_actual

    #logica para analizar el archivo de texto ingresado
    def analizar(self, codigo_fuente):
        log_salida = []
        errores_encontrados = []
        
        #ignorar en el log los comentarios
        tokens_a_ignorar_en_log = ['COMENTARIO']

        for tipo_token, valor_token, linea_num in self.tokenize(codigo_fuente, self.token_patterns):
            
            if tipo_token == 'ERROR_PALABRA':
                error_msg = f"Error Léxico en línea {linea_num}: Palabra no reconocida '{valor_token}' (no es una palabra reservada)."
                errores_encontrados.append(error_msg)
                continue
            
            elif tipo_token == 'ERROR_SIMBOLO':
                error_msg = f"Error Léxico en línea {linea_num}: Carácter inesperado '{valor_token}' no reconocido."
                errores_encontrados.append(error_msg)
                continue

            if tipo_token in tokens_a_ignorar_en_log:
                continue
                
            if tipo_token == 'OP_RELACIONAL' and (valor_token == "''" or valor_token == ""):
                continue

            # Si pasa todos los filtros y no da error, se añade al log
            log_entry = f"Línea {linea_num}: [Tipo: {tipo_token}, Valor: {valor_token}]"
            log_salida.append(log_entry)
        
        return log_salida, errores_encontrados


if __name__ == "__main__":
    root = tk.Tk()
    app = Analizador(root)
    root.mainloop()