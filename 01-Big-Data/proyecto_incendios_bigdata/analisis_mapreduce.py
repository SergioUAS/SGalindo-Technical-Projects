from pymongo import MongoClient
from bson.code import Code

# 1. Conexión al servidor
# Usa la IP de tu instancia de Ubuntu
cliente = MongoClient('mongodb://172.28.140.224:27017/')
db = cliente['registro_incendios']
coleccion = db['incendios_identificacion']

# 2. Función de Mapa (Map)
# Emite el estado como llave y el número 1 como valor
map_func = Code("""
function() {
    if (this.ubicacion && this.ubicacion.estado) {
        emit(this.ubicacion.estado, 1);
    }
}
""")

# 3. Función de Reducción (Reduce)
# Suma todos los '1' recibidos para cada estado
reduce_func = Code("""
function(key, values) {
    return Array.sum(values);
}
""")

# 4. Ejecución del MapReduce
# El resultado se guardará en una colección llamada 'resumen_incendios_estado'
print("Iniciando procesamiento MapReduce...")
db.command(
    "mapReduce",
    "incendios_identificacion",
    map=map_func,
    reduce=reduce_func,
    out="resumen_incendios_estado"
)

print("¡Procesamiento completado!")
print("Busca la colección 'resumen_incendios_estado' en MongoDB Compass.")