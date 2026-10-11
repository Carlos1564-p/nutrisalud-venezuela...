import streamlit as st
import urllib.parse

# Configuración de la página web
st.set_page_config(page_title="NutriSalud Venezuela", page_icon="🥗", layout="centered")

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

# Base de Datos Completa de Menús Clínicos Especializados (6 por patología)
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

# Directorio Nacional de Restaurantes y Dark Kitchens
DIRECTORIO_RESTAURANTES = [
    {"nombre": "NutriKitchen Chacao", "estado": "Distrito Capital", "municipio": "Chacao", "parroquia": "El Recreo / Chacao", "especialidad": "Renal y Diabetes", "contacto": "04120582064"},
    {"nombre": "Vida Sana El Viñedo", "estado": "Carabobo", "municipio": "Valencia", "parroquia": "San José", "especialidad": "Hipertensión y Sin Gluten", "contacto": "04124445566"},
    {"nombre": "Sabor Clínico Maracaibo", "estado": "Zulia", "municipio": "Maracaibo", "parroquia": "Olegario Villalobos", "especialidad": "Diabetes y Renal", "contacto": "04146667788"},
    {"nombre": "Cocina Terapéutica Barquisimeto", "estado": "Lara", "municipio": "Iribarren", "parroquia": "Catedral", "especialidad": "Multicondición", "contacto": "04169990011"},
    {"nombre": "NutriSalud Puerto La Cruz", "estado": "Anzoátegui", "municipio": "Sotillo", "parroquia": "Puerto La Cruz", "especialidad": "Sin Gluten y Cardio", "contacto": "04248889900"}
]

# Encabezado Principal
st.title("🥗 NutriSalud Venezuela")
st.caption(f"{DATOS_PAGO_BDV['empresa']} | RIF: {DATOS_PAGO_BDV['rif']}")
st.markdown("---")

# Barra de Navegación lateral
opcion = st.sidebar.radio("Navegación", ["🛒 Pedir Menú Clínico", "🏪 Directorio Nacional", "ℹ️ Compromiso con Venezuela"])

if opcion == "🛒 Pedir Menú Clínico":
    st.header("Seleccione Condición Médica / Patología")
    patologia = st.selectbox("Patología:", list(MENU_DATABASE.keys()))
    
    st.subheader(f"Platos Disponibles para: {patologia}")
    platos_disponibles = MENU_DATABASE[patologia]
    
    # Selector de platos
    nombres_platos = [f"{p['nombre']} (${p['precio']:.2f})" for p in platos_disponibles]
    plato_seleccionado_str = st.selectbox("Elige tu platillo terapéutico:", nombres_platos)
    
    # Buscar el plato seleccionado
    plato_obj = next(p for p in platos_disponibles if f"{p['nombre']} (${p['precio']:.2f})" == plato_seleccionado_str)
    
    st.info(f"**Descripción clínica:** {plato_obj['desc']}")
    
    st.markdown("---")
    st.subheader("Datos de Envío y Pago Móvil BDV")
    
    # Acordeón con datos de pago
    with st.expander("💳 Ver Datos Oficiales para Pagomóvil BDV"):
        st.write(f"**Empresa:** {DATOS_PAGO_BDV['empresa']}")
        st.write(f"**RIF:** {DATOS_PAGO_BDV['rif']}")
        st.write(f"**Banco:** {DATOS_PAGO_BDV['banco']}")
        st.write(f"**Teléfono:** {DATOS_PAGO_BDV['telefono']}")
        st.write(f"**Correo:** {DATOS_PAGO_BDV['email']}")
        st.success("Escanee el código QR oficial de la empresa desde su aplicación bancaria para realizar el pago inmediato.")

    # Formulario completo con los 24 estados
    estado_destino = st.selectbox("Seleccione su Estado en Venezuela:", ESTADOS_VENEZUELA)
    direccion = st.text_input("Dirección exacta (Municipio, Parroquia, Urbanización/Calle, Casa/Edif):")
    instrucciones = st.text_input("Instrucciones médicas especiales (Ej. Sin sal añadida, empaque sellado):", "Ninguna")
    referencia_pago = st.text_input("Nro. de Referencia de Pagomóvil BDV:")

    if st.button("🚀 Confirmar Pedido y Enviar a WhatsApp"):
        if not direccion or not referencia_pago:
            st.error("Por favor complete la dirección exacta y el número de referencia del Pagomóvil.")
        else:
            mensaje = (
                f"*[NUEVO PEDIDO - NUTRISALUD VENEZUELA]*\n"
                f"🍽️ Plato: {plato_obj['nombre']} (${plato_obj['precio']:.2f})\n"
                f"🩺 Patología: {patologia}\n"
                f"📍 Estado: {estado_destino}\n"
                f"🏠 Dirección: {direccion}\n"
                f"📝 Nota: {instrucciones}\n"
                f"💳 Ref BDV: {referencia_pago}\n"
                f"🏢 RIF Destino: {DATOS_PAGO_BDV['rif']}"
            )
            url_wsp = f"https://wa.me/{DATOS_PAGO_BDV['telefono']}?text={urllib.parse.quote(mensaje)}"
            st.success("¡Pedido registrado exitosamente en el sistema!")
            st.markdown(f"[📲 **Haga clic aquí para enviar su pedido por WhatsApp**]({url_wsp})")

elif opcion == "🏪 Directorio Nacional":
    st.header("Directorio Nacional de Dark Kitchens Aliadas")
    st.write("Red certificada de cocinas especializadas distribuidas para garantizar frescura y cercanía.")
    
    for r in DIRECTORIO_RESTAURANTES:
        with st.container():
            st.markdown(f"### 🍳 {r['nombre']}")
            st.write(f"* **Estado:** {r['estado']}")
            st.write(f"* **Municipio / Parroquia:** {r['municipio']} - {r['parroquia']}")
            st.write(f"* **Especialidad:** {r['especialidad']}")
            st.write(f"* **Contacto WhatsApp:** `{r['contacto']}`")
            st.markdown("---")

elif opcion == "ℹ️ Compromiso con Venezuela":
    st.header("Compromiso NutriSalud con la Salud de los Venezolanos")
    st.markdown(
        f"**NutriSalud Venezuela** (**{DATOS_PAGO_BDV['empresa']}**, RIF: `{DATOS_PAGO_BDV['rif']}`) "
        "nace con la firme convicción de transformar la nutrición clínica y terapéutica en el país.\n\n"
        "Sabemos que para un paciente con Enfermedad Renal Crónica, Diabetes, Hipertensión Severa "
        "o Celiaquía, la alimentación no es un lujo, sino una parte fundamental e irremplazable "
        "de su tratamiento médico.\n\n"
        "Nuestra plataforma articula la supervisión clínica, la elaboración en cocinas aliadas "
        "bajo estrictos protocolos de bioseguridad y control nutricional, y una red de entrega "
        "priorizada que cubre los **24 estados de Venezuela**. Unimos la tecnología HealthTech "
        "con el compromiso humano de cuidar la salud y el bienestar de cada familia venezolana."
    )
