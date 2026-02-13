import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, regexp_replace, split
from pyspark.ml.feature import CountVectorizer, StopWordsRemover, IDF

def get_stop_words():
    return [
        "the", "of", "and", "to", "in", "a", "is", "that", "for", "it",
        "as", "was", "with", "be", "by", "on", "not", "he", "i", "his",
        "at", "are", "but", "have", "had", "which", "from", "this", "they",
        "you", "she", "or", "an", "were", "we", "their", "him", "been",
        "has", "there", "who", "will", "one", "all", "would", "her",
        "said", "project", "gutenberg" 
    ]

def main():
    if len(sys.argv) < 3:
        print("Uso: python3 summarize_book.py <nombre_parcial_libro> <numero_palabras>")
        return

    target_book = sys.argv[1]
    try:
        n_words = int(sys.argv[2])
    except ValueError:
        print("El numero de palabras debe ser un entero.")
        return

    spark = SparkSession.builder.appName("GutenbergSummary").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    # 1. Carga y preprocesamiento
    df = spark.sparkContext.wholeTextFiles("libros/*.txt").toDF(["path", "text"])
    df = df.withColumn("title", regexp_replace("path", ".*\/", ""))
    
    df_clean = df.withColumn("clean_text", lower(col("text")))
    df_clean = df_clean.withColumn("clean_text", regexp_replace("clean_text", "[^a-z0-9\\s]", ""))
    df_clean = df_clean.withColumn("tokens", split(col("clean_text"), "\\s+"))
    
    remover = StopWordsRemover(inputCol="tokens", outputCol="filtered", stopWords=get_stop_words())
    df_filtered = remover.transform(df_clean)

    # 2. Calculo de TF-IDF
    cv = CountVectorizer(inputCol="filtered", outputCol="raw_features", vocabSize=20000, minDF=1.0)
    cv_model = cv.fit(df_filtered)
    df_tf = cv_model.transform(df_filtered)

    idf = IDF(inputCol="raw_features", outputCol="features")
    idf_model = idf.fit(df_tf)
    df_tfidf = idf_model.transform(df_tf)

    # 3. Extraccion de palabras clave para el libro solicitado
    book_row = df_tfidf.filter(col("title").contains(target_book)).first()

    if not book_row:
        print(f"No se encontro ningun libro que contenga: {target_book}")
        spark.stop()
        return

    tfidf_vector = book_row["features"]
    vocabulary = cv_model.vocabulary

    # Unir indices con palabras y ordenar por relevancia
    word_scores = []
    for idx, score in zip(tfidf_vector.indices, tfidf_vector.values):
        word_scores.append((vocabulary[idx], score))
    
    word_scores.sort(key=lambda x: x[1], reverse=True)

    print(f"\n--- Palabras resumen para: {book_row['title']} ---")
    for i in range(min(n_words, len(word_scores))):
        word, score = word_scores[i]
        print(f"{i+1}. {word}")

    spark.stop()

if __name__ == "__main__":
    main()