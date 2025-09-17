import requests
import webbrowser
import re
import time
import random
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from rembg import remove

# --- CONFIGURACIÓN ---

# Headers más completos para evitar bloqueos
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# --- FUNCIONES AUXILIARES ---

def buscar_imagenes_simple(termino_busqueda, tipo="producto"):
    """Método directo: abre Google Images y permite descarga manual rápida"""
    print(f"🔎 Buscando imágenes para: '{termino_busqueda}'...")

    # Abrir directamente Google Images
    search_url = f"https://www.google.com/search?tbm=isch&q={termino_busqueda.replace(' ', '+')}"

    try:
        webbrowser.open(search_url)
        print("🌐 Se abrió Google Images en tu navegador")
        print("👁️ Ve las imágenes y elige la mejor")

    except:
        print("❌ No se pudo abrir el navegador automáticamente")

    return buscar_descarga_rapida(termino_busqueda, tipo)

def buscar_descarga_rapida(termino_busqueda, nombre_sugerido="producto"):
    """Método de descarga rápida guiada"""
    print("\n🚀 Descarga rápida:")
    print("📝 Pasos súper rápidos:")
    print("1. 👀 Mira las imágenes que se abrieron en Google Images")
    print("2. 🖱️ Haz clic derecho en la imagen que te guste")
    print(f"3. 💾 'Guardar imagen como' → guárdala como '{nombre_sugerido}.jpg'")
    print("4. 📁 Ponla en esta misma carpeta")

    input("\n⏸️ Presiona ENTER cuando hayas descargado la imagen...")

    # Buscar archivo descargado con el nombre sugerido
    for ext in ['jpg', 'jpeg', 'png', 'webp']:
        nombre_archivo = f"{nombre_sugerido}.{ext}"
        if os.path.exists(nombre_archivo):
            print(f"✅ ¡Perfecto! Encontré '{nombre_archivo}'")
            return [{'url': nombre_archivo, 'title': 'Imagen descargada', 'width': 0, 'height': 0}]

    # Si no encuentra, listar archivos de imagen en la carpeta
    print(f"\n❌ No encontré '{nombre_sugerido}.jpg'. Archivos de imagen en la carpeta:")
    archivos_imagen = []
    for archivo in os.listdir('.'):
        if archivo.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
            archivos_imagen.append(archivo)
            print(f"📷 {len(archivos_imagen)}. {archivo}")

    if archivos_imagen:
        try:
            opcion = input(f"\n➡️ ¿Cuál archivo quieres usar? (1-{len(archivos_imagen)}): ")
            indice = int(opcion) - 1
            if 0 <= indice < len(archivos_imagen):
                archivo_elegido = archivos_imagen[indice]
                print(f"✅ Usando '{archivo_elegido}'")
                return [{'url': archivo_elegido, 'title': 'Imagen elegida', 'width': 0, 'height': 0}]
        except:
            pass

    print("❌ No se pudo encontrar ninguna imagen")
    return []

def buscar_con_serpapi_simulado(termino_busqueda):
    """Simula búsqueda usando patrones comunes de URLs de productos"""
    print("🤖 Generando URLs probables de productos...")

    # Generar URLs probables basadas en el producto
    producto_limpio = termino_busqueda.lower().replace(' ', '-').replace('funko pop', 'funko-pop')

    urls_probables = [
        f"https://m.media-amazon.com/images/I/61{hash(termino_busqueda) % 999999}.jpg",
        f"https://i.ebayimg.com/images/g/{hash(termino_busqueda + '1') % 999999}/s-l1600.jpg",
        f"https://cdn.shopify.com/s/files/1/products/{producto_limpio}-funko-pop.jpg",
        f"https://images.funkoshop.com/product/{producto_limpio}.jpg",
        f"https://hottopic.scene7.com/is/image/HotTopic/{producto_limpio}",
    ]

    # Verificar cuáles URLs existen
    session = requests.Session()
    session.headers.update(HEADERS)

    urls_validas = []
    for i, url in enumerate(urls_probables):
        try:
            print(f"📡 Verificando URL {i+1}...")
            response = session.head(url, timeout=5)
            if response.status_code == 200:
                urls_validas.append({
                    'url': url,
                    'title': f'Producto encontrado {i+1}',
                    'width': 0,
                    'height': 0
                })
        except:
            continue

    return urls_validas

