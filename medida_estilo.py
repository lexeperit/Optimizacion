import numpy as np
from PIL import Image

ancho_medida = 400   # todas las imagenes se miden al mismo ancho

def preparar(img):
    img = img.convert("RGB")
    return img.resize((ancho_medida, int(img.height * ancho_medida / img.width)))

# paleta: histograma de tono, saturacion y brillo
def histograma_color(img):
    hsv = np.array(img.convert("HSV")).reshape(-1, 3)
    h, _ = np.histogramdd(hsv, bins=(12, 4, 4), range=((0, 256), (0, 256), (0, 256)))
    h = h.flatten()
    return h / h.sum()

def gradiente(img):
    gris = np.array(img.convert("L")).astype(float)
    gy, gx = np.gradient(gris)
    return gx, gy

# textura: que tan fuertes son los bordes
def histograma_bordes(img):
    gx, gy = gradiente(img)
    magnitud = np.minimum(np.sqrt(gx**2 + gy**2), 99.9)
    h, _ = np.histogram(magnitud, bins=20, range=(0, 100))
    return h / h.sum()

# orientacion: que tan alineados estan los bordes en bloques de 8x8 (1 = todos en la misma direccion)
def histograma_coherencia(img):
    gx, gy = gradiente(img)
    alto, ancho = (gx.shape[0] // 8) * 8, (gx.shape[1] // 8) * 8
    def bloques(m):
        return m[:alto, :ancho].reshape(alto // 8, 8, ancho // 8, 8).mean(axis=(1, 3))
    jxx, jyy, jxy = bloques(gx * gx), bloques(gy * gy), bloques(gx * gy)
    coherencia = np.sqrt((jxx - jyy)**2 + 4 * jxy**2) / (jxx + jyy + 1e-9)
    h, _ = np.histogram(coherencia, bins=10, range=(0, 1))
    return h / h.sum()

def interseccion(h1, h2):
    return np.minimum(h1, h2).sum()   # 1 = histogramas iguales

def distancias(img, referencia):
    img, referencia = preparar(img), preparar(referencia)
    return [1 - interseccion(histograma_color(img), histograma_color(referencia)),
            1 - interseccion(histograma_bordes(img), histograma_bordes(referencia)),
            1 - interseccion(histograma_coherencia(img), histograma_coherencia(referencia))]

# 0 = igual que la foto, 1 = igual que la pintura de referencia
def porcentaje_estilo(img, foto, referencia):
    d_img = np.mean(distancias(img, referencia))
    d_foto = np.mean(distancias(foto, referencia))
    return 1 - d_img / d_foto


# uso: python medida_estilo.py resultados_fase3_vangogh/resultado.png
# compara contra la noche estrellada; 0% = igual que la foto, 100% = igual que la pintura
if __name__ == "__main__":
    import sys
    nombre_salida = sys.argv[1]
    nombre_foto = "imagenes/torii.jpg"
    nombre_referencia = "imagenes/noche_estrellada.jpg"
    if len(sys.argv) > 2:
        nombre_foto = sys.argv[2]
    if len(sys.argv) > 3:
        nombre_referencia = sys.argv[3]

    salida = Image.open(nombre_salida)
    foto = Image.open(nombre_foto)
    referencia = Image.open(nombre_referencia)

    d = distancias(salida, referencia)
    d_foto = distancias(foto, referencia)
    print("parecido de color:      " + str(round(1 - d[0], 2)) + "   (foto: " + str(round(1 - d_foto[0], 2)) + ")")
    print("parecido de bordes:     " + str(round(1 - d[1], 2)) + "   (foto: " + str(round(1 - d_foto[1], 2)) + ")")
    print("parecido de coherencia: " + str(round(1 - d[2], 2)) + "   (foto: " + str(round(1 - d_foto[2], 2)) + ")")
    print("estilo total: " + str(round(100 * porcentaje_estilo(salida, foto, referencia), 1)) + " %")
    print("estilo del trazo (sin color): " + str(round(100 * (1 - ((d[1] + d[2]) / 2) / ((d_foto[1] + d_foto[2]) / 2)), 1)) + " %")
