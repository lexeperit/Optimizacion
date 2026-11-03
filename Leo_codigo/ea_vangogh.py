"""
Algoritmo Evolutivo para "pintar" una imagen con pinceladas estilo Van Gogh.
Referencia: Engelbrecht, Computational Intelligence, 2a ed., Cap. 8-9 (GA / EP / ES).

IDEA GENERAL
------------
- El lienzo se construye por ETAPAS. En cada etapa se evoluciona un bloque de K pinceladas
  que se pintan ENCIMA del lienzo acumulado (pintura por capas, como un pintor real).
- Cromosoma (individuo) = K pinceladas. Cada pincelada es un vector de 9 genes reales:
      [x, y, angulo, largo, grosor, alpha, r, g, b]   (todos normalizados a [0,1])
- Fitness (a MINIMIZAR):
      f = MSE(lienzo_con_pinceladas, objetivo) / 255^2  +  lambda_flujo * penalizacion_angulo
  La penalizacion de angulo premia que la pincelada siga las "lineas de flujo" de la imagen
  (perpendicular al gradiente), que es lo que da el aspecto de Van Gogh.
- Operadores (Engelbrecht cap. 9):
      Seleccion: torneo (tamano 3)
      Cruza:     BLX-alpha (blend crossover) para genes reales
      Mutacion:  gaussiana con sigma que decrece con las generaciones
      Elitismo:  el mejor individuo pasa intacto a la siguiente generacion
- Coarse-to-fine: las primeras etapas usan pinceladas grandes, las ultimas pequenas.

Uso:
    python ea_vangogh.py ../Angie_codigo/vanGogh2.jpeg --pinceladas 600
"""
import argparse
import math
import os
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

N_GENES = 9  # x, y, angulo, largo, grosor, alpha, r, g, b


# ----------------------------------------------------------------------------
# Imagen objetivo y campo de flujo (direccion "natural" de las pinceladas)
# ----------------------------------------------------------------------------
def cargar_objetivo(ruta, ancho_max):
    img = Image.open(ruta).convert("RGB")
    if img.width > ancho_max:
        img = img.resize((ancho_max, int(img.height * ancho_max / img.width)), Image.LANCZOS)
    return np.asarray(img, dtype=np.float32)


def campo_de_flujo(objetivo):
    """Angulo de la linea de flujo en cada pixel = perpendicular al gradiente (Sobel)."""
    gris = Image.fromarray(objetivo.astype(np.uint8)).convert("L").filter(ImageFilter.GaussianBlur(3))
    g = np.asarray(gris, dtype=np.float32)
    gx = np.zeros_like(g); gy = np.zeros_like(g)
    gx[:, 1:-1] = g[:, 2:] - g[:, :-2]
    gy[1:-1, :] = g[2:, :] - g[:-2, :]
    return np.arctan2(gy, gx) + math.pi / 2  # perpendicular al gradiente


# ----------------------------------------------------------------------------
# Decodificar y dibujar pinceladas (fenotipo)
# ----------------------------------------------------------------------------
def decodificar(gen, H, W, largo_max, grosor_max):
    x = gen[0] * (W - 1)
    y = gen[1] * (H - 1)
    ang = gen[2] * math.pi                      # una linea es simetrica: [0, pi)
    largo = 2 + gen[3] * largo_max
    grosor = max(1, int(1 + gen[4] * grosor_max))
    alpha = int(60 + gen[5] * 195)              # transparencia en [60, 255]
    color = tuple(int(c * 255) for c in gen[6:9])
    return x, y, ang, largo, grosor, alpha, color


def pintar(lienzo, cromosoma, H, W, largo_max, grosor_max):
    """Dibuja las K pinceladas del cromosoma encima del lienzo (con transparencia)."""
    capa = lienzo.copy()
    for gen in cromosoma:
        x, y, ang, largo, grosor, alpha, color = decodificar(gen, H, W, largo_max, grosor_max)
        dx, dy = 0.5 * largo * math.cos(ang), 0.5 * largo * math.sin(ang)
        overlay = Image.new("RGBA", capa.size, (0, 0, 0, 0))
        ImageDraw.Draw(overlay).line([(x - dx, y - dy), (x + dx, y + dy)],
                                     fill=color + (alpha,), width=grosor, joint="curve")
        capa = Image.alpha_composite(capa, overlay)
    return capa


# ----------------------------------------------------------------------------
# Fitness
# ----------------------------------------------------------------------------
def fitness(cromosoma, lienzo, objetivo, flujo, cfg):
    H, W = objetivo.shape[:2]
    img = pintar(lienzo, cromosoma, H, W, cfg["largo_max"], cfg["grosor_max"])
    arr = np.asarray(img, dtype=np.float32)[..., :3]
    mse = np.mean((arr - objetivo) ** 2) / (255.0 ** 2)
    # penalizacion: diferencia entre angulo de la pincelada y el flujo local (0 = alineada)
    pen = 0.0
    for gen in cromosoma:
        xi, yi = int(gen[0] * (W - 1)), int(gen[1] * (H - 1))
        d = gen[2] * math.pi - flujo[yi, xi]
        pen += abs(math.sin(d))                 # 0 si paralela, 1 si perpendicular
    return mse + cfg["lambda_flujo"] * pen / len(cromosoma) * 1e-3


