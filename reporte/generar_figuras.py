"""
Genera las figuras del reporte (reporte/figuras/) y el archivo numeros.tex con las cifras,
a partir de las carpetas de resultados/. Ejecutar desde la carpeta reporte/:

    python generar_figuras.py
"""
import csv
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
RES = os.path.join(RAIZ, "resultados")
FIG = os.path.join(AQUI, "figuras")
sys.path.insert(0, os.path.join(RAIZ, "pintor_evolutivo"))
import pintor_evolutivo as pe  # noqa: E402

os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.size": 9})


def cargar_historial(carpeta):
    with open(os.path.join(carpeta, "historial.csv")) as f:
        return list(csv.DictReader(f))


def mini(im, ancho):
    return im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)


def etiqueta(im, texto):
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 8 + 7 * len(texto), 18], fill=(255, 255, 255))
    d.text((4, 3), texto, fill=(0, 0, 0))
    return im


# ---------- 1. progreso (capturas) ----------
pasos = [25, 200, 1600, 6400, 20000]
filas = []
for estilo in ("vangogh", "monet"):
    c = os.path.join(RES, f"torii_{estilo}")
    ims = [etiqueta(mini(Image.open(os.path.join(c, f"progreso_{n:05d}.jpg")), 260), f"{n} pinceladas") for n in pasos]
    filas.append(ims)
w, h = filas[0][0].size
grid = Image.new("RGB", (5 * w + 4 * 6, 2 * h + 6), "white")
for i, fila in enumerate(filas):
    for j, im in enumerate(fila):
        grid.paste(im, (j * (w + 6), i * (h + 6)))
grid.save(os.path.join(FIG, "progreso.jpg"), quality=88)

# ---------- 2. resultado final ----------
orig = Image.open(os.path.join(RAIZ, "imagenes", "torii.jpg")).convert("RGB")
vg = Image.open(os.path.join(RES, "torii_vangogh", "resultado.png"))
mo = Image.open(os.path.join(RES, "torii_monet", "resultado.png"))
W = 420
trio = [mini(orig, W), mini(vg, W), mini(mo, W)]
fin = Image.new("RGB", (3 * W + 12, trio[0].height), "white")
for i, im in enumerate(trio):
    fin.paste(im, (i * (W + 6), 0))
fin.save(os.path.join(FIG, "final.jpg"), quality=90)

# ---------- 3. detalle (zoom) ----------
caja = (330, 380, 830, 880)   # en la salida de 1200x1600
det = [mini(orig.resize(vg.size).crop(caja), 330), mini(vg.crop(caja), 330), mini(mo.crop(caja), 330)]
dimg = Image.new("RGB", (3 * 330 + 12, 330), "white")
for i, im in enumerate(det):
    dimg.paste(im, (i * 336, 0))
dimg.save(os.path.join(FIG, "detalle.jpg"), quality=90)

# ---------- 4. campo de flujo ----------
img = pe.cargar_Imagen(os.path.join(RAIZ, "imagenes", "torii.jpg"), 300)
obj = pe.preparar_Objetivo(img, pe.ESTILOS["vangogh"])
flujo, coh = pe.campo_de_flujo(obj)
H, Wd = flujo.shape
fig, ax = plt.subplots(1, 3, figsize=(7, 3.2))
ax[0].imshow(obj.astype("uint8")); ax[0].set_title("Objetivo estilizado")
ax[1].imshow(coh, cmap="gray"); ax[1].set_title("Coherencia")
ax[2].imshow(obj.astype("uint8"), alpha=0.35); ax[2].set_title("Campo de flujo")
paso = 10
for y in range(paso // 2, H, paso):
    for x in range(paso // 2, Wd, paso):
        a = flujo[y, x]; d = 0.45 * paso
        ax[2].plot([x - d * np.cos(a), x + d * np.cos(a)], [y - d * np.sin(a), y + d * np.sin(a)], "k-", lw=0.6)
for a in ax:
    a.axis("off")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "flujo.png"), dpi=170); plt.close(fig)

# ---------- 5. convergencia de las corridas finales ----------
fig, ax = plt.subplots(1, 2, figsize=(7, 2.6))
for estilo, nombre in (("vangogh", "Van Gogh"), ("monet", "Monet")):
    h = cargar_historial(os.path.join(RES, f"torii_{estilo}"))
    n = [int(r["pinceladas"]) for r in h]
    ax[0].plot(n, [float(r["mse"]) for r in h], label=nombre)
    acept = np.array([int(r["aceptada"]) for r in h], float)
    ventana = 200
    tasa = np.convolve(acept, np.ones(ventana) / ventana, mode="valid")
    ax[1].plot(n[ventana - 1:], 1 - tasa, label=nombre)
ax[0].set_yscale("log"); ax[0].set_xlabel("pinceladas"); ax[0].set_ylabel("MSE normalizado")
ax[1].set_xlabel("pinceladas"); ax[1].set_ylabel("tasa de etapas rechazadas")
for a in ax:
    a.grid(alpha=0.3); a.legend()
