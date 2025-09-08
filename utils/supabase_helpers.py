from supabase_client import supabase

def guardar_turno(usuario_id: str, pregunta: str, respuesta: str):
    if not all([usuario_id, pregunta, respuesta]):
        raise ValueError("❌ Uno de los campos está vacío. Revisa los valores enviados.")

    supabase.table("conversaciones").insert({
        "usuario_id": usuario_id,
        "mensaje_usuario": pregunta,
        "mensaje_auria": respuesta
    }).execute()
