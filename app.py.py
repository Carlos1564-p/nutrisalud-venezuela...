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

# Inicializar Base de Datos SQLite
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
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. DATOS DE CONFIGURACIÓN Y CONSTANTES
# ==========================================
DATOS_ADMIN = {
    "empresa": "COMPANIA HCHFA CA (Alimentos HCHF4 CA)",
    "rif": "J-404509216",
    "banco": "Banco de Venezuela (0102)",
    "telefono": "04120582064",
    "email": "alimentoshchf4@gmail.com",
    "password_admin": "Admin2026*"  # Contraseña secreta para ver módulos administrativos
}

ESTADOS_VENEZUELA = [
    "Amazonas", "Anzoátegui", "Apure", "Aragua", "Barinas", "Bolívar", 
    "Carabobo", "Cojedes", "Delta Amacuro", "Distrito Capital", "Falcón", 
    "Guárico", "Lara", "Mérida", "Miranda", "Monagas", "Nueva Esparta", 
    "Portuguesa", "Sucre", "Táchira", "Trujillo", "La Guaira", "Yaracuy", "Zulia"
]

RESTAURANTES_ALIADOS = {
    "Distrito Capital": {"nombre": "NutriKitchen Chacao", "telefono": "04120582064"},
    "Carabobo": {"nombre": "Vida Sana El Viñedo", "telefono": "04124445566"},
    "Zulia": {"nombre": "Sabor Clínico Maracaibo", "telefono": "04146667788"},
    "Lara": {"nombre": "Cocina Terapéutica Barquisimeto", "telefono": "04169990011"},
    "Anzoátegui": {"nombre": "NutriSalud Puerto La Cruz", "telefono": "04248889900"}
}

MENU_BASE = {
    "Diabetes Tipo 2": [
        {"nombre": "Bowl de Quinua y Pechuga al Limón", "precio_usd": 6.50},
        {"nombre": "Salmón al Horno con Vegetales", "precio_usd": 8.00},
        {"nombre": "Pechuga en Reducción de Balsámico", "precio_usd": 7.00}
    ],
    "Enfermedad Renal Crónica": [
        {"nombre": "Crema de Calabacín (Bajo Potasio)", "precio_usd": 5.00},
        {"nombre": "Pollo Acorazonado con Arroz Blanco", "precio_usd": 6.00},
        {"nombre": "Tortilla de Claras con Zanahoria", "precio_usd": 4.50}
    ],
    "Hipertensión Severa": [
        {"nombre": "Ensalada Mediterránea de Oliva", "precio_usd": 5.50},
        {"nombre": "Pavo a las Finas Hierbas", "precio_usd": 7.00},
        {"nombre": "Crema suave de Auyama sin Sal", "precio_usd": 5.00}
    ],
    "Celiaquía / Sin Gluten": [
        {"nombre": "Pasta de Garbanzos con Pesto", "precio_usd": 6.80},
        {"nombre": "Milanesa de Pollo con Harina de Yuca", "precio_usd": 6.20},
        {"nombre": "Risotto de Hongos Portobello", "precio_usd": 8.00}
    ]
}

# ==========================================
# 3. CONTROL DE ACCESO (LOGIN DE ADMINISTRADOR)
# ==========================================
st.sidebar.image("Logo Agrodigitalvenezueladeinitivo.png", use_container_width=True)
st.sidebar.title("🔐 Panel de Control")

# Control de Tasa de Cambio (Visible o editable con clave o por defecto)
tasa_dolar = st.sidebar.number_input(
    "Tasa de Cambio del Día (VES/USD):", 
    min_value=1.0, 
    value=36.50, 
    step=0.50
)

st.sidebar.markdown("---")
st.sidebar.subheader("Acceso a Módulos")
modo_usuario = st.sidebar.radio("Seleccione Perfil:", ["Público (Clientes)", "Administración Central"])

