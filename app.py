import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime
import urllib.parse
import webbrowser

# Lista oficial de los 24 estados de Venezuela
ESTADOS_VENEZUELA = [
    "Amazonas", "Anzoátegui", "Apure", "Aragua", "Barinas", "Bolívar", 
    "Carabobo", "Cojedes", "Delta Amacuro", "Distrito Capital", "Falcón", 
    "Guárico", "Lara", "Mérida", "Miranda", "Monagas", "Nueva Esparta", 
    "Portuguesa", "Sucre", "Táchira", "Trujillo", "La Guaira", "Yaracuy", "Zulia"
]

# Datos Oficiales de Pagomóvil BDV de la Empresa
DATOS_PAGO_BDV = {
    "empresa": "COMPANIA HCHFA CA (Alimentos HCHF4 CA)",
    "rif": "J-404509216",
    "banco": "Banco de Venezuela (0102)",
    "telefono": "04120582064",
    "email": "alimentoshchf4@gmail.com"
}

# Base de Datos de Menús Clínicos Especializados
MENU_DATABASE = {
    "Diabetes Tipo 2": [
        {"nombre": "Bowl de Quinua y Pechuga al Limón", "precio": 6.50, "desc": "Bajo índice glucémico, rico en fibra natural."},
        {"nombre": "Salmón al Horno con Vegetales al Vapor", "precio": 8.00, "desc": "Sin azúcares añadidos, alto en Omega-3."},
        {"nombre": "Pechuga de Pollo en Reducción de Balsámico", "precio": 7.00, "desc": "Acompañada de espárragos y brócoli fresco."},
        {"nombre": "Hamburguesa de Lentejas sin Pan", "precio": 6.00, "desc": "Base de ensalada verde y aderezo de aguacate."},
        {"nombre": "Filet de Merluza a la Plancha", "precio": 7.50, "desc": "Con puré de coliflor cremoso sin mantequilla."},
        {"nombre": "Wrap de Lechuga con Atún y Vegetales", "precio": 5.80, "desc": "Proteína magra, cero carbohidratos refinados."}
    ],
    "Enfermedad Renal Crónica": [
        {"nombre": "Crema de Calabacín (Bajo Potasio)", "precio": 5.00, "desc": "Control riguroso de sodio, fósforo y potasio."},
        {"nombre": "Pollo Acorazonado con Arroz Blanco Tierno", "precio": 6.00, "desc": "Proteína de alto valor biológico ajustada."},
        {"nombre": "Tortilla de Claras con Zanahoria Rallada", "precio": 4.50, "desc": "Bajo fósforo, ideal para cenas ligeras."},
        {"nombre": "Filet de Pollo Hervido con Arroz y Chayota", "precio": 6.20, "desc": "Preparación limpia sin condimentos ricos en potasio."},
        {"nombre": "Arroz Caldoso con Pechuga Desmenuzada", "precio": 5.50, "desc": "Fácil digestión y control estricto de electrolitos."},
        {"nombre": "Pastel de Arroz Blanco con Pavo Magro", "precio": 6.80, "desc": "Bajo contenido mineral y proteico controlado."}
    ],
    "Hipertensión Severa": [
        {"nombre": "Ensalada Mediterránea de Oliva", "precio": 5.50, "desc": "Cero sodio añadido, aderezo cardioprotector."},
        {"nombre": "Pavo a las Finas Hierbas con Camote", "precio": 7.00, "desc": "Rico en magnesio y potasio equilibrado."},
        {"nombre": "Lomo de Cerdo Magro al Horno", "precio": 7.50, "desc": "Especias naturales sin sal, con vegetales asados."},
        {"nombre": "Bowl de Arroz Integral y Salteado de Pavo", "precio": 6.80, "desc": "Bajo en sodio, endulzado con hierbas frescas."},
        {"nombre": "Crema suave de Auyama sin Sal", "precio": 5.00, "desc": "Suave al paladar, rica en antioxidantes naturales."},
        {"nombre": "Pescado Blanco al Horno con Limón y Eneldo", "precio": 7.20, "desc": "Cardioprotector, cero sodio agregado."}
    ],
    "Celiaquía / Sin Gluten": [
        {"nombre": "Pasta de Garbanzos con Pesto de Albahaca", "precio": 6.80, "desc": "100% Libre de gluten certificado."},
        {"nombre": "Milanesa de Pollo con Harina de Yuca", "precio": 6.20, "desc": "Crujiente, libre de contaminación cruzada."},
        {"nombre": "Pizza casera con Base de Yuca y Vegetales", "precio": 7.50, "desc": "Queso bajo en grasa y masa libre de trigo."},
        {"nombre": "Risotto de Hongos Portobello", "precio": 8.00, "desc": "Arroz arborio certificado sin gluten."},
        {"nombre": "Bowl de Pollo, Aguacate y Arroz", "precio": 6.50, "desc": "Ingredientes naturales seguros para celíacos."},
        {"nombre": "Croquetas de Yuca y Carne Desmechada", "precio": 5.90, "desc": "Horneadas, sin reboques de trigo tradicional."}
    ]
}

