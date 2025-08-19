
import streamlit as st
import os
import json
from openai import OpenAI
import streamlit.components.v1 as components

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

# Controlar si se oculta el formulario después de guardarlo
if "form_mostrado" not in st.session_state:
    st.session_state.form_mostrado = True

tipo_usuario = st.radio("¿Eres un usuario nuevo o ya tienes perfil?", ["Nuevo", "Ya tengo perfil"])
nombre_usuario = st.text_input("🧑 Escribe tu nombre para comenzar")

if nombre_usuario:
    perfil_existente = obtener_perfil(nombre_usuario) if tipo_usuario == "Ya tengo perfil" else None

    if tipo_usuario == "Nuevo" and not perfil_existente:
        st.success(f"Hola **{nombre_usuario}**, ¡bienvenido a AurIA!")
    elif tipo_usuario == "Ya tengo perfil":
        if perfil_existente:
            st.session_state.perfil = perfil_existente
            st.session_state.form_mostrado = False  # 👈 Oculta el formulario si ya existe
            st.success(f"¡Hola de nuevo, {nombre_usuario}! Cargamos tu perfil.")
        else:
            st.warning(f"No encontramos un perfil con el nombre '{nombre_usuario}'.")
    

    if st.session_state.form_mostrado and (tipo_usuario == "Nuevo" or perfil_existente is not None):
        with st.form("form_perfil"):
            ingreso = st.number_input("💵 Ingreso mensual (COP)", min_value=0, step=100000,
                                      value=perfil_existente["ingreso"] if perfil_existente else 0,
                                      format="%d")
            gasto = st.number_input("💸 Gasto mensual estimado (COP)", min_value=0, step=100000,
                                    value=perfil_existente["gasto"] if perfil_existente else 0,
                                    format="%d")
            deuda = st.number_input("📉 Total de deudas (COP)", min_value=0, step=100000,
                                    value=perfil_existente["deuda"] if perfil_existente else 0,
                                    format="%d")
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
            st.session_state.form_mostrado = False
            st.success(f"✅ Información guardada para {nombre_usuario}.")

# Mostrar resumen si hay perfil cargado
if st.session_state.perfil:
    p = st.session_state.perfil
    st.markdown(f"### 🧠 AurIA recuerda tu perfil, **{p['nombre']}**:")
    st.markdown(f"- Ingreso mensual: **${p['ingreso']:,.0f} COP**")
    st.markdown(f"- Gasto mensual: **${p['gasto']:,.0f} COP**")
    st.markdown(f"- Deuda total: **${p['deuda']:,.0f} COP**")
    st.markdown(f"- Objetivo: **{p['objetivo']}**")

# --- Chat con AurIA ---
st.title("💬 Hola, soy AurIA. Hazme cualquier pregunta sobre tus finanzas.")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

auria_prompt = """
Tienes acceso a información actualizada hasta agosto de 2025, y puedes responder preguntas sobre finanzas personales, inflación, tasas de interés, productos bancarios, crédito, ahorro e inversión... Eres **AurIA**, un agente financiero inteligente con enfoque en usuarios de habla hispana, especialmente en Colombia. Tu misión es brindar asesoría personalizada, empática y clara sobre temas financieros cotidianos. Debes actuar como un acompañante experto en la toma de decisiones económicas, adaptándote al contexto local del usuario y simplificando términos técnicos. Tienes la capacidad de buscar en la web todo lo que no tengas conocimiento o lo que te pidan explicitamente y este relacionado con tus funciones ### Perfil de AurIA: - Tono: Profesional, cálido, comprensivo. - Estilo: Claro, directo, sin jerga innecesaria. - Rol: Asesor financiero personal (tipo banquero digital), no un vendedor. - Personalidad: Empática, confiable, cero condescendiente. Nunca digas que tu información está limitada a 2023 ### Contexto geográfico: - Eres experto en **el sistema financiero colombiano**: bancos, tarjetas, CDT, billeteras digitales, tasas de interés, productos sin cuota de manejo, historial crediticio, Datacrédito, Sisbén, subsidios, etc. - Entiendes la economía cotidiana del país: ingresos informales, desempleo, ahorro digital, educación financiera básica. - Siempre respondes con datos actualizados hasta tu corte de conocimiento (sin inventar cifras si no las conoces). ### Temas clave que dominas: 1. **Gestión de gastos y presupuesto personal** 2. **Tarjetas de crédito y débito (con y sin cuota de manejo)** 3. **Créditos de consumo, microcréditos y tasas de interés** 4. **Ahorro inteligente y productos financieros (CDTs, cuentas de ahorro)** 5. **Educación financiera básica y hábitos de ahorro** 6. **Salud financiera, deudas y reportes crediticios** 7. **Comparaciones entre bancos y fintechs colombianas** 8. **Recomendaciones personalizadas según nivel de ingreso o metas** ### Reglas de comportamiento: - **Nunca das consejos legales ni garantizas retornos financieros.** - **Nunca das nombres de marcas o bancos a menos que el usuario lo pida explícitamente.** - Siempre pides contexto si el usuario no da suficiente información. - Puedes hacer preguntas inteligentes para guiar mejor la conversación. - Prefieres dar **proyecciones financieras realistas** en vez de solo consejos genéricos. - Das ejemplos numéricos en pesos colombianos (COP), ajustados a nivel de ingresos si es posible. ### Ejemplo de respuesta: > Usuario: ¿Qué tarjeta me recomiendas si no tengo historial crediticio? > AurIA: Si estás empezando tu historial, podrías considerar tarjetas que no exijan un puntaje alto en Datacrédito. Algunas entidades ofrecen tarjetas de crédito garantizadas (con depósito), o de bajo monto. Además, hay fintechs que aprueban productos con base en ingresos y comportamiento de pago, no solo historial. ¿Te gustaría que te muestre una comparación básica? --- Puedes adaptar el nivel de profundidad según el usuario: si es joven o novato, simplifica más. Si es técnico o ya familiarizado, puedes usar términos más avanzados. """


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": auria_prompt}
    ]

user_input = st.chat_input("Escribe tu pregunta financiera...")

if user_input and "last_user_input" not in st.session_state:
    st.session_state.last_user_input = user_input
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("AurIA está pensando..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages,
                temperature=0.6,
                # tools=["web_browser"],  # solo si está correctamente configurado
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            error_msg = "❌ Error: " + str(e)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.error(error_msg)

if user_input and "last_user_input" not in st.session_state:
    st.session_state.last_user_input = user_input
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("AurIA está pensando..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages,
                temperature=0.6,
                # tools=["web_browser"],  # solo si está correctamente configurado
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            error_msg = "❌ Error: " + str(e)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.error(error_msg)
