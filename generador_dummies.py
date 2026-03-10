import pickle
import numpy as np

archivo_db = "shogun_db.pkl"

# 1. Cargamos tu base de datos actual 
try:
    with open(archivo_db, "rb") as f:
        base_de_datos = pickle.load(f)
    print(f"Base de datos original cargada con {len(base_de_datos)} rostros.")
except FileNotFoundError:
    print("No se encontró la base de datos. ¡Corre tu main.py y regístrate primero!")
    exit()

# 2. Obtenemos el tamaño exacto del vector
primer_registro = list(base_de_datos.values())[0]
dimensiones = len(primer_registro)

print(f"\nInyectando esteroides nivel Dios... Generando 10,000 sujetos de prueba...")

# 3. Inyectamos 10,000 perfiles falsos 
for i in range(1, 10001):
    # Les pongo una 'X' en el nombre para no sobreescribir los 1,000 que ya tenía si es que no borre el archivo
    nombre_falso = f"Sujeto_Prueba_X_{i}" 
    vector_falso = np.random.uniform(low=-5.0, high=5.0, size=(dimensiones,))
    base_de_datos[nombre_falso] = vector_falso

# 4. Guardamos la nueva mega base de datos
with open(archivo_db, "wb") as f:
    pickle.dump(base_de_datos, f)

print(f"\n¡BOOM! 💥 El archivo 'shogun_db.pkl' acaba de engordar. Ahora tienes {len(base_de_datos)} registros.")
print("¡Listo para hacer sudar a ese procesador! :3")