def buscar_bing_directo(termino_busqueda):
    """Búsqueda directa en Bing Images"""
    print("🔍 Intentando búsqueda directa en Bing...")

    try:
        session = requests.Session()
        session.headers.update(HEADERS)

        # URL de Bing Images más simple
        url = "https://www.bing.com/images/search"
        params = {
            'q': termino_busqueda,
            'qft': '+filterui:imagesize-large',  # Solo imágenes grandes
            'form': 'IRFLTR'
        }

        response = session.get(url, params=params, timeout=10)

        if response.status_code == 200:
            # Buscar patrones de imágenes más generales
            patterns = [
                r'src="([^"]+\.jpg[^"]*)"',
                r'src="([^"]+\.jpeg[^"]*)"',
                r'src="([^"]+\.png[^"]*)"',
                r'data-src="([^"]+\.jpg[^"]*)"',
                r'data-src="([^"]+\.jpeg[^"]*)"',
                r'data-src="([^"]+\.png[^"]*)"'
            ]

            urls_imagenes = []
            for pattern in patterns:
                matches = re.findall(pattern, response.text)
                for match in matches[:5]:
                    if 'http' in match and any(x in match for x in ['amazon', 'ebay', 'funko', 'shop']):
                        urls_imagenes.append({
                            'url': match,
                            'title': f'Imagen de tienda #{len(urls_imagenes)+1}',
                            'width': 0,
                            'height': 0
                        })

                if len(urls_imagenes) >= 6:
                    break

            if urls_imagenes:
                print(f"✅ Encontré {len(urls_imagenes)} imágenes en Bing")
                return urls_imagenes

    except Exception as e:
        print(f"❌ Error en Bing directo: {e}")

    return buscar_metodo_fallback(termino_busqueda)

def buscar_metodo_fallback(termino_busqueda):
    """Método final automático: abrir búsqueda y usar clipboard"""
    print("🚀 Método automático final...")

    # Abrir Google Images automáticamente
    search_url = f"https://www.google.com/search?tbm=isch&q={termino_busqueda.replace(' ', '+')}"

    try:
        webbrowser.open(search_url)
        print("🌐 Se abrió Google Images en tu navegador")
        print("👁️ Las imágenes deberían aparecer automáticamente")

        # Dar URLs de ejemplo mientras tanto
        urls_ejemplo = []
        for i in range(5):
            urls_ejemplo.append({
                'url': f"https://ejemplo-tienda-{i+1}.com/imagen-{hash(termino_busqueda + str(i)) % 999}.jpg",
                'title': f'Imagen de Google Images #{i+1}',
                'width': 400,
                'height': 400
            })

        print("📋 Mostrando opciones de ejemplo (en el navegador verás las reales)")
        return urls_ejemplo

    except:
        return buscar_imagenes_respaldo(termino_busqueda)

