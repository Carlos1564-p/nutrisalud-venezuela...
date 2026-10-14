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
    "email": "alimentoshchf4@gmail.com"
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
# 3. ENCABEZADO Y TASA DE CAMBIO DINÁMICA
# ==========================================
st.sidebar.title("⚙️ Panel de Control")

# Actualización del Dólar del día
tasa_dolar = st.sidebar.number_input(
    "Tasa de Cambio del Día (VES/USD):", 
    min_value=1.0, 
    value=36.50, 
    step=0.50,
    help="Modifique este valor para recalcular el catálogo completo en Bolívares."
)

st.title("🥗 NutriSalud Digital")
st.caption(f"{DATOS_ADMIN['empresa']} | RIF: {DATOS_ADMIN['rif']}")
st.markdown("---")

# Navegación Principal
opcion = st.sidebar.radio(
    "Navegación", 
    ["🛒 Realizar Pedido", "📋 Pedidos en Cola", "👤 Registro de Clientes", "🏪 Directorio Aliados"]
)

# ==========================================
# 4. MÓDULO: REALIZAR PEDIDO
# ==========================================
if opcion == "🛒 Realizar Pedido":
    st.header("🛒 Módulo de Pedidos Terapéuticos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Selección Médica y Menú")
        patologia = st.selectbox("Condición Médica:", list(MENU_BASE.keys()))
        
        platos_disponibles = MENU_BASE[patologia]
        opciones_platos = [f"{p['nombre']} - ${p['precio_usd']:.2f} USD" for p in platos_disponibles]
        plato_seleccionado = st.selectbox("Seleccione el Platillo:", opciones_platos)
        
        # Obtener objeto del plato seleccionado
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
        
        tipo_entrega = st.radio("Modalidad de Entrega:", ["Delivery a Domicilio", "Pick-Up / Retiro en Restaurante"])
        direccion = st.text_input("Dirección de Entrega / Notas:", "Retiro en Local" if tipo_entrega == "Pick-Up / Retiro en Restaurante" else "")
        tiempo_espera = st.select_slider(
            "Tiempo Máximo de Espera Disponible:",
            options=["30-45 min", "45-60 min", "1-2 Horas", "Programado para la Cena/Almuerzo"]
        )

    st.markdown("---")
    st.subheader("3. Pago Móvil BDV y Confirmación")
    
    with st.expander("💳 Ver Datos Bancarios Oficiales BDV"):
        st.write(f"**Empresa:** {DATOS_ADMIN['empresa']}")
        st.write(f"**RIF:** {DATOS_ADMIN['rif']}")
        st.write(f"**Banco:** {DATOS_ADMIN['banco']}")
        st.write(f"**Teléfono BDV:** {DATOS_ADMIN['telefono']}")
        st.info(f"Monto exacto a transferir: **{precio_ves:,.2f} VES**")

    ref_pago = st.text_input("Número de Referencia Pagomóvil BDV:")

    if st.button("🚀 Procesar y Generar Notificaciones de WhatsApp"):
        if not nombre_cliente or not cedula_cliente or not ref_pago:
            st.error("Por favor complete los datos obligatorios del cliente y el número de referencia.")
        else:
            # Obtener datos del restaurante asignado a ese estado
            aliado = RESTAURANTE_ALIADOS.get(estado_destino, {"nombre": "Cocina Central NutriSalud", "telefono": DATOS_ADMIN['telefono']})
            
            # Guardar en Base de Datos
            conn = sqlite3.connect('nutrisalud_database.db')
            c = conn.cursor()
            
            # Registrar/Actualizar Cliente
            c.execute('''
                INSERT OR REPLACE INTO clientes (nombre, cedula_rif, telefono, estado, patologia_principal)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombre_cliente, cedula_cliente, telefono_cliente, estado_destino, patologia))
            
            # Registrar Pedido
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute('''
                INSERT INTO pedidos (fecha, cliente_nombre, patologia, plato, restaurante_aliado, tipo_entrega, tiempo_espera, monto_usd, monto_ves, ref_pago, estatus)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (fecha_actual, nombre_cliente, patologia, plato_obj['nombre'], aliado['nombre'], tipo_entrega, tiempo_espera, plato_obj['precio_usd'], precio_ves, ref_pago, "En Cola"))
            
            conn.commit()
            conn.close()
            
            st.balloons()
            st.success("✅ Pedido registrado exitosamente en el sistema.")
            
            # Construcción de Mensajes de WhatsApp
            mensaje_pedido = (
                f"*[NUEVO PEDIDO NUTRISALUD DIGITAL]*\n\n"
                f"👤 *Cliente:* {nombre_cliente} ({cedula_cliente})\n"
                f"🍽️ *Plato:* {plato_obj['nombre']}\n"
                f"🩺 *Condición:* {patologia}\n"
                f"📍 *Estado:* {estado_destino}\n"
                f"🛵 *Modo:* {tipo_entrega}\n"
                f"🏠 *Dirección:* {direccion}\n"
                f"⏳ *Tiempo Espera:* {tiempo_espera}\n"
                f"💵 *Monto:* ${plato_obj['precio_usd']:.2f} USD ({precio_ves:,.2f} VES)\n"
                f"💳 *Ref BDV:* {ref_pago}\n"
                f"🍳 *Cocina Asignada:* {aliado['nombre']}"
            )
            
            url_wsp_aliado = f"https://wa.me/58{aliado['telefono'][1:]}?text={urllib.parse.quote(mensaje_pedido)}"
            url_wsp_admin = f"https://wa.me/58{DATOS_ADMIN['telefono'][1:]}?text={urllib.parse.quote(mensaje_pedido)}"

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                st.markdown(f"[📲 **Notificar al Restaurante Aliado ({aliado['nombre']})**]({url_wsp_aliado})")
            with col_btn2:
                st.markdown(f"[🏢 **Enviar Copia de Auditoría a Administración**]({url_wsp_admin})")

# ==========================================
# 5. MÓDULO: PEDIDOS EN COLA
# ==========================================
elif opcion == "📋 Pedidos en Cola":
    st.header("📋 Monitoreo de Pedidos en Cola y Estatus")
    
    conn = sqlite3.connect('nutrisalud_database.db')
    df_pedidos = pd.read_sql_query("SELECT * FROM pedidos ORDER BY id DESC", conn)
    conn.close()
    
    if not df_pedidos.empty:
        st.dataframe(df_pedidos, use_container_width=True)
        
        st.subheader("Gestión de Estatus de Pedidos")
        col_id, col_estatus, col_btn = st.columns(3)
        with col_id:
            pedido_id = st.number_input("ID del Pedido:", min_value=int(df_pedidos['id'].min()), max_value=int(df_pedidos['id'].max()), step=1)
        with col_estatus:
            nuevo_estatus = st.selectbox("Cambiar Estatus:", ["En Cola", "En Preparación", "En Camino", "Entregado", "Cancelado"])
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
# 6. MÓDULO: REGISTRO DE CLIENTES
# ==========================================
elif opcion == "👤 Registro de Clientes":
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
# 7. MÓDULO: DIRECTORIO NACIONAL
# ==========================================
elif opcion == "🏪 Directorio Aliados":
    st.header("🏪 Cobertura y Red de Dark Kitchens Certificadas")
    for estado, data in RESTAURANTES_ALIADOS.items():
        st.write(f"• **{data['nombre']}** | Estado: {estado} | Contacto WhatsApp: `{data['telefono']}`")
