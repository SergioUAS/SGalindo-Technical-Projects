def load_data(filename="matriz_similitud.txt"):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            # La primera linea tiene los titulos separados por |
            titles_line = f.readline().strip()
            titles = titles_line.split('|')
            
            matrix = []
            for line in f:
                # Las demas lineas son los valores de similitud
                row = list(map(float, line.strip().split(',')))
                matrix.append(row)
        return titles, matrix
    except FileNotFoundError:
        print("Error: No se encontró el archivo de matriz.")
        return [], []

def get_recommendations(book_name, n=5):
    titles, matrix = load_data()
    
    if book_name not in titles:
        print(f"El libro '{book_name}' no se encuentra en la base de datos.")
        # Imprimimos los primeros 3 para que el usuario vea como se llaman
        if titles:
            print(f"Ejemplos de nombres válidos: {titles[:3]}")
        return []

    # Obtener el indice del libro
    book_idx = titles.index(book_name)
    
    # Obtener la fila de similitudes de ese libro
    scores = matrix[book_idx]
    
    # Crear lista de tuplas (indice, score) ignorando el mismo libro (donde score es > 0.99)
    # Usamos enumerate para guardar la posicion original
    ranked_books = []
    for idx, score in enumerate(scores):
        if idx != book_idx:
            ranked_books.append((idx, score))
    
    # Ordenar de mayor a menor similitud
    ranked_books.sort(key=lambda x: x[1], reverse=True)
    
    # Tomar los top N
    top_books = ranked_books[:n]
    
    results = [titles[idx] for idx, _ in top_books]
    return results

if __name__ == "__main__":
    # Cargar titulos para tomar uno de ejemplo automaticamente
    titles, _ = load_data()
    
    if titles:
        # Probamos con el primer libro de la lista
        test_book = titles[0]
        cant = 5
        
        print(f"--- Recomendando libros basados en: {test_book} ---")
        recomendaciones = get_recommendations(test_book, cant)
        
        for i, libro in enumerate(recomendaciones, 1):
            print(f"{i}. {libro}")
    else:
        print("No hay datos para procesar.")