es_admin = False
if modo_usuario == "Administración Central":
    pwd_ingresada = st.sidebar.text_input("Ingrese Clave de Administrador:", type="password")
    if pwd_ingresada == DATOS_ADMIN["password_admin"]:
        es_admin = True
        st.sidebar.success("✅ Acceso de Administrador Concedido")
    elif pwd_ingresada != "":
        st.sidebar.error("❌ Contraseña incorrecta")

# Navegación condicional según rol
if es_admin:
    opcion = st.sidebar.radio(
        "Módulos de Gestión", 
        ["📋 Pedidos en Cola & Liquidaciones", "👤 Registro de Clientes", "📄 Contrato y Acuerdos Comerciales"]
    )
else:
    opcion = "🛒 Realizar Pedido"
    if modo_usuario == "Administración Central":
        st.sidebar.warning("⚠️ Ingrese la contraseña correcta para ver los módulos administrativos.")

st.title("🥗 NutriSalud Digital")
st.caption(f"{DATOS_ADMIN['empresa']} | RIF: {DATOS_ADMIN['rif']}")
st.markdown("---")

# ==========================================
# 4. MÓDULO PÚBLICO: REALIZAR PEDIDO
# ==========================================
if opcion == "🛒 Realizar Pedido":
    st.header("🛒 Módulo de Pedidos Terapéuticos")
    st.info("💡 Su pago es procesado de forma centralizada y segura a través de la cuenta matriz de la empresa. La plataforma articula de forma automatizada la elaboración con la cocina aliada correspondiente.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Selección Médica y Menú")
        patologia = st.selectbox("Condición Médica:", list(MENU_BASE.keys()))
        
        platos_disponibles = MENU_BASE[patologia]
        opciones_platos = [f"{p['nombre']} - ${p['precio_usd']:.2f} USD" for p in platos_disponibles]
        plato_seleccionado = st.selectbox("Seleccione el Platillo:", opciones_platos)
        
        idx = opciones_platos.index(plato_seleccionado)
        plato_obj = platos_disponibles[idx]
        precio_ves = plato_obj["precio_usd"] * tasa_dolar
        
        st.success(f"💰 **Precio Ref:** ${plato_obj['precio_usd']:.2f} USD | **Total a Pagar:** {precio_ves:,.2f} VES")

    with col2:
        st.subheader("2. Datos del Cliente y Entrega")
        nombre_cliente = st.text_input("Nombre Completo:")
        cedula_cliente = st.text_input("Cédula o RIF:")
        telefono_cliente = st.text_input("Teléfono de Contacto (WhatsApp):")
        estado_destino = st.selectbox("Estado de Venezuela:", ESTADOS_VENEZUELA)
        
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
        if not nombre_cliente or not cedula_cliente or not ref_pago:
            st.error("Por favor complete los datos obligatorios del cliente y el número de referencia.")
        else:
            aliado = RESTAURANTES_ALIADOS.get(estado_destino, {"nombre": "Cocina Central NutriSalud", "telefono": DATOS_ADMIN['telefono']})
            
            # Cálculos financieros del negocio (10% comisión plataforma, 90% pago neto al restaurante)
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
            st.success("✅ Pedido registrado exitosamente en el sistema central.")
            
            mensaje_pedido = (
                f"*[NUEVO PEDIDO NUTRISALUD DIGITAL]*\n\n"
                f"👤 *Cliente:* {nombre_cliente} ({cedula_cliente})\n"
                f"🍽️ *Plato:* {plato_obj['nombre']}\n"
                f"🩺 *Condición:* {patologia}\n"
                f"📍 *Estado:* {estado_destino}\n"
                f"🛵 *Modo:* {tipo_entrega}\n"
                f"🏠 *Dirección:* {direccion}\n"
                f"⏳ *Tiempo Espera:* {tiempo_espera}\n"
                f"💵 *Monto Total:* ${monto_usd:.2f} USD ({precio_ves:,.2f} VES)\n"
                f"💳 *Ref BDV Central:* {ref_pago}\n"
                f"🍳 *Cocina Asignada:* {aliado['nombre']}\n"
                f"💼 *Liquidación a transferir al Aliado:* ${pago_neto_aliado:.2f} USD (Neto 90%)"
            )
            
            url_wsp_aliado = f"https://wa.me/58{aliado['telefono'][1:]}?text={urllib.parse.quote(mensaje_pedido)}"
            url_wsp_admin = f"https://wa.me/58{DATOS_ADMIN['telefono'][1:]}?text={urllib.parse.quote(mensaje_pedido)}"

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                st.markdown(f"[📲 **Notificar a la Cocina Aliada ({aliado['nombre']})**]({url_wsp_aliado})")
            with col_btn2:
                st.markdown(f"[🏢 **Enviar Copia de Auditoría a Administración**]({url_wsp_admin})")

