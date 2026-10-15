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

# Inicializar Base de Datos SQLite y Migración Automática
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
    
    # Tabla de Restaurantes Aliados (Afiliados formalmente)
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
    
    # Verificar y actualizar columnas si la base de datos es de una versión anterior
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
# 2. DATOS DE CONFIGURACIÓN Y CONSTANTES
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
    "Guárico", "Lara", "Mérida", "Miranda", "Monagas", "Nueva Esparta", 
    "Portuguesa", "Sucre", "Táchira", "Trujillo", "La Guaira", "Yaracuy", "Zulia"
]

# Función para cargar aliados desde la BD o usar los base por defecto
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
    
    for _, row in df.iterrows():
        aliados[row['estado']] = {"nombre": row['nombre_comercial'], "telefono": row['telefono']}
    
    return aliados

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
st.sidebar.image("logonutrisalud.png", use_container_width=True)
st.sidebar.title("🔐 Panel de Control")

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

if es_admin:
    opcion = st.sidebar.radio(
        "Módulos de Gestión", 
        [
            "📋 Pedidos en Cola & Liquidaciones", 
            "👤 Registro de Clientes", 
            "🤝 Módulo de Afiliación y Contratos B2B", 
            "📄 Contrato Marco de Adhesión"
        ]
    )
