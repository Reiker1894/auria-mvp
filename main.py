
import streamlit as st
import os
import json
from openai import OpenAI
# Nombre del archivo donde se guardarán los perfiles
DATA_FILE = "usuarios.json"

# Función para cargar todos los usuarios guardados
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Función para guardar/actualizar un usuario
def guardar_datos(nombre, perfil):
    datos = cargar_datos()
    datos[nombre] = perfil
    with open(DATA_FILE, "w") as f:
        json.dump(datos, f, indent=2)

# Función para recuperar un perfil por nombre
def obtener_perfil(nombre):
    datos = cargar_datos()
    return datos.get(nombre, None)

st.markdown("---")
st.header("👋 Bienvenido a AurIA")

if "perfil" not in st.session_state:
    st.session_state.perfil = {}

# Pregunta si es nuevo o ya tiene perfil
tipo_usuario = st.radio("¿Eres un usuario nuevo o ya tienes perfil?", ["Nuevo", "Ya tengo perfil"])

# Pedir el nombre del usuario
nombre_usuario = st.text_input("🧑 Escribe tu nombre para comenzar")

# Si el usuario escribe su nombre, iniciamos el proceso
if nombre_usuario:
    perfil_existente = obtener_perfil(nombre_usuario) if tipo_usuario == "Ya tengo perfil" else None

    # Si es nuevo, saludarlo
    if tipo_usuario == "Nuevo" and not perfil_existente:
        st.success(f"Hola **{nombre_usuario}**, ¡bienvenido a AurIA!")

    # Si ya tiene perfil, cargarlo
    elif tipo_usuario == "Ya tengo perfil":
        if perfil_existente:
            st.session_state.perfil = perfil_existente
            st.success(f"¡Hola de nuevo, {nombre_usuario}! Cargamos tu perfil.")
        else:
            st.warning(f"No encontramos un perfil con el nombre '{nombre_usuario}'.")

    # Mostrar el formulario para crear o actualizar el perfil
    if tipo_usuario == "Nuevo" or (tipo_usuario == "Ya tengo perfil" and perfil_existente):
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
            st.success(f"✅ Información guardada para {nombre_usuario}.")

# Mostrar el resumen del perfil si existe
if st.session_state.perfil:
    st.markdown(f"### 🧠 AurIA recuerda tu perfil, **{st.session_state.perfil['nombre']}**:")
    st.markdown(f"- Ingreso mensual: **${st.session_state.perfil['ingreso']:,.0f} COP**")
    st.markdown(f"- Gasto mensual: **${st.session_state.perfil['gasto']:,.0f} COP**")
    st.markdown(f"- Deuda total: **${st.session_state.perfil['deuda']:,.0f} COP**")
    st.markdown(f"- Objetivo: **{st.session_state.perfil['objetivo']}**")



# # Configuración de la página
# st.set_page_config(page_title="AurIA")
# # Inicializar cliente OpenAI

import streamlit.components.v1 as components

# Fondo animado
components.html(
    open("background.html", "r").read(),
    height=0,  # ocultamos la altura fija
    width=0,
)


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Mostrar solo el logo, centrado
st.markdown(
    """
    <div style='text-align: center; margin-top: -40px;'>
        <img src='https://raw.githubusercontent.com/Reiker1894/auria-mvp/main/auria-logo-white.png' width='220'/>
    </div>
    """,
    unsafe_allow_html=True
)


auria_prompt = """
Tienes acceso a información actualizada hasta agosto de 2025, y puedes responder preguntas sobre finanzas personales, inflación, tasas de interés, productos bancarios, crédito, ahorro e inversión...

Eres **AurIA**, un agente financiero inteligente con enfoque en usuarios de habla hispana, especialmente en Colombia. Tu misión es brindar asesoría personalizada, empática y clara sobre temas financieros cotidianos. Debes actuar como un acompañante experto en la toma de decisiones económicas, adaptándote al contexto local del usuario y simplificando términos técnicos.
Tienes la capacidad de buscar en la web todo lo que no tengas conocimiento o lo que te pidan explicitamente y este relacionado con tus funciones
### Perfil de AurIA:
- Tono: Profesional, cálido, comprensivo.
- Estilo: Claro, directo, sin jerga innecesaria.
- Rol: Asesor financiero personal (tipo banquero digital), no un vendedor.
- Personalidad: Empática, confiable, cero condescendiente.
Nunca digas que tu información está limitada a 2023
### Contexto geográfico:
- Eres experto en **el sistema financiero colombiano**: bancos, tarjetas, CDT, billeteras digitales, tasas de interés, productos sin cuota de manejo, historial crediticio, Datacrédito, Sisbén, subsidios, etc.
- Entiendes la economía cotidiana del país: ingresos informales, desempleo, ahorro digital, educación financiera básica.
- Siempre respondes con datos actualizados hasta tu corte de conocimiento (sin inventar cifras si no las conoces).

### Temas clave que dominas:
1. **Gestión de gastos y presupuesto personal**
2. **Tarjetas de crédito y débito (con y sin cuota de manejo)**
3. **Créditos de consumo, microcréditos y tasas de interés**
4. **Ahorro inteligente y productos financieros (CDTs, cuentas de ahorro)**
5. **Educación financiera básica y hábitos de ahorro**
6. **Salud financiera, deudas y reportes crediticios**
7. **Comparaciones entre bancos y fintechs colombianas**
8. **Recomendaciones personalizadas según nivel de ingreso o metas**

### Reglas de comportamiento:
- **Nunca das consejos legales ni garantizas retornos financieros.**
- **Nunca das nombres de marcas o bancos a menos que el usuario lo pida explícitamente.**
- Siempre pides contexto si el usuario no da suficiente información.
- Puedes hacer preguntas inteligentes para guiar mejor la conversación.
- Prefieres dar **proyecciones financieras realistas** en vez de solo consejos genéricos.
- Das ejemplos numéricos en pesos colombianos (COP), ajustados a nivel de ingresos si es posible.

### Ejemplo de respuesta:
> Usuario: ¿Qué tarjeta me recomiendas si no tengo historial crediticio?

> AurIA: Si estás empezando tu historial, podrías considerar tarjetas que no exijan un puntaje alto en Datacrédito. Algunas entidades ofrecen tarjetas de crédito garantizadas (con depósito), o de bajo monto. Además, hay fintechs que aprueban productos con base en ingresos y comportamiento de pago, no solo historial. ¿Te gustaría que te muestre una comparación básica?

---

Puedes adaptar el nivel de profundidad según el usuario: si es joven o novato, simplifica más. Si es técnico o ya familiarizado, puedes usar términos más avanzados.


"""
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": auria_prompt}
    ]

st.set_page_config(page_title="AurIA", page_icon="💰")
st.title("💬 Hola, soy AurIA. Hazme cualquier pregunta sobre tus finanzas.")

user_input = st.chat_input("Escribe tu pregunta financiera...")

if user_input:
    print(f"Usuario escribió: {user_input}")  # Debug en consola
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("AurIA está pensando..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages,
                temperature=0.6
                tools=["web_browser"],  # si tu cuenta lo permite
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            if "insufficient_quota" in str(e):
                error_msg = "⚠️ Has excedido tu cuota de OpenAI. Por favor verifica tu plan y facturación en platform.openai.com"
            else:
                error_msg = f"❌ Error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.error(error_msg)

for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
