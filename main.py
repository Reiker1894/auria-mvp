import streamlit as st
import os
from openai import OpenAI
from serpapi import GoogleSearch
from supabase_client import supabase
from utils.supabase_helpers import guardar_turno, cargar_historial
import streamlit.components.v1 as components
from tools.prompt_loader import cargar_prompt
# --- Configuración de página
st.set_page_config(page_title="AurIA", page_icon="💰")
components.html(open("background.html", "r").read(), height=0, width=0)





# Capturar nombre del usuario si aún no lo ha ingresado
if "username" not in st.session_state:
    nombre_ingresado = st.text_input("🧑 Escribe tu nombre para comenzar:")
    if nombre_ingresado:
        st.session_state.username = nombre_ingresado
        st.experimental_rerun()  # Recarga la app para mostrar el chat con todo inicializado
else:
    nombre_usuario = st.session_state.username
    auria_prompt = cargar_prompt()  # Aquí puedes continuar con el resto del flujo







# --- Inicializar cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Prompt base de AurIA (System)
auria_prompt = cargar_prompt()  # Usa el mismo prompt largo que ya definiste

# --- Función de búsqueda web con SerpAPI
def buscar_en_internet(pregunta):
    params = {
        "engine": "google",
        "q": pregunta,
        "location": "Colombia",
        "api_key": os.getenv("SERPAPI_KEY")
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

# --- Capturar usuario
st.title("💬 Hola, soy AurIA. Tu asistente financiero en Colombia")

if "username" not in st.session_state:
    st.session_state.username = st.text_input("🧑 Escribe tu nombre para comenzar:", key="username_input")

if st.session_state.username:
    nombre_usuario = st.session_state.username

    # Cargar historial desde Supabase (solo una vez)
    if "messages" not in st.session_state:
        st.session_state.messages = cargar_historial(nombre_usuario)

    # Mostrar historial
    for msg in st.session_state.messages[1:]:  # omitimos el system prompt
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Entrada del usuario
    user_input = st.chat_input("Escribe tu pregunta financiera...")

    if user_input:
        # Enriquecer con búsqueda web si detecta ciertas palabras clave
        if any(kw in user_input.lower() for kw in ["inflación", "tasa", "dólar", "ipc", "interés", "uvr", "cdt", "salario mínimo"]):
            resultado_web = buscar_en_internet(user_input)
            user_input += f"\n\n[Este dato fue obtenido en tiempo real de la web: {resultado_web}]"

        # Agregar entrada del usuario al historial
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Llamar al modelo
        with st.spinner("AurIA está pensando..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=st.session_state.messages,
                    temperature=0.6
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = f"❌ Error: {str(e)}"

        # Agregar respuesta al historial
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

        # Guardar en Supabase
        guardar_turno(nombre_usuario, user_input, reply)