# ==========================================
# 5. MÓDULO PRIVADO: PEDIDOS EN COLA & LIQUIDACIONES
# ==========================================
elif opcion == "📋 Pedidos en Cola & Liquidaciones" and es_admin:
    st.header("📋 Monitoreo de Pedidos, Estatus y Liquidación a Aliados")
    st.write("Vista exclusiva para Administración. Control de pagos netos a restaurantes (90%) y retención de comisión (10%).")
    
    conn = sqlite3.connect('nutrisalud_database.db')
    df_pedidos = pd.read_sql_query("SELECT * FROM pedidos ORDER BY id DESC", conn)
    conn.close()
    
    if not df_pedidos.empty:
        st.dataframe(df_pedidos, use_container_width=True)
        
        st.subheader("Gestión de Estatus y Liquidación")
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
        st.info("No hay pedidos registrados en la base de datos.")

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
        st.caption(f"Total de clientes activos registrados: {len(df_clientes)}")
    else:
        st.info("Aún no hay clientes registrados en la base de datos.")

# ==========================================
# 7. MÓDULO PRIVADO: CONTRATO Y ACUERDOS
# ==========================================
elif opcion == "📄 Contrato y Acuerdos Comerciales" and es_admin:
    st.header("📄 Contrato Marco de Confidencialidad, Garantía de Pagos y Comisiones")
    st.markdown(
        f"""
        ### ACUERDO DE ALIANZA COMERCIAL Y PRESTACIÓN DE SERVICIOS HEALTHERS / RESTAURANTES ALIADOS
        **COMPANIA HCHFA CA (RIF: J-404509216)**
        
        ---
        
        **1. OBJETO DEL ACUERDO:**  
        El presente documento establece los términos y condiciones bajo los cuales la red de cocinas aliadas (Dark Kitchens / Restaurantes) procesará los menús terapéuticos y clínicos solicitados a través de la plataforma tecnológica **NutriSalud Digital**, garantizando el cumplimiento estricto de gramajes, patologías y normativas bromatológicas.

        **2. MODELO FINANCIERO Y COMISIONES (10%):**  
        * **Cobro Centralizado:** Todo pago efectuado por el paciente final ingresa de forma centralizada a la cuenta de **COMPANIA HCHFA CA**.
        * **Comisión de la Plataforma:** La plataforma retiene un **10%** del valor total del plato por concepto de articulación de demanda, marketing nacional, pasarela tecnológica y soporte logístico.
        * **Liquidación al Aliado (90%):** La empresa transferirá el **90%** restante al restaurante aliado correspondiente, según los acuerdos de liquidación acordados (diarios o semanales), respaldados mediante comprobantes de pago verificados.

        **3. CONFIDENCIALIDAD Y PROTECCIÓN DE DATOS:**  
        * Las partes se comprometen a mantener estricta confidencialidad sobre la base de datos de pacientes, historiales clínicos, recetas médicas y volúmenes de transacciones gestionados a través del sistema. Queda prohibida la divulgación o uso comercial externo de dicha información.

        **4. GARANTÍA DE CALIDAD Y TIEMPOS:**  
        * El restaurante aliado garantiza la elaboración de los menús conforme a las especificaciones clínicas (Diabetes, Renal, Hipertensión, Celiaquía) y respetando los tiempos de espera seleccionados por el cliente o la modalidad de entrega (Con o sin delivery).
        """
    )