def buscar_como_humano(termino_busqueda):
    """Simula búsqueda humana en Google y extrae imágenes de los primeros resultados"""
    print("🔍 Buscando como lo haría un humano en Google...")

    try:
        session = requests.Session()
        session.headers.update(HEADERS)

        # Simular búsqueda en Google normal (no Google Images)
        google_url = "https://www.google.com/search"
        params = {
            'q': termino_busqueda,
            'tbm': '',  # Búsqueda web normal
            'num': 10   # Primeros 10 resultados
        }

        # Delay como humano
        time.sleep(random.uniform(2, 4))

        response = session.get(google_url, params=params, timeout=15)
        response.raise_for_status()

        # Extraer URLs de los primeros resultados
        url_patterns = [
            r'"https://([^"]+amazon[^"]*)"',
            r'"https://([^"]+ebay[^"]*)"',
            r'"https://([^"]+mercadolibre[^"]*)"',
            r'"https://([^"]+hottopic[^"]*)"',
            r'"https://([^"]+gamestop[^"]*)"',
            r'"https://([^"]+funko[^"]*)"',
            r'"https://([^"]+walmart[^"]*)"',
            r'"https://([^"]+target[^"]*)"'
        ]

        sitios_encontrados = []
        for pattern in url_patterns:
            matches = re.findall(pattern, response.text)
            for match in matches[:2]:  # 2 por sitio
                sitio_url = f"https://{match}"
                if sitio_url not in sitios_encontrados:
                    sitios_encontrados.append(sitio_url)

        print(f"🎯 Encontré {len(sitios_encontrados)} sitios de tiendas")

        # Ahora buscar imágenes en esos sitios
        urls_imagenes = []
        for i, sitio in enumerate(sitios_encontrados[:5]):  # Solo los primeros 5
            try:
                print(f"🛒 Extrayendo imágenes del sitio {i+1}...")

                time.sleep(random.uniform(1, 2))
                site_response = session.get(sitio, timeout=10)

                if site_response.status_code == 200:
                    # Buscar imágenes de productos en el sitio
                    img_patterns = [
                        r'<img[^>]+src="([^"]+)"[^>]*>',
                        r'"image":"([^"]+)"',
                        r'"imageUrl":"([^"]+)"',
                        r'"img_src":"([^"]+)"'
                    ]

                    for pattern in img_patterns:
                        imgs = re.findall(pattern, site_response.text)
                        for img_url in imgs[:3]:  # 3 por sitio
                            if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                                if not img_url.startswith('http'):
                                    continue

                                urls_imagenes.append({
                                    'url': img_url,
                                    'title': f'Producto de {sitio.split("/")[2]} #{len(urls_imagenes)+1}',
                                    'width': 0,
                                    'height': 0
                                })

                        if len(urls_imagenes) >= 8:  # Suficientes imágenes
                            break

            except:
                continue

        if urls_imagenes:
            print(f"✅ Encontré {len(urls_imagenes)} imágenes de productos reales")
            return urls_imagenes

    except Exception as e:
        print(f"❌ Error en búsqueda Google: {e}")

    return buscar_imagenes_respaldo(termino_busqueda)

def buscar_imagenes_respaldo(termino_busqueda):
    """Método de respaldo final - búsqueda manual guiada"""
    print("\n🔍 Búsqueda manual en tiendas específicas:")
    print("📋 Te recomendamos buscar en estos sitios:")
    print("1. 🛒 Amazon - amazon.com")
    print("2. 🛒 eBay - ebay.com")
    print("3. 🛒 Hot Topic - hottopic.com")
    print("4. 🛒 GameStop - gamestop.com")
    print("5. 🛒 Funko Shop - funko.com")
    print("6. 🛒 MercadoLibre - mercadolibre.com")

    print(f"\n🔎 Busca: '{termino_busqueda}'")
    print("📝 Pasos:")
    print("1. Ve a cualquiera de esas tiendas")
    print("2. Busca el producto")
    print("3. Haz clic derecho en la imagen del producto → 'Guardar imagen como'")
    print("4. Guárdala como 'imagen_manual.jpg' en esta carpeta")

    respuesta = input("\n➡️ ¿Ya descargaste la imagen? (s/n): ").lower()
    if respuesta == 's':
        # Verificar si existe el archivo
        for ext in ['jpg', 'jpeg', 'png', 'webp']:
            if os.path.exists(f'imagen_manual.{ext}'):
                print(f"✅ Archivo encontrado: imagen_manual.{ext}")
                return [{'url': f'imagen_manual.{ext}', 'title': 'Imagen de tienda', 'width': 0, 'height': 0}]

        print("❌ No se encontró el archivo 'imagen_manual.jpg'")

    return []

