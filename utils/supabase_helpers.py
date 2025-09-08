# utils/supabase_helpers.py
from supabase_client import supabase

def guardar_turno(usuario_id: str, pregunta: str, respuesta: str):
    supabase.table("conversaciones").insert({
        "usuario_id": usuario_id,
        "mensaje_usuario": pregunta,
        "mensaje_auria": respuesta
    }).execute()

def cargar_historial(usuario_id: str):
    response = supabase.table("conversaciones") \
        .select("*") \
        .eq("usuario_id", usuario_id) \
        .order("timestamp", desc=False) \
        .execute()

    if response.data:
        mensajes = [{"role": "system", "content": "Eres un asesor financiero colombiano, empático y claro..."}]
        for fila in response.data:
            mensajes.append({"role": "user", "content": fila["mensaje_usuario"]})
            mensajes.append({"role": "assistant", "content": fila["mensaje_auria"]})
        return mensajes
    else:
        return [{"role": "system", "content": "Eres un asesor financiero colombiano, empático y claro..."}]
