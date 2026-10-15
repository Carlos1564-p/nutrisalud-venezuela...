import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN INICIAL Y BASE DE DATOS
# ==========================================
st.set_page_config(
    page_title="NutriSalud Digital", 
    page_icon="🥗", 
    layout="wide"
)

# Inicializar Base de Datos SQLite y Estructuras de Costos
def init_db():
    conn = sqlite3.connect('nutrisalud_database.db')
    c = conn.cursor()
    
    # Tabla de Clientes
    c.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula_rif TEXT UNIQUE NOT NULL,
            telefono TEXT NOT NULL,
            estado TEXT NOT NULL,
            patologia_principal TEXT
        )
    ''')
    
    # Tabla de Restaurantes Aliados
    c.execute('''
        CREATE TABLE IF NOT EXISTS restaurantes_afiliados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_registro TEXT,
            nombre_comercial TEXT NOT NULL,
            rif TEXT UNIQUE NOT NULL,
            representante TEXT NOT NULL,
            estado TEXT NOT NULL,
            telefono TEXT NOT NULL,
            email TEXT NOT NULL,
            acepto_terminos TEXT NOT NULL
        )
    ''')
    
    # Tabla de Catálogo de Menús y Costos (Modificable por Admin)
    c.execute('''
        CREATE TABLE IF NOT EXISTS menu_platos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            nombre_plato TEXT NOT NULL,
            precio_usd REAL NOT NULL
        )
    ''')
    
    # Poblar menú inicial si está vacío
    c.execute("SELECT COUNT(*) FROM menu_platos")
    if c.fetchone()[0] == 0:
        menu_inicial = [
            ("Fitness y Deportistas / Alto Rendimiento", "Power Bowl: Pechuga a la Plancha, Arroz Integral y Brócoli", 7.50),
            ("Fitness y Deportistas / Alto Rendimiento", "Filet de Res Lean con Puré de Batata y Espinaca", 9.00),
            ("Fitness y Deportistas / Alto Rendimiento", "Tortilla Proteica de Claras, Avena y Frutos Rojos", 5.50),
            ("Fitness y Deportistas / Alto Rendimiento", "Salmón Grillado con Quínoa y Espárragos", 10.00),
            ("Diabetes Tipo 2", "Bowl de Quinua y Pechuga al Limón", 6.50),
            ("Diabetes Tipo 2", "Salmón al Horno con Vegetales", 8.00),
            ("Diabetes Tipo 2", "Pechuga en Reducción de Balsámico", 7.00),
            ("Enfermedad Renal Crónica", "Crema de Calabacín (Bajo Potasio)", 5.00),
            ("Enfermedad Renal Crónica", "Pollo Acorazonado con Arroz Blanco", 6.00),
            ("Enfermedad Renal Crónica", "Tortilla de Claras con Zanahoria", 4.50),
            ("Hipertensión Severa", "Ensalada Mediterránea de Oliva", 5.50),
            ("Hipertensión Severa", "Pavo a las Finas Hierbas", 7.00),
            ("Hipertensión Severa", "Crema suave de Auyama sin Sal", 5.00),
            ("Celiaquía / Sin Gluten", "Pasta de Garbanzos con Pesto", 6.80),
            ("Celiaquía / Sin Gluten", "Milanesa de Pollo con Harina de Yuca", 6.20),
            ("Celiaquía / Sin Gluten", "Risotto de Hongos Portobello", 8.00)
        ]
        c.executemany("INSERT INTO menu_platos (categoria, nombre_plato, precio_usd) VALUES (?, ?, ?)", menu_inicial)

    # Tabla de Pedidos
    c.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            cliente_nombre TEXT,
            patologia TEXT,
            plato TEXT,
            restaurante_aliado TEXT,
            tipo_entrega TEXT,
            tiempo_espera TEXT,
            monto_usd REAL,
            monto_ves REAL,
            comision_plataforma_usd REAL,
            pago_neto_aliado_usd REAL,
            ref_pago TEXT,
            estatus TEXT
        )
    ''')
    
    # Migración de columnas de pedidos si es necesario
    c.execute("PRAGMA table_info(pedidos);")
    columnas_existentes = [col[1] for col in c.fetchall()]
    if "comision_plataforma_usd" not in columnas_existentes:
        c.execute("ALTER TABLE pedidos ADD COLUMN comision_plataforma_usd REAL DEFAULT 0.0;")
    if "pago_neto_aliado_usd" not in columnas_existentes:
        c.execute("ALTER TABLE pedidos ADD COLUMN pago_neto_aliado_usd REAL DEFAULT 0.0;")
        
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. CONFIGURACIÓN Y CONSTANTES
# ==========================================
DATOS_ADMIN = {
    "empresa": "COMPANIA HCHFA CA (Alimentos HCHF4 CA)",
    "rif": "J-404509216",
    "banco": "Banco de Venezuela (0102)",
    "telefono": "04120582064",
    "email": "alimentoshchf4@gmail.com",
    "password_admin": "Admin2026*"
}

