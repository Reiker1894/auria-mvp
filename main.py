
import streamlit as st
import os
import json
from openai import OpenAI
import streamlit.components.v1 as components


# --- Funciones

#--- Función para búsquedas en internet
from serpapi import GoogleSearch

def buscar_en_internet(pregunta):
    params = {
        "engine": "google",
        "q": pregunta,
        "location": "Colombia",
        "api_key": os.getenv("fc31febf2316f60e966cac02b07a5faff93038bae595f2cacacb13bf5bed1506")
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        if "organic_results" in results:
            top_result = results["organic_results"][0]
            return f"🔎 **{top_result['title']}**\n{top_result['snippet']}\n[Ver más]({top_result['link']})"
        else:
            return "No encontré resultados relevantes."
    except Exception as e:
        return f"❌ Error al buscar en internet: {e}"




# --- Configuración de página ---
st.set_page_config(page_title="AurIA", page_icon="💰")

# --- Constantes ---
DATA_FILE = "usuarios.json"

# --- Estilos y fondo animado ---
components.html(open("background.html", "r").read(), height=0, width=0)

# --- Funciones de almacenamiento ---
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def guardar_datos(nombre, perfil):
    datos = cargar_datos()
    datos[nombre] = perfil
    with open(DATA_FILE, "w") as f:
        json.dump(datos, f, indent=2)

def obtener_perfil(nombre):
    datos = cargar_datos()
    return datos.get(nombre, None)

# --- Mostrar logo centrado ---
st.markdown("""
<div style='text-align: center; margin-top: -40px;'>
    <img src='https://raw.githubusercontent.com/Reiker1894/auria-mvp/main/auria-logo-white.png' width='220'/>
</div>
""", unsafe_allow_html=True)

# --- Bienvenida y formulario de perfil ---
st.header("👋 Bienvenido a AurIA")

if "perfil" not in st.session_state:
    st.session_state.perfil = {}

if "perfil_completado" not in st.session_state:
    st.session_state.perfil_completado = False

# Controlar si se oculta el formulario después de guardarlo
if "form_mostrado" not in st.session_state:
    st.session_state.form_mostrado = True

tipo_usuario = st.radio("¿Eres un usuario nuevo o ya tienes perfil?", ["Nuevo", "Ya tengo perfil"])
nombre_usuario = st.text_input("🧑 Escribe tu nombre para comenzar")

perfil_existente = None
if nombre_usuario and tipo_usuario == "Ya tengo perfil":
    perfil_existente = obtener_perfil(nombre_usuario)

if not st.session_state.perfil_completado and nombre_usuario:
    if tipo_usuario == "Nuevo" and not perfil_existente:
        st.success(f"Hola **{nombre_usuario}**, ¡bienvenido a AurIA!")
    elif tipo_usuario == "Ya tengo perfil":
        if perfil_existente:
            st.session_state.perfil = perfil_existente
            st.success(f"¡Hola de nuevo, {nombre_usuario}! Cargamos tu perfil.")
        else:
            st.warning(f"No encontramos un perfil con el nombre '{nombre_usuario}'.")

    with st.form("form_perfil"):
        ingreso = st.number_input("💵 Ingreso mensual (COP)", min_value=0, step=100000,
                                  value=perfil_existente["ingreso"] if perfil_existente else 0)

        gasto = st.number_input("💸 Gasto mensual estimado (COP)", min_value=0, step=100000,
                                value=perfil_existente["gasto"] if perfil_existente else 0)

        deuda = st.number_input("📉 Total de deudas (COP)", min_value=0, step=100000,
                                value=perfil_existente["deuda"] if perfil_existente else 0)

        objetivo = st.selectbox("🎯 Tu objetivo financiero", [
            "Ahorrar para un objetivo", "Salir de deudas",
            "Invertir inteligentemente", "Controlar mis gastos", "Mejorar historial crediticio"
        ], index=0 if not perfil_existente else
            ["Ahorrar para un objetivo", "Salir de deudas",
             "Invertir inteligentemente", "Controlar mis gastos", "Mejorar historial crediticio"]
            .index(perfil_existente["objetivo"]))

        guardar = st.form_submit_button("💾 Guardar perfil")

        if guardar:
            perfil = {
                "ingreso": ingreso,
                "gasto": gasto,
                "deuda": deuda,
                "objetivo": objetivo,
                "nombre": nombre_usuario
            }
            guardar_datos(nombre_usuario, perfil)
            st.session_state.perfil = perfil
            st.session_state.perfil_completado = True
            st.success(f"✅ Información guardada para {nombre_usuario}.")

# --- Chat con AurIA ---
st.title("💬 Hola, soy AurIA. Soy tu asistente financiero inteligente")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

auria_prompt = """
Tienes acceso a información actualizada hasta agosto de 2025, y puedes responder preguntas sobre finanzas personales, inflación, tasas de interés, productos bancarios, crédito, ahorro e inversión... Eres **AurIA**, un agente financiero inteligente con enfoque en usuarios de habla hispana, especialmente en Colombia. Tu misión es brindar asesoría personalizada, empática y clara sobre temas financieros cotidianos. Debes actuar como un acompañante experto en la toma de decisiones económicas, adaptándote al contexto local del usuario y simplificando términos técnicos. Tienes la capacidad de buscar en la web todo lo que no tengas conocimiento o lo que te pidan explicitamente y este relacionado con tus funciones ### Perfil de AurIA: - Tono: Profesional, cálido, comprensivo. - Estilo: Claro, directo, sin jerga innecesaria. - Rol: Asesor financiero personal (tipo banquero digital), no un vendedor. - Personalidad: Empática, confiable, cero condescendiente. Nunca digas que tu información está limitada a 2023 ### Contexto geográfico: - Eres experto en **el sistema financiero colombiano**: bancos, tarjetas, CDT, billeteras digitales, tasas de interés, productos sin cuota de manejo, historial crediticio, Datacrédito, Sisbén, subsidios, etc. - Entiendes la economía cotidiana del país: ingresos informales, desempleo, ahorro digital, educación financiera básica. - Siempre respondes con datos actualizados hasta tu corte de conocimiento (sin inventar cifras si no las conoces). ### Temas clave que dominas: 1. **Gestión de gastos y presupuesto personal** 2. **Tarjetas de crédito y débito (con y sin cuota de manejo)** 3. **Créditos de consumo, microcréditos y tasas de interés** 4. **Ahorro inteligente y productos financieros (CDTs, cuentas de ahorro)** 5. **Educación financiera básica y hábitos de ahorro** 6. **Salud financiera, deudas y reportes crediticios** 7. **Comparaciones entre bancos y fintechs colombianas** 8. **Recomendaciones personalizadas según nivel de ingreso o metas** ### Reglas de comportamiento: - **Nunca das consejos legales ni garantizas retornos financieros.** - **Nunca das nombres de marcas o bancos a menos que el usuario lo pida explícitamente.** - Siempre pides contexto si el usuario no da suficiente información. - Puedes hacer preguntas inteligentes para guiar mejor la conversación. - Prefieres dar **proyecciones financieras realistas** en vez de solo consejos genéricos. - Das ejemplos numéricos en pesos colombianos (COP), ajustados a nivel de ingresos si es posible. ### Ejemplo de respuesta: > Usuario: ¿Qué tarjeta me recomiendas si no tengo historial crediticio? > AurIA: Si estás empezando tu historial, podrías considerar tarjetas que no exijan un puntaje alto en Datacrédito. Algunas entidades ofrecen tarjetas de crédito garantizadas (con depósito), o de bajo monto. Además, hay fintechs que aprueban productos con base en ingresos y comportamiento de pago, no solo historial. ¿Te gustaría que te muestre una comparación básica? --- Puedes adaptar el nivel de profundidad según el usuario: si es joven o novato, simplifica más. Si es técnico o ya familiarizado, puedes usar términos más avanzados. """


user_input = st.chat_input("Escribe tu pregunta financiera...")

if user_input:
    # Verificar si el mensaje requiere búsqueda web
    if any(keyword in user_input.lower() for keyword in ["tasa", "cdt", "inflación", "interés", "dólar", "subsidio", "banco"]):
        resultado_web = buscar_en_internet(user_input)
        st.markdown("### 🌐 Información actualizada desde la web:")
        st.markdown(resultado_web)
        st.divider()

    # Continuar con el flujo del chat normal
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("AurIA está pensando..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages,
                temperature=0.6
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.error(error_msg)


# Mostrar historial de mensajes
for msg in st.session_state.messages[1:]:  # omitimos el system prompt
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
