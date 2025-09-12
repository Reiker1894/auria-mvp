from supabase_client import supabase

def cargar_perfil_financiero(usuario_id: str):
    response = supabase.table("perfil_financiero") \
        .select("*") \
        .eq("usuario_id", usuario_id) \
        .limit(1) \
        .execute()

    if response.data:
        return response.data[0]
    else:
        return None

def guardar_perfil_financiero(usuario_id: str, ingreso: float, gasto: float, deuda: float, objetivo: str):
    datos = {
        "usuario_id": usuario_id,
        "ingreso_mensual": ingreso,
        "gasto_mensual": gasto,
        "deuda_total": deuda,
        "objetivo": objetivo
    }

    supabase.table("perfil_financiero").upsert(datos, on_conflict=["usuario_id"]).execute()