# ----------------------------------------------------------------------------
# Operadores evolutivos
# ----------------------------------------------------------------------------
def individuo_aleatorio(K, objetivo, flujo, rng):
    """Inicializacion heuristica: color y angulo muestreados de la imagen objetivo."""
    H, W = objetivo.shape[:2]
    ind = rng.random((K, N_GENES))
    for g in ind:
        xi, yi = int(g[0] * (W - 1)), int(g[1] * (H - 1))
        g[6:9] = objetivo[yi, xi] / 255.0
        g[2] = (flujo[yi, xi] % math.pi) / math.pi
    return ind


def torneo(pob, fit, rng, k=3):
    idx = rng.choice(len(pob), k, replace=False)
    return pob[idx[np.argmin(fit[idx])]]


def cruza_blx(p1, p2, rng, alpha=0.3):
    lo, hi = np.minimum(p1, p2), np.maximum(p1, p2)
    d = hi - lo
    return rng.uniform(lo - alpha * d, hi + alpha * d)


def mutacion_gauss(ind, sigma, pm, rng):
    mask = rng.random(ind.shape) < pm
    ind = ind + mask * rng.normal(0, sigma, ind.shape)
    ind[:, 2] %= 1.0                            # el angulo es circular
    return np.clip(ind, 0, 1)


def evolucionar_etapa(lienzo, objetivo, flujo, cfg, rng):
    P, G, K = cfg["poblacion"], cfg["generaciones"], cfg["K"]
    pob = np.array([individuo_aleatorio(K, objetivo, flujo, rng) for _ in range(P)])
    fit = np.array([fitness(i, lienzo, objetivo, flujo, cfg) for i in pob])
    for gen in range(G):
        sigma = cfg["sigma0"] * (1 - gen / G) + 0.01
        elite = pob[np.argmin(fit)].copy()
        hijos = [elite]
        while len(hijos) < P:
            p1, p2 = torneo(pob, fit, rng), torneo(pob, fit, rng)
            h = cruza_blx(p1, p2, rng) if rng.random() < cfg["pc"] else p1.copy()
            hijos.append(mutacion_gauss(h, sigma, cfg["pm"], rng))
        pob = np.array(hijos)
        fit = np.array([fitness(i, lienzo, objetivo, flujo, cfg) for i in pob])
    b = np.argmin(fit)
    return pob[b], fit[b]


# ----------------------------------------------------------------------------
# Programa principal
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("imagen")
    ap.add_argument("--pinceladas", type=int, default=600)
    ap.add_argument("--ancho", type=int, default=200)
    ap.add_argument("--K", type=int, default=5, help="pinceladas por etapa (tamano del cromosoma)")
    ap.add_argument("--poblacion", type=int, default=16)
    ap.add_argument("--generaciones", type=int, default=12)
    ap.add_argument("--lambda_flujo", type=float, default=5.0)
    ap.add_argument("--salida", default="salida")
    ap.add_argument("--semilla", type=int, default=0)
    a = ap.parse_args()

    rng = np.random.default_rng(a.semilla)
    objetivo = cargar_objetivo(a.imagen, a.ancho)
    flujo = campo_de_flujo(objetivo)
    H, W = objetivo.shape[:2]
    os.makedirs(a.salida, exist_ok=True)

    # Lienzo inicial: color promedio de la imagen
    prom = tuple(int(c) for c in objetivo.reshape(-1, 3).mean(0))
    lienzo = Image.new("RGBA", (W, H), prom + (255,))

    etapas = a.pinceladas // a.K
    historial = []
    t0 = time.time()
    for e in range(etapas):
        prog = e / etapas                        # coarse-to-fine
        cfg = dict(poblacion=a.poblacion, generaciones=a.generaciones, K=a.K,
                   pc=0.8, pm=0.3, sigma0=0.15, lambda_flujo=a.lambda_flujo,
                   largo_max=W * (0.35 * (1 - prog) + 0.06),
                   grosor_max=W * (0.08 * (1 - prog) + 0.015))
        mejor, f = evolucionar_etapa(lienzo, objetivo, flujo, cfg, rng)
        lienzo = pintar(lienzo, mejor, H, W, cfg["largo_max"], cfg["grosor_max"])
        historial.append(f)
        if e % max(1, etapas // 10) == 0 or e == etapas - 1:
            print(f"etapa {e+1}/{etapas}  pinceladas={(e+1)*a.K}  fitness={f:.5f}  t={time.time()-t0:.0f}s")
            lienzo.convert("RGB").save(os.path.join(a.salida, f"progreso_{(e+1)*a.K:04d}.png"))

    lienzo.convert("RGB").save(os.path.join(a.salida, "resultado.png"))
    Image.fromarray(objetivo.astype(np.uint8)).save(os.path.join(a.salida, "objetivo.png"))
    np.savetxt(os.path.join(a.salida, "fitness.csv"), historial, delimiter=",")
    print("Listo ->", os.path.join(a.salida, "resultado.png"))


if __name__ == "__main__":
    main()
