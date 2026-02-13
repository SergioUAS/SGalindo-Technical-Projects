import os
import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, lower, regexp_replace, split
from pyspark.sql.types import ArrayType, StringType, DoubleType
from pyspark.ml.feature import CountVectorizer, StopWordsRemover, Normalizer
from pyspark.mllib.linalg.distributed import RowMatrix
from pyspark.mllib.linalg import Vectors

def get_stop_words():
    # Mismas stop words que en el paso anterior para consistencia
    return [
        "the", "of", "and", "to", "in", "a", "is", "that", "for", "it",
        "as", "was", "with", "be", "by", "on", "not", "he", "i", "his",
        "at", "are", "but", "have", "had", "which", "from", "this", "they",
        "you", "she", "or", "an", "were", "we", "their", "him", "been",
        "has", "there", "who", "will", "one", "all", "would", "her"
    ]

def main():
    # Inicializar Spark
    spark = SparkSession.builder \
        .appName("GutenbergSimilarity") \
        .getOrCreate()
    
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    # 1. Cargar libros
    # wholeTextFiles lee (ruta, contenido)
    books_rdd = sc.wholeTextFiles("libros/*.txt")
    
    # Convertir a DataFrame y limpiar ruta para dejar solo el nombre del archivo
    df = books_rdd.toDF(["path", "text"])
    df = df.withColumn("title", regexp_replace("path", ".*\/", ""))

    # 2. Aplicar los 4 filtros (Minusculas, Regex, Tokenizacion, StopWords)
    
    # a. Minusculas y limpieza de caracteres (Regex)
    df_clean = df.withColumn("clean_text", lower(col("text")))
    df_clean = df_clean.withColumn("clean_text", regexp_replace("clean_text", "[^a-z0-9\\s]", ""))
    
    # b. Tokenizacion (split por espacio)
    df_clean = df_clean.withColumn("tokens", split(col("clean_text"), "\\s+"))
    
    # c. Eliminar Stop Words
    remover = StopWordsRemover(inputCol="tokens", outputCol="filtered", stopWords=get_stop_words())
    df_filtered = remover.transform(df_clean)

    # 3. Vectorizacion (TF - Frecuencia de Termino)
    # Usamos vocabularioSize equivalente al que generaste o automatico
    vectorizer = CountVectorizer(inputCol="filtered", outputCol="raw_features", vocabSize=10000, minDF=1.0)
    model = vectorizer.fit(df_filtered)
    df_vectorized = model.transform(df_filtered)

    # 4. Normalizacion (Para calcular Similitud del Coseno despues)
    normalizer = Normalizer(inputCol="raw_features", outputCol="features", p=2.0)
    df_norm = normalizer.transform(df_vectorized)

    # 5. Calculo de la Matriz de Similitud (Producto Punto de vectores normalizados)
    # Convertimos a RDD para usar operaciones de matriz eficientes
    mat_rdd = df_norm.select("features").rdd.map(lambda row: Vectors.dense(row.features.toArray()))
    mat = RowMatrix(mat_rdd)
    
    # Compute column similarities (esto nos da similitud entre documentos si transponemos o A * A^T)
    # Para 100 libros, es mas facil hacer producto punto localmente o via gramian
    # CoordinateMatrix es costoso, hacemos el producto punto manual que es equivalente a la similitud coseno
    
    features = mat_rdd.collect()
    n = len(features)
    print(f"Calculando matriz {n}x{n}...")

    # Guardamos los titulos para referencia
    titles = df_norm.select("title").rdd.flatMap(lambda x: x).collect()
    
    sim_matrix = []
    for i in range(n):
        row = []
        vec1 = features[i]
        for j in range(n):
            vec2 = features[j]
            # Dot product de vectores normalizados = Similitud Coseno
            sim = vec1.dot(vec2)
            row.append(sim)
        sim_matrix.append(row)

    # 6. Guardar resultados para los siguientes pasos
    # Guardamos los titulos y la matriz en un archivo simple
    with open("matriz_similitud.txt", "w", encoding="utf-8") as f:
        # Primera linea: titulos separados por |
        f.write("|".join(titles) + "\n")
        # Siguientes lineas: filas de la matriz
        for row in sim_matrix:
            f.write(",".join(map(str, row)) + "\n")

    print("Matriz calculada y guardada en 'matriz_similitud.txt'")
    spark.stop()

if __name__ == "__main__":
    main()