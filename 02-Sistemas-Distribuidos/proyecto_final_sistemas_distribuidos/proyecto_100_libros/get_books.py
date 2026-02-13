import re
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import os

def get_links(n=-1):
    url = "https://www.gutenberg.org/browse/scores/top"
    try:
        response = requests.get(url)
        parser = BeautifulSoup(response.text, 'html.parser')
        
        ordered_list = parser.find('ol')
        list_items = ordered_list.find_all('li')
        
        if n != -1:
            indices = list(n) if isinstance(n, (list, range)) else [n]
            list_filtered = [list_items[i-1] for i in indices if i-1 < len(list_items)]
        else:
            list_filtered = list_items

        prefix = "https://www.gutenberg.org"
        suffix = ".txt.utf-8"
        
        links, titles = [], []
        
        for li in list_filtered:
            try:
                href = li.find("a").get("href")
                if href:
                    links.append(prefix + href + suffix)
                    
                    # --- AQUÍ ESTÁ LA MAGIA DE LA LIMPIEZA ---
                    # 1. Obtenemos el texto
                    raw_title = li.get_text()
                    # 2. Reemplazamos CUALQUIER carácter que no sea letra/número por nada
                    clean_title = re.sub(r'[^\w\s]', '', raw_title)
                    # 3. Reemplazamos espacios por guiones bajos
                    title = re.sub(r'\s+', '_', clean_title)
                    # 4. Quitamos números finales
                    title = re.sub(r'_\d+$', '', title)
                    title += '.txt'
                    titles.append(title)
            except AttributeError:
                continue
        
        # Esta línea es la que faltaba o fallaba antes:
        return links, titles
        
    except Exception as e:
        print(f"Error: {e}")
        return [], []

def download_file(url, name):
    try:
        if not os.path.exists('libros'):
            os.makedirs('libros')
        file_path = os.path.join('libros', name)
        response = requests.get(url, stream=True)
        with open(file_path, mode='wb') as file:
            for chunk in response.iter_content(chunk_size=10240):
                file.write(chunk)
        print(f"Descargado: {name}")
    except Exception as e:
        print(f"Error en {name}: {e}")

def store_files(links, names):
    with ThreadPoolExecutor() as executor:
        executor.map(download_file, links, names)

def main(n=-1):
    links, titles = get_links(n)
    if links:
        print(f"Descargando {len(links)} libros...")
        store_files(links, titles)
        print("¡Listo!")
    else:
        print("No se encontraron enlaces.")

if __name__ == "__main__":
    n = range(1, 101)
    main(n)