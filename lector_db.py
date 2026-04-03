import pickle
import os

print("========================================")
print("   🛡️ AUDITORÍA DE SHOGUN AI v2.0 🛡️")
print("========================================\n")

# --- 1. LEER BASE DE DATOS PRINCIPAL ---
print("--- USUARIOS REGISTRADOS (shogun_db.pkl) ---")
if os.path.exists("shogun_db.pkl"):
    with open("shogun_db.pkl", "rb") as f:
        db = pickle.load(f)
        if len(db) > 0:
            for nombre, vector in db.items():
                # Solo mostramos el nombre y el tamaño del vector para no saturar la pantalla
                print(f"✅ Usuario: {nombre.upper()} | Biometría: Vector de {len(vector)} dimensiones")
        else:
            print("La base de datos está vacía.")
else:
    print("El archivo shogun_db.pkl no existe.")

print("\n")

# --- 2. LEER REGISTRO DE INVÁLIDOS ---
print("--- INTENTOS BLOQUEADOS (shogun_invalidos.pkl) ---")
if os.path.exists("shogun_invalidos.pkl"):
    with open("shogun_invalidos.pkl", "rb") as f:
        invalidos = pickle.load(f)
        if len(invalidos) > 0:
            for intento in invalidos:
                print(f"🚨 [{intento['fecha']}] ALERTA: {intento['motivo']}")
        else:
            print("No hay registros de intentos fallidos.")
else:
    print("El archivo shogun_invalidos.pkl no existe.")
    
print("\n========================================")