ESTADOS_VENEZUELA = [
    "Amazonas", "Anzoátegui", "Apure", "Aragua", "Barinas", "Bolívar", 
    "Carabobo", "Cojedes", "Delta Amacuro", "Distrito Capital", "Falcón", 
    "Guárico", "La Guaira", "Lara", "Mérida", "Miranda", "Monagas", 
    "Nueva Esparta", "Portuguesa", "Sucre", "Táchira", "Trujillo", "Yaracuy", "Zulia"
]

def obtener_restaurantes_aliados():
    conn = sqlite3.connect('nutrisalud_database.db')
    df = pd.read_sql_query("SELECT estado, nombre_comercial, telefono FROM restaurantes_afiliados", conn)
    conn.close()
    
    aliados = {
        "Distrito Capital": {"nombre": "NutriKitchen Chacao", "telefono": "04120582064"},
        "Carabobo": {"nombre": "Vida Sana El Viñedo", "telefono": "04124445566"},
        "Zulia": {"nombre": "Sabor Clínico Maracaibo", "telefono": "04146667788"},
        "Lara": {"nombre": "Cocina Terapéutica Barquisimeto", "telefono": "04169990011"},
        "Anzoátegui": {"nombre": "NutriSalud Puerto La Cruz", "telefono": "04248889900"}
    }
    
    for est in ESTADOS_VENEZUELA:
        if est not in aliados:
            aliados[est] = {"nombre": f"Cocina Matriz NutriSalud ({est})", "telefono": DATOS_ADMIN['telefono']}
            
    for _, row in df.iterrows():
        aliados[row['estado']] = {"nombre": row['nombre_comercial'], "telefono": row['telefono']}
        
    return aliados

def obtener_menu_desde_db():
    conn = sqlite3.connect('nutrisalud_database.db')
    df = pd.read_sql_query("SELECT * FROM menu_platos", conn)
    conn.close()
    
    menu = {}
    for cat in df['categoria'].unique():
        platos = df[df['categoria'] == cat]
        menu[cat] = [{"nombre": row['nombre_plato'], "precio_usd": row['precio_usd'], "id": row['id']} for _, row in platos.iterrows()]
    return menu

# ==========================================
# 3. CONTROL DE ACCESO Y TASA BCV
# ==========================================
st.sidebar.image("logonutrisalud.png", use_container_width=True)
st.sidebar.title("🔐 Panel de Control")

# Control de Tasa del Dólar BCV (Por defecto o modificable por Admin)
if 'tasa_bcv' not in st.session_state:
    st.session_state.tasa_bcv = 36.50

modo_usuario = st.sidebar.radio("Seleccione Perfil:", ["Público (Clientes)", "Administración Central"])

