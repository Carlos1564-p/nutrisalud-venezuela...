import streamlit as st
import urllib.parse

# Configuración de la página web
st.set_page_config(page_title="NutriSalud Venezuela", page_icon="🥗", layout="centered")

# Encabezado Oficial
st.title("🥗 NutriSalud Venezuela")
st.caption("COMPANIA HCHFA CA (Alimentos HCHF4 CA) | RIF: J-404509216")
st.markdown("---")

# Menú lateral para navegación
opcion = st.sidebar.radio("Navegación", ["🛒 Pedir Menú Clínico", "🏪 Directorio Aliados", "ℹ️ Compromiso con Venezuela"])

# DATOS DE PAGO DENTRO DE LA WEB
DATOS_BDV = {
    "empresa": "COMPANIA HCHFA CA",
    "rif": "J-404509216",
    "banco": "Banco de Venezuela (0102)",
    "telefono": "04120582064",
    "email": "alimentoshchf4@gmail.com"
}

if opcion == "🛒 Pedir Menú Clínico":
    st.header("Seleccione su Condición Médica")
    patologia = st.selectbox("Patología / Condición:", ["Diabetes Tipo 2", "Enfermedad Renal Crónica", "Hipertensión Severa", "Celiaquía / Sin Gluten"])
    
    st.subheader("Platos Disponibles")
    if patologia == "Diabetes Tipo 2":
        plato = "Bowl de Quinua y Pechuga al Limón ($6.50)"
    elif patologia == "Enfermedad Renal Crónica":
        plato = "Crema de Calabacín Bajo Potasio ($5.00)"
    elif patologia == "Hipertensión Severa":
        plato = "Ensalada Mediterránea de Oliva ($5.50)"
    else:
        plato = "Pasta de Garbanzos con Pesto ($6.80)"
        
    st.info(f"Plato seleccionado: **{plato}**")
    
    # Formulario de Envío
    st.subheader("Datos de Entrega y Pago Móvil BDV")
    estado = st.selectbox("Estado de Venezuela:", ["Distrito Capital", "Carabobo", "Zulia", "Lara", "Aragua", "Anzoátegui"])
    direccion = st.text_input("Dirección exacta / Parroquia:")
    referencia = st.text_input("Nro. de Referencia de Pagomóvil BDV:")
    
    with st.expander("💳 Ver datos bancarios para Pagomóvil BDV"):
        st.write(f"**Empresa:** {DATOS_BDV['empresa']}")
        st.write(f"**RIF:** {DATOS_BDV['rif']}")
        st.write(f"**Banco:** {DATOS_BDV['banco']}")
        st.write(f"**Teléfono:** {DATOS_BDV['telefono']}")

    if st.button("🚀 Confirmar Pedido vía WhatsApp"):
        if not direccion or not referencia:
            st.error("Por favor ingrese la dirección y la referencia de pago.")
        else:
            mensaje = f"*[NUEVO PEDIDO NUTRISALUD VENEZUELA]*\nPlato: {plato}\nPatología: {patologia}\nEstado: {estado}\nDirección: {direccion}\nRef BDV: {referencia}"
            url_wsp = f"https://wa.me/{DATOS_BDV['telefono']}?text={urllib.parse.quote(mensaje)}"
            st.success("¡Pedido registrado! Haz clic abajo para abrir WhatsApp:")
            st.markdown(f"[📲 **Abrir WhatsApp para Confirmar Orden**]({url_wsp})")

elif opcion == "🏪 Directorio Aliados":
    st.header("Directorio Nacional de Dark Kitchens")
    st.write("• **NutriKitchen Chacao** | Distrito Capital (Chacao) | WA: 04120582064")
    st.write("• **Vida Sana El Viñedo** | Carabobo (Valencia) | WA: 04124445566")

elif opcion == "ℹ️ Compromiso con Venezuela":
    st.header("NutriSalud Venezuela")
    st.write("Transformamos la nutrición clínica y terapéutica en Venezuela llevando platillos especializados a los 24 estados bajo supervisión médica.")