def mostrar_opciones_y_descargar(termino_busqueda, nombre_archivo, tipo="producto"):
    """Busca imágenes, las abre en navegador y permite elegir"""
    imagenes = buscar_imagenes_simple(termino_busqueda, tipo)

    if not imagenes:
        print("❌ No se encontraron imágenes.")
        return False

    print(f"\n🌐 Abriendo las primeras {len(imagenes)} imágenes en tu navegador...")
    print("👀 Revisa las pestañas que se abrieron y elige la mejor imagen")

    # Abre las primeras 5 imágenes en el navegador
    for i, img in enumerate(imagenes[:5], 1):
        try:
            webbrowser.open(img['url'])
        except:
            print(f"❌ No se pudo abrir imagen {i}")

    print(f"\n📋 Opciones disponibles:")
    print("-" * 60)

    for i, img in enumerate(imagenes, 1):
        size_info = f"({img['width']}x{img['height']})" if img['width'] > 0 else ""
        print(f"{i}. {img['title']} {size_info}")

    print("-" * 60)

    while True:
        try:
            opcion = input(f"➡️ ¿Cuál imagen te gustó? Elige un número (1-{len(imagenes)}): ")
            indice = int(opcion) - 1

            if 0 <= indice < len(imagenes):
                imagen_elegida = imagenes[indice]
                return descargar_imagen(imagen_elegida['url'], nombre_archivo)
            else:
                print(f"❌ Por favor elige un número entre 1 y {len(imagenes)}")
        except ValueError:
            print("❌ Por favor ingresa un número válido")
        except KeyboardInterrupt:
            print("\n❌ Búsqueda cancelada")
            return False

def descargar_imagen(url, nombre_archivo):
    """Descarga una imagen desde una URL o copia archivo local"""
    try:
        # Si es un archivo local
        if not url.startswith('http'):
            # Si el archivo origen y destino son iguales, no hacer nada
            if url == nombre_archivo:
                print(f"✅ Archivo '{nombre_archivo}' ya está en el lugar correcto")
                return True

            print(f"📁 Copiando archivo local '{url}' como '{nombre_archivo}'...")
            import shutil
            shutil.copy(url, nombre_archivo)
            print(f"✅ Archivo copiado como '{nombre_archivo}'")
            return True

        # Si es una URL normal
        print(f"⬇️ Descargando imagen elegida...")
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        with open(nombre_archivo, 'wb') as f:
            f.write(response.content)

        print(f"✅ Imagen guardada como '{nombre_archivo}'")
        return True

    except Exception as e:
        print(f"❌ Error al descargar imagen: {e}")
        return False

def crear_logo_simple():
    """Crea un logo simple por defecto"""
    logo = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)

    # Dibuja un círculo simple como logo
    draw.ellipse([20, 20, 180, 180], fill=(255, 100, 50, 200), outline=(255, 255, 255, 255), width=3)

    # Agrega texto "LOGO"
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()

    text = "LOGO"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    text_x = (200 - text_width) // 2
    text_y = (200 - text_height) // 2

    draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)

    logo.save("logo.png")
    print("📝 Logo por defecto creado como 'logo.png'")

# --- PROCESO PRINCIPAL ---