es_admin = False
if modo_usuario == "Administración Central":
    pwd_ingresada = st.sidebar.text_input("Ingrese Clave de Administrador:", type="password")
    if pwd_ingresada == DATOS_ADMIN["password_admin"]:
        es_admin = True
        st.sidebar.success("✅ Acceso de Administrador Concedido")
    elif pwd_ingresada != "":
        st.sidebar.error("❌ Contraseña incorrecta")

if es_admin:
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Configuración Admin")
    st.session_state.tasa_bcv = st.sidebar.number_input(
        "Modificar Tasa del Dólar BCV (VES):", 
        min_value=1.0, 
        value=st.session_state.tasa_bcv, 
        step=0.50
    )
    
    opcion = st.sidebar.radio(
        "Módulos de Gestión", 
        [
            "📋 Pedidos en Cola & Liquidaciones", 
            "👤 Registro de Clientes", 
            "⚙️ Gestión de Menús y Costos", 
            "🤝 Módulo de Afiliación B2B", 
            "📄 Contrato Marco de Adhesión"
        ]
    )
else:
    opcion = "🛒 Realizar Pedido"
    st.sidebar.markdown("---")
    st.sidebar.info(f"📊 **Tasa Oficial BCV del Día:** {st.session_state.tasa_bcv:,.2f} VES/USD")

st.title("🥗 NutriSalud Digital")
st.caption(f"{DATOS_ADMIN['empresa']} | RIF: {DATOS_ADMIN['rif']} | Tasa BCV Oficial: {st.session_state.tasa_bcv:,.2f} VES/USD")
st.markdown("---")

