import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


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


components.html(open("background.html", "r").read(), height=0, width=0)

# --- Mostrar logo centrado ---
st.markdown("""
<div style='text-align: center; margin-top: -40px;'>
    <img src='https://raw.githubusercontent.com/Reiker1894/auria-mvp/main/auria-logo-white.png' width='420'/>
</div>
""", unsafe_allow_html=True)




# --- Mostrar título
st.title("💬 Hola, soy AurIA. Tu asistente financiero en Colombia")

# --- Capturar nombre del usuario
if "username" not in st.session_state:
    nombre_ingresado = st.text_input("🧑 Escribe tu nombre para comenzar:")
    if nombre_ingresado:
        st.session_state.username = nombre_ingresado
        st.experimental_rerun()
else:
    nombre_usuario = st.session_state.username

    # --- Cargar prompt solo una vez
    if "messages" not in st.session_state:
        auria_prompt = cargar_prompt()
        st.session_state.messages = [{"role": "system", "content": auria_prompt}]
        st.session_state.messages += cargar_historial(nombre_usuario)[1:]  # omitimos repetir el system

    # --- Inicializar cliente OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

    # --- Mostrar historial
    for msg in st.session_state.messages[1:]:  # omitimos el system prompt
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- Entrada del usuario
    user_input = st.chat_input("Escribe tu pregunta financiera...")

    if user_input:
        # 🔍 Buscar en internet si detecta palabras clave
        if any(kw in user_input.lower() for kw in ["inflación", "tasa", "dólar", "ipc", "interés", "uvr", "cdt", "salario mínimo"]):
            resultado_web = buscar_en_internet(user_input)
            user_input += f"\n\n[Este dato fue obtenido en tiempo real de la web: {resultado_web}]"

        # Agregar entrada del usuario
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Obtener respuesta
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

        # Mostrar respuesta
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

        # Guardar turno en Supabase
        guardar_turno(nombre_usuario, user_input, reply)