else:
    opcion = "🛒 Realizar Pedido"

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
        telefono_cliente = st.text_input("Teléfono de Contacto (Ej: 04121234567):", help="Ingrese su número móvil para recibir la confirmación por WhatsApp.")
        
        RESTAURANTES_ALIADOS = obtener_restaurantes_aliados()
        estado_destino = st.selectbox("Estado de Venezuela:", list(RESTAURANTES_ALIADOS.keys()))
        
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
                f"🩺 *Condición:* {patologia}\n"
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
                f"En nombre de *{DATOS_ADMIN['empresa']} (NutriSalud Digital)*, queremos agradecerle profundamente la confianza depositada en nosotros para cuidar su salud y garantizarle una vida más saludable y equilibrada.\n\n"
                f"✅ *Hemos recibido su pago (Ref: {ref_pago})* y su pedido ya se encuentra **en proceso de elaboración** bajo estrictos estándares clínicos:\n\n"
                f"🍽️ *Plato:* {plato_obj['nombre']}\n"
                f"🩺 *Condición:* {patologia}\n"
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
            st.write("Haga clic en los siguientes botones para enviar los mensajes correspondientes:")
            
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                st.markdown(f"[📲 **Notificar al Aliado**]({url_wsp_aliado})")
            with col_b2:
                st.markdown(f"[💬 **Enviar Mensaje de Agradecimiento al Cliente**]({url_wsp_cliente})")
            with col_b3:
                st.markdown(f"[🏢 **Copia de Auditoría Admin**]({url_wsp_admin})")

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
# 7. MÓDULO PRIVADO: AFILIACIÓN Y CONTRATOS B2B
# ==========================================
elif opcion == "🤝 Módulo de Afiliación y Contratos B2B" and es_admin:
    st.header("🤝 Módulo de Afiliación Digital de Restaurantes y Dark Kitchens")
    st.write("Registro oficial de nuevos locales aliados bajo el Contrato Marco de Adhesión, Inocuidad Alimentaria y Comisiones (90/10).")
    
    with st.form("form_afiliacion"):
        st.subheader("Datos del Establecimiento Comercial / Aliado")
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            nombre_comercial = st.text_input("Nombre Comercial del Restaurante / Dark Kitchen:")
            rif_restaurante = st.text_input("RIF del Establecimiento (Ej: J-12345678-9):")
            representante_legal = st.text_input("Nombre del Representante Legal:")
            
        with col_f2:
            estado_operacion = st.selectbox("Estado de Operación (Cobertura):", ESTADOS_VENEZUELA)
            telefono_contacto = st.text_input("Teléfono Móvil / WhatsApp del Local:")
            email_contacto = st.text_input("Correo Electrónico Corporativo:")
            
        st.markdown("---")
        st.subheader("📜 Cláusula de Adhesión, Sanidad y Responsabilidad Legal")
        st.info(
            """
            Al registrar y afiliar este establecimiento, el Representante Legal declara conocer y aceptar irrevocablemente:
            1. **Modelo Financiero:** Retención del 10% por parte de la plataforma tecnológica y liquidación del 90% neta al restaurante.
            2. **Responsabilidad Sanitaria e Inocuidad:** El restaurante aliado asume plena, exclusiva e ineludible responsabilidad civil, penal y sanitaria sobre la manipulación, preparación, calidad bromatológica, gramajes, frescura e inocuidad de los alimentos entregados a los pacientes, liberando de toda responsabilidad a **COMPANIA HCHFA CA**.
            3. **Permisología:** El aliado garantiza poseer permisos sanitarios vigentes y cumplir con la Ley de Alimentación y normativas bromatológicas de la República Bolivariana de Venezuela.
            """
        )
        
        acepto_contrato = st.checkbox("✅ El establecimiento declara haber leído, entendido y aceptado formalmente las condiciones de negocio, comisiones y la responsabilidad legal en materia sanitaria y de inocuidad de los alimentos.")
        
        btn_registrar_aliado = st.form_submit_button("📝 Registrar y Afiliar Restaurante Aliado")
        
        if btn_registrar_aliado:
            if not nombre_comercial or not rif_restaurante or not representante_legal or not telefono_contacto:
                st.error("Por favor complete todos los campos obligatorios del establecimiento.")
            elif not acepto_contrato:
                st.error("Debe marcar la casilla de aceptación del Contrato de Adhesión y Responsabilidad Sanitaria para proceder.")
            else:
                try:
                    conn = sqlite3.connect('nutrisalud_database.db')
                    c = conn.cursor()
                    fecha_afiliacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    c.execute('''
                        INSERT INTO restaurantes_afiliados (fecha_registro, nombre_comercial, rif, representante, estado, telefono, email, acepto_terminos)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (fecha_afiliacion, nombre_comercial, rif_restaurante, representante_legal, estado_operacion, telefono_contacto, email_contacto, "SÍ - ACEPTADO"))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success(f"🎉 ¡Restaurante **{nombre_comercial}** afiliado exitosamente para el estado **{estado_operacion}** bajo el Contrato Marco B2B!")
                    st.balloons()
                except sqlite3.IntegrityError:
                    st.error("❌ Error: Ya existe un restaurante registrado con este mismo RIF en el sistema.")

    st.markdown("---")
    st.subheader("📋 Listado de Restaurantes Aliados Activos")
    conn = sqlite3.connect('nutrisalud_database.db')
    df_aliados = pd.read_sql_query("SELECT * FROM restaurantes_afiliados", conn)
    conn.close()
    
    if not df_aliados.empty:
        st.dataframe(df_aliados, use_container_width=True)
    else:
        st.info("No hay restaurantes registrados mediante el módulo digital aún (utilizando los aliados base por defecto).")

# ==========================================
# 8. MÓDULO PRIVADO: CONTRATO MARCO DE ADHESIÓN
# ==========================================
elif opcion == "📄 Contrato Marco de Adhesión" and es_admin:
    st.header("📄 Contrato Marco de Adhesión, Comisiones y Responsabilidad Sanitaria B2B")
    st.markdown(
        f"""
        ### ACUERDO DE ALIANZA COMERCIAL Y PRESTACIÓN DE SERVICIOS HEALTHERS / RESTAURANTES ALIADOS
        **COMPANIA HCHFA CA (RIF: J-404509216)**
        
        ---
        
        **1. OBJETO DEL ACUERDO:**  
        El presente contrato regula los términos y condiciones de la vinculación comercial entre **COMPANIA HCHFA CA** y las cocinas aliadas (*Dark Kitchens* / Restaurantes) que procesarán y despacharán menús clínicos y terapéuticos a través de la plataforma tecnológica **NutriSalud Digital**.

        **2. MODELO FINANCIERO Y COMISIONES (90/10):**  
        * **Centralización de Pagos:** Todos los pagos realizados por los clientes finales son recaudados centralmente por **COMPANIA HCHFA CA**.
        * **Comisión de Plataforma (10%):** La empresa retiene un diez por ciento (10%) del valor total de cada menú procesado por concepto de pasarela tecnológica, marketing nacional y articulación de demanda.
        * **Liquidación Neta al Aliado (90%):** La empresa transfiere el noventa por ciento (90%) restante al restaurante aliado conforme a los cierres y liquidaciones acordadas.

        **3. RESPONSABILIDAD SANITARIA, BROMATOLOGÍA E INOCUIDAD:**  
        * El restaurante aliado asume **total e ineludible responsabilidad legal, civil, administrativa y penal** sobre la manipulación, salubridad, calidad bromatológica, frescura, gramajes y trazabilidad de los alimentos preparados y entregados.
        * El aliado garantiza contar con licencias sanitarias vigentes y cumplir de manera estricta con las leyes alimentarias y de sanidad de la República Bolivariana de Venezuela, eximiendo y blindando por completo a **COMPANIA HCHFA CA** ante cualquier eventualidad bromatológica o sanitaria.

        **4. CONFIDENCIALIDAD:**  
        * Queda estrictamente prohibido el uso comercial externo o divulgación de la base de datos de pacientes, recetas o historiales clínicos gestionados a través de la plataforma.
        """
    )
