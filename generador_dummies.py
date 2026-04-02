import pickle
import os
import numpy as np

archivo_db = "shogun_db.pkl"

# 1. Intentamos cargar la base de datos actual para NO borrar lo que ya hiciste
if os.path.exists(archivo_db):
    with open(archivo_db, "rb") as f:
        base_de_datos = pickle.load(f)
    print(f"--- Base de datos encontrada con {len(base_de_datos)} registros reales ---")
else:
    base_de_datos = {}
    print("--- Creando base de datos nueva desde cero ---")

# 2. Generar 10,000 usuarios sintéticos cuidando no duplicar
print("Generando 10,000 perfiles de estrés... por favor espera.")
for i in range(10000):
    nombre_bot = f"Sintetico_{i}"
    # Solo lo agregamos si no existe (por si corres el script varias veces)
    if nombre_bot not in base_de_datos:
        # Vector de 128 dimensiones con ruido aleatorio
        # El +50.0 es tu firma de seguridad para que no se parezcan a humanos
        base_de_datos[nombre_bot] = np.random.rand(128) + 50.0

# 3. Guardamos la mezcla de registros reales + dummies
with open(archivo_db, "wb") as f:
    pickle.dump(base_de_datos, f)

print(f"¡Éxito! Ahora tienes un total de {len(base_de_datos)} registros.")
print("Tus registros reales están a salvo junto con los 10,000 bots.")