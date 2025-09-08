from supabase_client import supabase

def guardar_turno(usuario_id, pregunta, respuesta):
    if not all([usuario_id, pregunta, respuesta]):
        raise ValueError("❌ Uno de los campos está vacío.")
    supabase.table("conversaciones").insert({
        "usuario_id": usuario_id,
        "mensaje_usuario": pregunta,
        "mensaje_auria": respuesta
    }).execute()

def cargar_historial(usuario_id):
    response = supabase.table("conversaciones") \
        .select("*") \
        .eq("usuario_id", usuario_id) \
        .order("timestamp", desc=False) \
        .execute()
    mensajes = [{"role": "system", "content": "Eres un asesor financiero colombiano..."}]
    for fila in response.data:
        mensajes.append({"role": "user", "content": fila["mensaje_usuario"]})
        mensajes.append({"role": "assistant", "content": fila["mensaje_auria"]})
    return mensajes