# ==========================================
# 4. MÓDULO PÚBLICO: REALIZAR PEDIDO
# ==========================================
if opcion == "🛒 Realizar Pedido":
    st.header("🛒 Módulo de Pedidos Terapéuticos y Fitness")
    st.info(f"💡 Pagos centralizados a través de {DATOS_ADMIN['empresa']}. Tasa de conversión aplicada: {st.session_state.tasa_bcv:,.2f} VES por USD.")
    
    MENU_BASE = obtener_menu_desde_db()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Selección de Categoría y Menú")
        patologia = st.selectbox("Objetivo / Condición:", list(MENU_BASE.keys()))
        
        platos_disponibles = MENU_BASE[patologia]
        opciones_platos = [f"{p['nombre']} - ${p['precio_usd']:.2f} USD" for p in platos_disponibles]
        plato_seleccionado = st.selectbox("Seleccione el Platillo:", opciones_platos)
        
        idx = opciones_platos.index(plato_seleccionado)
        plato_obj = platos_disponibles[idx]
        precio_ves = plato_obj["precio_usd"] * st.session_state.tasa_bcv
        
        st.success(f"💰 **Precio Ref:** ${plato_obj['precio_usd']:.2f} USD | **Total a Pagar:** {precio_ves:,.2f} VES")

    with col2:
        st.subheader("2. Datos del Cliente y Entrega")
        nombre_cliente = st.text_input("Nombre Completo:")
        cedula_cliente = st.text_input("Cédula o RIF:")
        telefono_cliente = st.text_input("Teléfono de Contacto (Ej: 04121234567):", help="Ingrese su número móvil para recibir la confirmación por WhatsApp.")
        
        estado_destino = st.selectbox("Estado de Venezuela (24 Entidades):", ESTADOS_VENEZUELA)
        
        tipo_entrega = st.radio("Modalidad de Entrega:", ["Delivery a Domicilio", "Pick-Up / Sin Delivery (Retiro en Local)"])
        direccion = st.text_input("Dirección de Entrega / Notas:", "Retiro en Local" if "Sin Delivery" in tipo_entrega else "")
        tiempo_espera = st.select_slider(
            "Tiempo Máximo de Espera Disponible:",
            options=["30-45 min", "45-60 min", "1-2 Horas", "Programado para la Cena/Almuerzo"]
        )

    st.markdown("---")
    st.subheader("3. Pago Móvil BDV Centralizado")
    
    with st.expander("💳 Ver Datos Bancarios Oficiales BDV para el Pago Centralizado"):
        st.write(f"**Empresa:** {DATOS_ADMIN['empresa']}")
        st.write(f"**RIF:** {DATOS_ADMIN['rif']}")
        st.write(f"**Banco:** {DATOS_ADMIN['banco']}")
        st.write(f"**Teléfono BDV:** {DATOS_ADMIN['telefono']}")
        st.info(f"Monto exacto a transferir a la cuenta central: **{precio_ves:,.2f} VES**")

    ref_pago = st.text_input("Número de Referencia Pagomóvil BDV:")

    if st.button("🚀 Procesar Pedido y Enviar a WhatsApp"):
        if not nombre_cliente or not cedula_cliente or not telefono_cliente or not ref_pago:
            st.error("Por favor complete todos los campos obligatorios, incluyendo su teléfono de contacto y referencia.")
        else:
            RESTAURANTES_ALIADOS = obtener_restaurantes_aliados()
            aliado = RESTAURANTES_ALIADOS.get(estado_destino, {"nombre": "Cocina Central NutriSalud", "telefono": DATOS_ADMIN['telefono']})
            
            monto_usd = plato_obj['precio_usd']
            comision_plataforma = monto_usd * 0.10
            pago_neto_aliado = monto_usd * 0.90
            
            conn = sqlite3.connect('nutrisalud_database.db')
            c = conn.cursor()
            
            c.execute('''
                INSERT OR REPLACE INTO clientes (nombre, cedula_rif, telefono, estado, patologia_principal)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombre_cliente, cedula_cliente, telefono_cliente, estado_destino, patologia))
            
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute('''
                INSERT INTO pedidos (fecha, cliente_nombre, patologia, plato, restaurante_aliado, tipo_entrega, tiempo_espera, monto_usd, monto_ves, comision_plataforma_usd, pago_neto_aliado_usd, ref_pago, estatus)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (fecha_actual, nombre_cliente, patologia, plato_obj['nombre'], aliado['nombre'], tipo_entrega, tiempo_espera, monto_usd, precio_ves, comision_plataforma, pago_neto_aliado, ref_pago, "En Cola"))
            
            conn.commit()
            conn.close()
            
            st.balloons()
            st.success("✅ ¡Pedido registrado exitosamente en el sistema central!")
            
            mensaje_aliado = (
                f"*[NUEVO PEDIDO NUTRISALUD DIGITAL]*\n\n"
                f"👤 *Cliente:* {nombre_cliente} ({cedula_cliente})\n"
                f"🍽️ *Plato:* {plato_obj['nombre']}\n"
                f"🏋️ *Categoría / Objetivo:* {patologia}\n"
                f"📍 *Estado:* {estado_destino}\n"
                f"🛵 *Modo:* {tipo_entrega}\n"
                f"🏠 *Dirección:* {direccion}\n"
                f"⏳ *Tiempo Espera:* {tiempo_espera}\n"
                f"💵 *Monto Total:* ${monto_usd:.2f} USD ({precio_ves:,.2f} VES)\n"
                f"💳 *Ref BDV Central:* {ref_pago}\n"
                f"🍳 *Cocina Asignada:* {aliado['nombre']}\n"
                f"💼 *Liquidación Neta Aliado (90%):* ${pago_neto_aliado:.2f} USD"
            )
            
            mensaje_cliente = (
                f"¡Hola *{nombre_cliente}*! 🥗\n\n"
                f"En nombre de *{DATOS_ADMIN['empresa']} (NutriSalud Digital)*, queremos agradecerle profundamente la confianza depositada en nosotros para cuidar su salud y rendimiento físico.\n\n"
                f"✅ *Hemos recibido su pago (Ref: {ref_pago})* y su pedido ya se encuentra **en proceso de elaboración** bajo estrictos estándares clínicos:\n\n"
                f"🍽️ *Plato:* {plato_obj['nombre']}\n"
                f"🏋️ *Objetivo:* {patologia}\n"
                f"📍 *Estado:* {estado_destino}\n"
                f"🛵 *Modalidad:* {tipo_entrega}\n"
                f"⏳ *Tiempo estimado:* {tiempo_espera}\n\n"
                f"Le estaremos notificando en cuanto su menú salga hacia su destino. ¡Gracias por confiar en nuestra tecnología y compromiso nutricional!"
            )
            
            url_wsp_aliado = f"https://wa.me/58{aliado['telefono'][1:]}?text={urllib.parse.quote(mensaje_aliado)}"
            url_wsp_admin = f"https://wa.me/58{DATOS_ADMIN['telefono'][1:]}?text={urllib.parse.quote(mensaje_aliado)}"
            
            tel_cliente_limpio = telefono_cliente.strip()
            if tel_cliente_limpio.startswith("0"):
                tel_cliente_limpio = tel_cliente_limpio[1:]
            url_wsp_cliente = f"https://wa.me/58{tel_cliente_limpio}?text={urllib.parse.quote(mensaje_cliente)}"

            st.markdown("### 📲 Acciones de Notificación por WhatsApp")
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                st.markdown(f"[📲 **Notificar al Aliado**]({url_wsp_aliado})")
            with col_b2:
                st.markdown(f"[💬 **Agradecimiento al Cliente**]({url_wsp_cliente})")
            with col_b3:
                st.markdown(f"[🏢 **Copia de Auditoría Admin**]({url_wsp_admin})")

