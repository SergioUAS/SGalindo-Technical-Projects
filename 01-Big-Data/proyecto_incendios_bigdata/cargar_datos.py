import pandas as pd
from pymongo import MongoClient

# 1. Conexión a MongoDB
# Nota: Usamos la IP de tu Ubuntu que confirmamos que funciona
cliente = MongoClient('mongodb://172.28.140.224:27017/')
db = cliente['registro_incendios']

# 2. Definir las colecciones
identificacion = db['incendios_identificacion']
ecologia = db['incendios_ecologia']
metricas = db['incendios_metricas']

# 3. Limpieza de datos previos
# Esto asegura que siempre tengamos exactamente 100 registros nuevos
print("Limpiando colecciones antiguas...")
identificacion.drop()
ecologia.drop()
metricas.drop()
db['resumen_incendios_estado'].drop() # Borramos resultados previos de MapReduce
print("Base de datos lista para nuevos registros.")

# 4. Procesamiento del CSV
print("Leyendo archivo CSV y seleccionando muestra aleatoria...")
df = pd.read_csv('estadisticasincendiosforestales2015-2024.csv')

# Tomamos 100 registros al azar para tener variedad de estados 🇲🇽
df_100 = df.sample(n=100)
registros = df_100.to_dict(orient='records')

# Listas para clasificar los datos en las 3 colecciones
docs_identificacion = []
docs_ecologia = []
docs_metricas = []

for r in registros:
    # Datos de identidad y lugar
    docs_identificacion.append({
        "clave_incendio": r['Clave_del_incendio'],
        "anio": r['anio'],
        "ubicacion": {
            "estado": r['Estado'], 
            "municipio": r['Municipio'], 
            "region": r['Region']
        }
    })
    
    # Datos de vegetación y causas
    docs_ecologia.append({
        "clave_incendio": r['Clave_del_incendio'],
        "detalles": {
            "vegetacion": r['Tipo_Vegetacion'], 
            "impacto": r['Tipo_impacto'], 
            "causa": r['Causa']
        }
    })
    
    # Datos cuantitativos para análisis
    docs_metricas.append({
        "clave_incendio": r['Clave_del_incendio'],
        "datos_numericos": {
            "hectareas": r['Total_hectareas'], 
            "duracion_dias": r['Duracion_dias']
        }
    })

# 5. Inserción masiva
if docs_identificacion:
    identificacion.insert_many(docs_identificacion)
    ecologia.insert_many(docs_ecologia)
    metricas.insert_many(docs_metricas)
    print(f"¡Éxito! Se han insertado 100 registros aleatorios en 3 colecciones.")
else:
    print("No se encontraron datos para insertar. Revisa el archivo CSV.")