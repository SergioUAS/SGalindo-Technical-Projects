import os
import re

def get_stop_words():
    # Lista basica de stop words en ingles
    return set([
        "the", "of", "and", "to", "in", "a", "is", "that", "for", "it",
        "as", "was", "with", "be", "by", "on", "not", "he", "i", "his",
        "at", "are", "but", "have", "had", "which", "from", "this", "they",
        "you", "she", "or", "an", "were", "we", "their", "him", "been",
        "has", "there", "who", "will", "one", "all", "would", "her"
    ])

def process_books():
    folder = "libros"
    vocabulary = set()
    stop_words = get_stop_words()

    if not os.path.exists(folder):
        print("Carpeta no encontrada.")
        return

    files = [f for f in os.listdir(folder) if f.endswith(".txt")]
    print(f"Procesando vocabulario de {len(files)} libros...")

    for filename in files:
        path = os.path.join(folder, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()

            # 1. Transformar a minusculas
            text = text.lower()

            # 2. Limpieza de caracteres especiales (dejamos solo letras, numeros y espacios)
            text = re.sub(r'[^a-z0-9\s]', '', text)

            # 3. Tokenizacion (split por espacios)
            tokens = text.split()

            # 4. Eliminar stop words y agregar al vocabulario (set evita duplicados)
            for token in tokens:
                if token not in stop_words and len(token) > 1:
                    vocabulary.add(token)

        except Exception as e:
            print(f"Error leyendo {filename}: {e}")

    # Guardar vocabulario
    with open("vocabulario.txt", "w", encoding="utf-8") as f:
        for word in sorted(vocabulary):
            f.write(word + "\n")

    print(f"Vocabulario creado con {len(vocabulary)} palabras unicas.")
    print("Guardado en 'vocabulario.txt'")

if __name__ == "__main__":
    process_books()