# ==========================================
# 5. MÓDULO PRIVADO: PEDIDOS EN COLA
# ==========================================
elif opcion == "📋 Pedidos en Cola & Liquidaciones" and es_admin:
    st.header("📋 Monitoreo de Pedidos, Estatus y Liquidación a Aliados")
    
    conn = sqlite3.connect('nutrisalud_database.db')
    df_pedidos = pd.read_sql_query("SELECT * FROM pedidos ORDER BY id DESC", conn)
    conn.close()
    
    if not df_pedidos.empty:
        st.dataframe(df_pedidos, use_container_width=True)
        
        col_id, col_estatus, col_btn = st.columns(3)
        with col_id:
            pedido_id = st.number_input("ID del Pedido:", min_value=int(df_pedidos['id'].min()), max_value=int(df_pedidos['id'].max()), step=1)
        with col_estatus:
            nuevo_estatus = st.selectbox("Cambiar Estatus:", ["En Cola", "En Preparación", "En Camino", "Entregado & Liquidado", "Cancelado"])
        with col_btn:
            st.write("")
            st.write("")
            if st.button("Actualizar Estatus"):
                conn = sqlite3.connect('nutrisalud_database.db')
                c = conn.cursor()
                c.execute("UPDATE pedidos SET estatus = ? WHERE id = ?", (nuevo_estatus, pedido_id))
                conn.commit()
                conn.close()
                st.success(f"Pedido #{pedido_id} actualizado a {nuevo_estatus}")
                st.rerun()
    else:
        st.info("No hay pedidos registrados.")

# ==========================================
# 6. MÓDULO PRIVADO: REGISTRO DE CLIENTES
# ==========================================
elif opcion == "👤 Registro de Clientes" and es_admin:
    st.header("👤 Base de Datos Activa de Clientes Registrados")
    conn = sqlite3.connect('nutrisalud_database.db')
    df_clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
    conn.close()
    if not df_clientes.empty:
        st.dataframe(df_clientes, use_container_width=True)
    else:
        st.info("Aún no hay clientes registrados.")

