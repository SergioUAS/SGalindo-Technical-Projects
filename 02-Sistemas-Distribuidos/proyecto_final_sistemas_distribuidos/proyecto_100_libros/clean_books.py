import os

def clean_content(text):
    # Marcadores comunes en Project Gutenberg
    start_markers = ["*** START OF", "***START OF"]
    end_markers = ["*** END OF", "***END OF"]
    
    start_idx = -1
    end_idx = -1

    # Buscar inicio
    for marker in start_markers:
        idx = text.find(marker)
        if idx != -1:
            # Buscar el salto de linea despues del marcador para no incluirlo
            start_idx = text.find('\n', idx) + 1
            break
            
    # Buscar fin
    for marker in end_markers:
        idx = text.rfind(marker)
        if idx != -1:
            end_idx = idx
            break

    # Si se encuentran ambos, recortar. Si no, devolver texto original.
    if start_idx != -1 and end_idx != -1:
        return text[start_idx:end_idx]
    return text

def main():
    folder = "libros"
    if not os.path.exists(folder):
        print(f"Carpeta {folder} no encontrada.")
        return

    files = os.listdir(folder)
    print(f"Limpiando {len(files)} libros...")

    for filename in files:
        if not filename.endswith(".txt"):
            continue
            
        path = os.path.join(folder, filename)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            new_content = clean_content(content)
            
            # Sobreescribimos el archivo con la versión limpia
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
        except Exception as e:
            print(f"Error en {filename}: {e}")

    print("Limpieza terminada.")

if __name__ == "__main__":
    main()