from pyspark.sql import SparkSession

# Creamos la sesión de Spark configurada para MongoDB
spark = SparkSession.builder \
    .appName("AnalisisIncendiosSEMARNAT") \
    .config("spark.mongodb.read.connection.uri", "mongodb://172.28.140.224:27017/registro_incendios.incendios_identificacion") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.4.0") \
    .getOrCreate()

print("¡Sesión de Spark creada con éxito!")

# Cargamos los datos de la colección de identificación
df_identificacion = spark.read \
    .format("mongodb") \
    .load()

# Mostramos el esquema (la estructura de los datos)
print("Estructura de la colección identificación:")
df_identificacion.printSchema()

# Mostramos los primeros 5 registros
df_identificacion.show(5)

# Cargamos la colección de ecología
df_ecologia = spark.read \
    .format("mongodb") \
    .option("spark.mongodb.read.connection.uri", "mongodb://172.28.140.224:27017/registro_incendios.incendios_ecologia") \
    .load()

# Cargamos la colección de métricas
df_metricas = spark.read \
    .format("mongodb") \
    .option("spark.mongodb.read.connection.uri", "mongodb://172.28.140.224:27017/registro_incendios.incendios_metricas") \
    .load()

print("¡Todas las colecciones han sido cargadas en Spark!")

# Unimos Identificación con Ecología
df_unido = df_identificacion.join(df_ecologia, "clave_incendio")

# Unimos el resultado con Métricas
df_final = df_unido.join(df_metricas, "clave_incendio")

print("Unión completada. Ahora tenemos todos los datos en un solo DataFrame.")

from pyspark.sql import functions as F

# 1. Agrupamos por el campo de vegetación (que está dentro de 'detalles')
# 2. Promediamos las hectáreas (que están dentro de 'datos_numericos')
resultado_analisis = df_final.groupBy("detalles.vegetacion") \
    .agg(F.avg("datos_numericos.hectareas").alias("promedio_hectareas")) \
    .orderBy("promedio_hectareas", ascending=False)

# Mostramos el resultado final
print("Promedio de hectáreas quemadas por tipo de vegetación:")
resultado_analisis.show()

# Guardamos el resultado en una nueva colección de MongoDB
resultado_analisis.write \
    .format("mongodb") \
    .mode("overwrite") \
    .option("spark.mongodb.write.connection.uri", "mongodb://172.28.140.224:27017/registro_incendios.reporte_vegetacion") \
    .save()

print("¡Resultados persistidos en MongoDB!")