# Directorio de Restaurantes y Dark Kitchens por Estado, Municipio y Parroquia
DIRECTORIO_RESTAURANTES = [
    {"nombre": "NutriKitchen Chacao", "estado": "Distrito Capital", "municipio": "Chacao", "parroquia": "El Recreo / Chacao", "especialidad": "Renal y Diabetes", "contacto": "584120582064"},
    {"nombre": "Vida Sana El Viñedo", "estado": "Carabobo", "municipio": "Valencia", "parroquia": "San José", "especialidad": "Hipertensión y Sin Gluten", "contacto": "584124445566"},
    {"nombre": "Sabor Clínico Maracaibo", "estado": "Zulia", "municipio": "Maracaibo", "parroquia": "Olegario Villalobos", "especialidad": "Diabetes y Renal", "contacto": "584146667788"},
    {"nombre": "Cocina Terapéutica Barquisimeto", "estado": "Lara", "municipio": "Iribarren", "parroquia": "Catedral", "especialidad": "Multicondición", "contacto": "584169990011"},
    {"nombre": "NutriSalud Puerto La Cruz", "estado": "Anzoátegui", "municipio": "Sotillo", "parroquia": "Puerto La Cruz", "especialidad": "Sin Gluten y Cardio", "contacto": "584248889900"}
]

ORDER_QUEUE = [
    {"id": "ORD-101", "estado": "Distrito Capital", "patologia": "Enfermedad Renal Crónica", "plato": "Crema de Calabacín (Bajo Potasio)", "prioridad": 1, "prioridad_txt": "ALTA (Renal)", "hora": "14:15", "cliente": "María Pérez"}
]


class NutriSaludApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NutriSalud Venezuela - Plataforma HealthTech")
        self.root.geometry("520x860")
        self.root.configure(bg="#F4F6F5")

        # Header Principal
        header_frame = tk.Frame(root, bg="#1B5E20", height=95)
        header_frame.pack(fill="x")
        
        lbl_title = tk.Label(header_frame, text="NutriSalud Venezuela", font=("Helvetica", 15, "bold"), fg="white", bg="#1B5E20")
        lbl_title.pack(pady=3)

        lbl_sub = tk.Label(header_frame, text="Alimentación Médica Especializada y Terapéutica", font=("Helvetica", 8, "italic"), fg="#A5D6A7", bg="#1B5E20")
        lbl_sub.pack(pady=0)

        # Barra de Navegación
        nav_frame = tk.Frame(header_frame, bg="#1B5E20")
        nav_frame.pack(pady=4)

        tk.Button(nav_frame, text="🛒 Menú", bg="#2E7D32", fg="white", font=("Helvetica", 8, "bold"), bd=0, padx=5, pady=2, command=self.mostrar_vista_clientes).pack(side="left", padx=2)
        tk.Button(nav_frame, text="🏪 Directorio", bg="#2E7D32", fg="white", font=("Helvetica", 8, "bold"), bd=0, padx=5, pady=2, command=self.mostrar_directorio).pack(side="left", padx=2)
        tk.Button(nav_frame, text="👨‍🍳 Cocina", bg="#2E7D32", fg="white", font=("Helvetica", 8, "bold"), bd=0, padx=5, pady=2, command=self.mostrar_vista_cocina).pack(side="left", padx=2)
        tk.Button(nav_frame, text="ℹ️ Compromiso", bg="#2E7D32", fg="white", font=("Helvetica", 8, "bold"), bd=0, padx=5, pady=2, command=self.mostrar_resena).pack(side="left", padx=2)

        self.main_container = tk.Frame(root, bg="#F4F6F5")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.mostrar_vista_clientes()

    def limpiar_contenedor(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # ==================== VISTA 1: MENÚ DE PACIENTES ====================
    def mostrar_vista_clientes(self):
        self.limpiar_contenedor()

        tk.Label(self.main_container, text="Seleccione Condición Médica / Patología:", font=("Helvetica", 10, "bold"), bg="#F4F6F5", anchor="w").pack(fill="x", pady=2)
        
        self.patologia_var = tk.StringVar(value="Diabetes Tipo 2")
        combo = ttk.Combobox(self.main_container, textvariable=self.patologia_var, values=list(MENU_DATABASE.keys()), state="readonly", font=("Helvetica", 10))
        combo.pack(fill="x", pady=4)
        combo.bind("<<ComboboxSelected>>", self.actualizar_menu)

        container_scroll = tk.Frame(self.main_container, bg="#F4F6F5")
        container_scroll.pack(fill="both", expand=True, pady=5)

        self.canvas = tk.Canvas(container_scroll, bg="#F4F6F5", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container_scroll, orient="vertical", command=self.canvas.yview)
        self.canvas_frame = tk.Frame(self.canvas, bg="#F4F6F5")

        self.canvas_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.canvas_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.actualizar_menu()

    def actualizar_menu(self, event=None):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        patologia = self.patologia_var.get()
        platos = MENU_DATABASE.get(patologia, [])

        for plato in platos:
            card = tk.Frame(self.canvas_frame, bg="white", bd=1, relief="solid", padx=10, pady=8)
            card.pack(fill="x", pady=5, ipadx=5)

            tk.Label(card, text=plato['nombre'], font=("Helvetica", 10, "bold"), fg="#1B5E20", bg="white").pack(anchor="w")
            tk.Label(card, text=f"Precio: ${plato['precio']:.2f}", font=("Helvetica", 9, "bold"), fg="#2E7D32", bg="white").pack(anchor="w")
            tk.Label(card, text=plato['desc'], font=("Helvetica", 8), fg="#555555", bg="white", wraplength=420, justify="left").pack(anchor="w", pady=2)

            btn_pedir = tk.Button(card, text="Pedir y Pagar con Pagomóvil BDV", bg="#2E7D32", fg="white", font=("Helvetica", 8, "bold"), bd=0, padx=8, pady=4, command=lambda p=plato, pat=patologia: self.abrir_checkout(p, pat))
            btn_pedir.pack(anchor="e", pady=2)

    # ==================== CHECKOUT Y PASARELA BDV ====================
    def abrir_checkout(self, plato, patologia):
        top = tk.Toplevel(self.root)
        top.title("Checkout NutriSalud - Pagomóvil BDV")
        top.geometry("440x780")
        top.configure(bg="#F4F6F5")

        tk.Label(top, text=f"Pedido: {plato['nombre']}\nPatología: {patologia}", font=("Helvetica", 10, "bold"), bg="#F4F6F5", justify="center").pack(pady=6)

        # Recuadro con datos fiscales
        frame_bdv = tk.LabelFrame(top, text=" Datos Oficiales para Pagomóvil BDV ", font=("Helvetica", 8, "bold"), bg="#E8F5E9", fg="#1B5E20", padx=8, pady=6)
        frame_bdv.pack(fill="x", padx=15, pady=4)

        info_txt = (
            f"• Empresa: {DATOS_PAGO_BDV['empresa']}\n"
            f"• RIF: {DATOS_PAGO_BDV['rif']}\n"
            f"• Banco: {DATOS_PAGO_BDV['banco']}\n"
            f"• Teléfono: {DATOS_PAGO_BDV['telefono']}\n"
            f"• Email: {DATOS_PAGO_BDV['email']}"
        )
        tk.Label(frame_bdv, text=info_txt, font=("Helvetica", 8), bg="#E8F5E9", justify="left").pack(anchor="w")

        tk.Label(top, text="Estado de Destino (Venezuela):", font=("Helvetica", 9, "bold"), bg="#F4F6F5").pack(anchor="w", padx=15, pady=(4, 0))
        estado_combo = ttk.Combobox(top, values=ESTADOS_VENEZUELA, state="readonly")
        estado_combo.set("Distrito Capital")
        estado_combo.pack(fill="x", padx=15, pady=2)

        tk.Label(top, text="Dirección Específica / Zona / Parroquia:", font=("Helvetica", 9, "bold"), bg="#F4F6F5").pack(anchor="w", padx=15, pady=(4, 0))
        dir_entry = tk.Entry(top, font=("Helvetica", 9))
        dir_entry.pack(fill="x", padx=15, pady=2)
        dir_entry.insert(0, "Av. principal, Edif. ...")

        tk.Label(top, text="Instrucciones Médicas o Especiales:", font=("Helvetica", 9, "bold"), bg="#F4F6F5").pack(anchor="w", padx=15, pady=(4, 0))
        sug_entry = tk.Entry(top, font=("Helvetica", 9))
        sug_entry.pack(fill="x", padx=15, pady=2)
        sug_entry.insert(0, "Sin sal añadida, empaque hermético.")

        tk.Label(top, text="Nro. Referencia de Pagomóvil BDV:", font=("Helvetica", 9, "bold"), bg="#F4F6F5").pack(anchor="w", padx=15, pady=(4, 0))
        ref_entry = tk.Entry(top, font=("Helvetica", 9))
        ref_entry.pack(fill="x", padx=15, pady=2)

        def procesar():
            ref = ref_entry.get().strip()
            direccion = dir_entry.get().strip()

            if not ref or not direccion:
                messagebox.showerror("Error", "Debe ingresar la dirección completa y la referencia del Pagomóvil.", parent=top)
                return
            
            prio = 1 if "Renal" in patologia else 2
            prio_txt = "ALTA (Renal)" if prio == 1 else "MEDIA"
            id_orden = f"ORD-{random.randint(100, 999)}"
            
            nueva_orden = {
                "id": id_orden,
                "estado": estado_combo.get(),
                "patologia": patologia,
                "plato": plato['nombre'],
                "prioridad": prio,
                "prioridad_txt": prio_txt,
                "hora": datetime.now().strftime("%H:%M"),
                "cliente": "Paciente NutriSalud"
            }
            ORDER_QUEUE.append(nueva_orden)

            texto_wsp = (
                f"*[NUEVO PEDIDO NUTRISALUD VENEZUELA]*\n"
                f"ID: {id_orden}\n"
                f"Plato: {plato['nombre']}\n"
                f"Patología: {patologia}\n"
                f"Estado: {estado_combo.get()}\n"
                f"Dirección: {direccion}\n"
                f"Nota: {sug_entry.get().strip()}\n"
                f"Pagomóvil Ref: {ref}\n"
                f"RIF Destino: {DATOS_PAGO_BDV['rif']}"
            )
            
            link_wsp = f"https://wa.me/{DATOS_PAGO_BDV['telefono']}?text={urllib.parse.quote(texto_wsp)}"
            
            messagebox.showinfo("¡Pedido Exitoso!", f"Registrado en NutriSalud Venezuela.\nPrioridad: {prio_txt}\n\nSe abrirá WhatsApp para confirmar la orden.", parent=top)
            webbrowser.open(link_wsp)
            top.destroy()

        tk.Button(top, text="Confirmar Pedido y Enviar a WhatsApp", bg="#1B5E20", fg="white", font=("Helvetica", 10, "bold"), bd=0, pady=8, command=procesar).pack(fill="x", padx=15, pady=12)

    # ==================== VISTA 2: DIRECTORIO NACIONAL ====================
    def mostrar_directorio(self):
        self.limpiar_contenedor()

        tk.Label(self.main_container, text="Directorio Nacional de Aliados NutriSalud", font=("Helvetica", 10, "bold"), fg="#1B5E20", bg="#F4F6F5").pack(anchor="w", pady=4)
        tk.Label(self.main_container, text="Cocinas Certificadas por Estado, Municipio y Parroquia", font=("Helvetica", 8, "italic"), bg="#F4F6F5").pack(anchor="w", pady=(0, 6))

        for r in DIRECTORIO_RESTAURANTES:
            card = tk.Frame(self.main_container, bg="white", bd=1, relief="solid", padx=8, pady=6)
            card.pack(fill="x", pady=3)

            tk.Label(card, text=f"• {r['nombre']}", font=("Helvetica", 9, "bold"), fg="#2E7D32", bg="white").pack(anchor="w")
            tk.Label(card, text=f"Ubicación: {r['estado']} | Mun. {r['municipio']} | Parroquia {r['parroquia']}", font=("Helvetica", 8), bg="white").pack(anchor="w")
            tk.Label(card, text=f"Especialidad: {r['especialidad']} | WhatsApp: {r['contacto']}", font=("Helvetica", 8, "italic"), fg="#555", bg="white").pack(anchor="w")

    # ==================== VISTA 3: PANEL DE COCINA ====================
    def mostrar_vista_cocina(self):
        self.limpiar_contenedor()

        tk.Label(self.main_container, text="Panel de Cocina: Órdenes por Prioridad Clínica", font=("Helvetica", 10, "bold"), fg="#1B5E20", bg="#F4F6F5").pack(anchor="w", pady=5)
        
        cola_ordenada = sorted(ORDER_QUEUE, key=lambda x: (x['prioridad'], x['hora']))

        for orden in cola_ordenada:
            color_fondo = "#FFEBEE" if orden['prioridad'] == 1 else "white"
            card = tk.Frame(self.main_container, bg=color_fondo, bd=1, relief="solid", padx=10, pady=8)
            card.pack(fill="x", pady=4)

            tk.Label(card, text=f"[{orden['id']}] - Estado: {orden['estado']} ({orden['hora']})", font=("Helvetica", 9, "bold"), bg=color_fondo).pack(anchor="w")
            tk.Label(card, text=f"Plato: {orden['plato']}", font=("Helvetica", 9), bg=color_fondo).pack(anchor="w")
            tk.Label(card, text=f"Prioridad: {orden['prioridad_txt']} | Patología: {orden['patologia']}", font=("Helvetica", 8, "italic"), fg="#C62828" if orden['prioridad']==1 else "#333", bg=color_fondo).pack(anchor="w")

    # ==================== VISTA 4: RESEÑA E INSTITUCIONAL ====================
    def mostrar_resena(self):
        self.limpiar_contenedor()

        tk.Label(self.main_container, text="Compromiso NutriSalud con Venezuela", font=("Helvetica", 11, "bold"), fg="#1B5E20", bg="#F4F6F5").pack(anchor="w", pady=4)
        
        texto_resena = (
            "NutriSalud Venezuela (COMPANIA HCHFA CA / Alimentos HCHF4 CA) nace con la misión "
            "de transformar la nutrición clínica y terapéutica en el país.\n\n"
            "Sabemos que para un paciente con Enfermedad Renal Crónica, Diabetes, Hipertensión "
            "o Celiaquía, la alimentación no es un lujo, sino una parte fundamental de su "
            "tratamiento médico. Nuestra red articula la supervisión médica, la elaboración "
            "en cocinas aliadas con estrictos protocolos de bioseguridad y la entrega "
            "priorizada a domicilio en los 24 estados de Venezuela.\n\n"
            "Unimos la tecnología HealthTech con el compromiso humano de cuidar la vida "
            "de cada venezolano."
        )
        
        lbl = tk.Label(self.main_container, text=texto_resena, font=("Helvetica", 9), bg="white", fg="#333333", relief="solid", bd=1, padx=12, pady=12, justify="left", wraplength=440)
        lbl.pack(fill="both", expand=True, pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = NutriSaludApp(root)
    root.mainloop()
