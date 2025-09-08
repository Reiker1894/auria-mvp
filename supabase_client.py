
from supabase import create_client, Client

# Usa tus propios valores aquí:
SUPABASE_URL = "https://trrxzgtfydvojvtrvpkh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRycnh6Z3RmeWR2b2p2dHJ2cGtoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTcyODg0MzYsImV4cCI6MjA3Mjg2NDQzNn0.O3Xj1zAb4JuO4hbijzOyKZNudgME0IEtppb8EB7oFEc"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