def main():
    print("--- Creador Automático de Imágenes para Posts ---")
    
    # 1. OBTENER DATOS DEL USUARIO
    nombre_producto = input("➡️ Ingresa el nombre completo del producto (ej: Funko Pop Goku Super Saiyan): ")
    precio_producto = input("➡️ Ingresa el precio (ej: 125.00): ")
    tema_fondo = input("➡️ Ingresa un tema para el fondo (ej: Dragon Ball Z landscape): ")

    # 2. BÚSQUEDA Y DESCARGA DE IMÁGENES
    print("\n🛍️ Buscando imagen del producto...")
    if not mostrar_opciones_y_descargar(f"{nombre_producto} fondo blanco", "producto_original.png", "producto"):
        return # Si no se puede descargar, detenemos el script

    print("\n🎨 Buscando imagen de fondo...")
    if not mostrar_opciones_y_descargar(f"{tema_fondo} wallpaper 4k", "fondo.jpg", "fondo"):
        return

    # 3. PROCESAMIENTO Y COMPOSICIÓN DE LA IMAGEN
    print("🎨 Creando la imagen del post...")
    
    # Abrimos las imágenes que descargamos
    try:
        input_producto = Image.open("producto_original.png")
        fondo = Image.open("fondo.jpg")

        # Creamos un logo simple si no existe
        if not os.path.exists("logo.png"):
            crear_logo_simple()
        logo = Image.open("logo.png")

    except FileNotFoundError as e:
        print(f"❌ Error: Asegúrate de que el archivo '{e.filename}' esté en la carpeta.")
        return

    # Quitamos el fondo de la imagen del producto
    producto_sin_fondo = remove(input_producto)

    # Creamos el lienzo final de 1080x1080
    lienzo = Image.new('RGB', (1080, 1080), 'white')

    # Ajustamos el fondo para que llene el lienzo cuadrado sin deformarse
    # NUEVO: Adaptamos a la ALTURA completa y centramos horizontalmente
    ratio_fondo = fondo.width / fondo.height
    nuevo_alto = 1080  # Altura completa del lienzo
    nuevo_ancho = int(nuevo_alto * ratio_fondo)  # Ancho proporcional
    fondo = fondo.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)

    # Centramos horizontalmente y recortamos los excesos laterales
    corte_horizontal = (nuevo_ancho - 1080) // 2
    if nuevo_ancho >= 1080:
        # Si el ancho es mayor, recortamos los lados
        fondo = fondo.crop((corte_horizontal, 0, corte_horizontal + 1080, 1080))
    else:
        # Si el ancho es menor, ponemos barras laterales (caso raro)
        fondo_centrado = Image.new('RGB', (1080, 1080), (0, 0, 0))
        pos_x = (1080 - nuevo_ancho) // 2
        fondo_centrado.paste(fondo, (pos_x, 0))
        fondo = fondo_centrado

    # Aplicamos un desenfoque (blur) al fondo para que el producto resalte
    fondo_blur = fondo.filter(ImageFilter.GaussianBlur(radius=8))
    lienzo.paste(fondo_blur, (0, 0))

    # Ajustamos el tamaño del producto y lo pegamos en el lienzo
    producto_sin_fondo.thumbnail((800, 800)) # Reducimos el tamaño para que quepa bien
    pos_x = (1080 - producto_sin_fondo.width) // 2
    pos_y = (1080 - producto_sin_fondo.height) // 2 - 50 # Un poco más arriba del centro
    lienzo.paste(producto_sin_fondo, (pos_x, pos_y), producto_sin_fondo) # El tercer parámetro es la máscara para la transparencia

    # Ajustamos el tamaño del logo y lo pegamos
    logo.thumbnail((200, 200))
    lienzo.paste(logo, (1080 - logo.width - 40, 1080 - logo.height - 40), logo)

    # Añadimos el precio
    draw = ImageDraw.Draw(lienzo)
    try:
        # Asegúrate de tener 'arial.ttf' en la misma carpeta o pon la ruta completa
        font = ImageFont.truetype("arial.ttf", 90) 
    except IOError:
        print("❌ No se encontró el archivo de fuente 'arial.ttf'. Usando fuente por defecto.")
        font = ImageFont.load_default()
        
    texto_precio = f"S/ {precio_producto}"
    bbox = draw.textbbox((0, 0), texto_precio, font=font)
    ancho_texto = bbox[2] - bbox[0]
    alto_texto = bbox[3] - bbox[1]
    
    pos_precio_x = (1080 - ancho_texto) // 2
    pos_precio_y = 1080 - alto_texto - 80
    
    # Dibujamos un rectángulo semi-transparente detrás del texto para que se lea mejor
    draw.rectangle(
        (pos_precio_x - 20, pos_precio_y - 15, pos_precio_x + ancho_texto + 20, pos_precio_y + alto_texto + 15),
        fill=(0, 0, 0, 128) # Negro con 50% de transparencia
    )
    draw.text((pos_precio_x, pos_precio_y), texto_precio, font=font, fill="white")

    # Guardamos la imagen final
    nombre_final = f"{nombre_producto.replace(' ', '_').lower()}_post.png"
    lienzo.save(nombre_final)
    
    print("\n---------------------------------")
    print(f"🎉 ¡Éxito! La imagen ha sido creada.")
    print(f"Busca el archivo: '{nombre_final}' en tu carpeta.")
    print("---------------------------------")


# Esto hace que la función main() se ejecute cuando corres el script
if __name__ == "__main__":
    main()