# ==========================================
# 7. MÓDULO PRIVADO: GESTIÓN DE MENÚS Y COSTOS (NUEVO)
# ==========================================
elif opcion == "⚙️ Gestión de Menús y Costos" and es_admin:
    st.header("⚙️ Modificación de Estructura de Costos por Plato")
    st.write("Actualice el precio referencial en USD de cada platillo terapéutico o fitness en tiempo real.")
    
    conn = sqlite3.connect('nutrisalud_database.db')
    df_menu = pd.read_sql_query("SELECT * FROM menu_platos", conn)
    conn.close()
    
    st.dataframe(df_menu, use_container_width=True)
    
    st.markdown("---")
    st.subheader("✏️ Editar Precio de Platillo Individual")
    
    with st.form("form_editar_precio"):
        plato_a_editar = st.selectbox("Seleccione el Platillo:", df_menu['nombre_plato'].tolist())
        
        # Buscar precio actual
        precio_actual = float(df_menu[df_menu['nombre_plato'] == plato_a_editar]['precio_usd'].values[0])
        nuevo_precio_usd = st.number_input("Nuevo Precio en USD ($):", min_value=0.50, value=precio_actual, step=0.50)
        
        btn_actualizar_precio = st.form_submit_button("💾 Actualizar Estructura de Costo")
        
        if btn_actualizar_precio:
            conn = sqlite3.connect('nutrisalud_database.db')
            c = conn.cursor()
            c.execute("UPDATE menu_platos SET precio_usd = ? WHERE nombre_plato = ?", (nuevo_precio_usd, plato_a_editar))
            conn.commit()
            conn.close()
            st.success(f"✅ ¡Precio del plato '{plato_a_editar}' actualizado exitosamente a ${nuevo_precio_usd:.2f} USD!")
            st.rerun()

# ==========================================
# 8. MÓDULO PRIVADO: AFILIACIÓN B2B
# ==========================================
elif opcion == "🤝 Módulo de Afiliación B2B" and es_admin:
    st.header("🤝 Módulo de Afiliación Digital de Restaurantes y Dark Kitchens")
    with st.form("form_afiliacion"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            nombre_comercial = st.text_input("Nombre Comercial del Restaurante:")
            rif_restaurante = st.text_input("RIF del Establecimiento:")
            representante_legal = st.text_input("Representante Legal:")
        with col_f2:
            estado_operacion = st.selectbox("Estado de Operación:", ESTADOS_VENEZUELA)
            telefono_contacto = st.text_input("Teléfono / WhatsApp:")
            email_contacto = st.text_input("Correo Electrónico:")
            
        acepto_contrato = st.checkbox("✅ Acepta términos de comisión (10/90) y responsabilidad sanitaria e inocuidad.")
        btn_reg = st.form_submit_button("📝 Registrar Aliado")
        
        if btn_reg:
            if not nombre_comercial or not rif_restaurante or not acepto_contrato:
                st.error("Complete los campos obligatorios y acepte el contrato.")
            else:
                try:
                    conn = sqlite3.connect('nutrisalud_database.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO restaurantes_afiliados (fecha_registro, nombre_comercial, rif, representante, estado, telefono, email, acepto_terminos) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nombre_comercial, rif_restaurante, representante_legal, estado_operacion, telefono_contacto, email_contacto, "SÍ - ACEPTADO"))
                    conn.commit()
                    conn.close()
                    st.success(f"🎉 Restaurante {nombre_comercial} afiliado con éxito.")
                except sqlite3.IntegrityError:
                    st.error("❌ Ya existe un restaurante con este RIF.")

    st.subheader("Listado de Aliados")
    conn = sqlite3.connect('nutrisalud_database.db')
    st.dataframe(pd.read_sql_query("SELECT * FROM restaurantes_afiliados", conn), use_container_width=True)
    conn.close()

# ==========================================
# 9. MÓDULO PRIVADO: CONTRATO MARCO
# ==========================================
elif opcion == "📄 Contrato Marco de Adhesión" and es_admin:
    st.header("📄 Contrato Marco de Adhesión y Comisiones (90/10)")
    st.markdown(
        f"""
        ### ACUERDO COMERCIAL Y SANITARIO B2B
        **{DATOS_ADMIN['empresa']} (RIF: {DATOS_ADMIN['rif']})**
        * **Comisión Plataforma:** 10%
        * **Liquidación Aliado:** 90%
        * **Inocuidad y Sanidad:** Responsabilidad exclusiva del restaurante aliado.
        """
    )