fig.tight_layout(); fig.savefig(os.path.join(FIG, "convergencia_final.png"), dpi=170); plt.close(fig)

# ---------- 6. figuras de experimentos ----------
EXP = os.path.join(RES, "experimentos")
for nombre in ("convergencia_ag_vs_aleatoria.png", "panel_lambda_flujo.jpg"):
    Image.open(os.path.join(EXP, nombre)).convert("RGB").save(
        os.path.join(FIG, nombre if nombre.endswith(".png") else nombre), quality=88)

# ---------- 7. numeros.tex ----------
def res(nombre):
    return json.load(open(os.path.join(EXP, nombre, "res.json")))


m_vg = json.load(open(os.path.join(RES, "torii_vangogh", "metricas.json")))
m_mo = json.load(open(os.path.join(RES, "torii_monet", "metricas.json")))
ag = [res(f"E1_AG_s{s}") for s in range(3)]
al = [res(f"E1_aleatoria_s{s}") for s in range(3)]
e1b = res("E1b_aleatoria_mismo_tiempo")
e2 = {l: res(f"E2_vangogh_lambda{l}") for l in (0.0, 0.04, 0.15)}
k3 = res("E3_K3")
mse_ag, mse_al = np.mean([r["mse"] for r in ag]), np.mean([r["mse"] for r in al])

macros = {
    "vgMSE": f"{m_vg['mse_normalizado_vs_objetivo']:.5f}", "vgPSNR": f"{m_vg['psnr_db_vs_objetivo']:.2f}",
    "vgSSIM": f"{m_vg['ssim_vs_objetivo']:.3f}", "vgTiempo": f"{m_vg['tiempo_s'] / 60:.1f}",
    "vgEtapas": f"{m_vg['etapas']}", "vgRech": f"{m_vg['rechazadas']}",
    "vgEval": f"{m_vg['evaluaciones_fitness'] / 1e6:.2f}",
    "moMSE": f"{m_mo['mse_normalizado_vs_objetivo']:.5f}", "moPSNR": f"{m_mo['psnr_db_vs_objetivo']:.2f}",
    "moSSIM": f"{m_mo['ssim_vs_objetivo']:.3f}", "moTiempo": f"{m_mo['tiempo_s'] / 60:.1f}",
    "moEtapas": f"{m_mo['etapas']}", "moRech": f"{m_mo['rechazadas']}",
    "moEval": f"{m_mo['evaluaciones_fitness'] / 1e6:.2f}",
    "agMSE": f"{mse_ag:.5f}", "agSD": f"{np.std([r['mse'] for r in ag]):.5f}",
    "alMSE": f"{mse_al:.5f}", "alSD": f"{np.std([r['mse'] for r in al]):.5f}",
    "agPSNR": f"{np.mean([r['psnr'] for r in ag]):.2f}", "alPSNR": f"{np.mean([r['psnr'] for r in al]):.2f}",
    "agSSIM": f"{np.mean([r['ssim'] for r in ag]):.3f}", "alSSIM": f"{np.mean([r['ssim'] for r in al]):.3f}",
    "agT": f"{np.mean([r['tiempo_s'] for r in ag]):.0f}", "alT": f"{np.mean([r['tiempo_s'] for r in al]):.0f}",
    "agEval": f"{ag[0]['evaluaciones'] / 1e3:.0f}", "alEval": f"{al[0]['evaluaciones'] / 1e3:.0f}",
    "mejora": f"{100 * (1 - mse_ag / mse_al):.1f}",
    "ebMSE": f"{e1b['mse']:.5f}", "ebPSNR": f"{e1b['psnr']:.2f}", "ebSSIM": f"{e1b['ssim']:.3f}",
    "ebT": f"{e1b['tiempo_s']:.0f}", "ebEval": f"{e1b['evaluaciones'] / 1e3:.0f}",
    "kTresMSE": f"{k3['mse']:.5f}", "kTresT": f"{k3['tiempo_s']:.0f}", "kUnoMSE": f"{ag[0]['mse']:.5f}",
    "kUnoT": f"{ag[0]['tiempo_s']:.0f}",
}
for l, clave in ((0.0, "Cero"), (0.04, "Med"), (0.15, "Alto")):
    macros[f"lam{clave}MSE"] = f"{e2[l]['mse']:.5f}"
    macros[f"lam{clave}Des"] = f"{e2[l]['desalineacion']:.3f}"
    macros[f"lam{clave}SSIM"] = f"{e2[l]['ssim']:.3f}"
with open(os.path.join(AQUI, "numeros.tex"), "w") as f:
    f.write("% Generado automaticamente por generar_figuras.py: no editar a mano\n")
    for k, v in macros.items():
        f.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")
print("Figuras en", FIG)
print("\n".join(f"{k} = {v}" for k, v in macros.items()))
