"""
Experimentos para el reporte (todos con la misma imagen, 300 px de ancho y 3000 pinceladas):

  E1. AG vs busqueda aleatoria guiada con el MISMO numero de evaluaciones de fitness
      (3 semillas cada uno, estilo "libre" = solo MSE).
  E1b. Busqueda aleatoria con ~30% mas evaluaciones (= mismo TIEMPO que el AG).
  E2. Efecto del termino de flujo (lambda_flujo = 0, 0.04, 0.15) en el estilo Van Gogh.
  E3. Tamano del cromosoma: K = 1 vs K = 3 pinceladas por individuo.

Uso:  python experimentos.py ../imagenes/torii.jpg  [--procesos 2] [--pinceladas 3000] [--solo E2]
Salida: ../resultados/experimentos/ (resumen.csv, convergencia_*.png, paneles de imagenes)
"""
import argparse
import json
import os
import time
from multiprocessing import Pool

import numpy as np
from PIL import Image

import pintor_evolutivo as pe

SALIDA = os.path.join("..", "resultados", "experimentos")


def correr(cfg):
    nombre, imagen, total, kw = cfg
    t = time.time()
    p = pe.Pintor(imagen, ancho=300, escala_salida=2, **kw)
    p.pintar(total, None, verbose=False)
    carpeta = os.path.join(SALIDA, nombre)
    os.makedirs(carpeta, exist_ok=True)
    p.lienzo.generate_image().save(os.path.join(carpeta, "resultado.jpg"), quality=92)
    res = {"nombre": nombre, "mse": p.lienzo.mse(), "psnr": p.lienzo.psnr(),
           "ssim": pe.ssim(p.lienzo.lienzo, p.objetivo), "desalineacion": p.desalineacion_Flujo(),
           "evaluaciones": p.ag.evaluaciones, "rechazadas": p.rechazadas,
           "tiempo_s": time.time() - t,
           "curva": [(h["pinceladas"], h["mse"]) for h in p.historial]}
    with open(os.path.join(carpeta, "res.json"), "w") as f:
        json.dump(res, f)
    print(f"{nombre:28s} MSE={res['mse']:.5f} PSNR={res['psnr']:.2f} SSIM={res['ssim']:.3f} "
          f"desal={res['desalineacion']:.3f} t={res['tiempo_s']:.0f}s", flush=True)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("imagen")
    ap.add_argument("--procesos", type=int, default=2)
    ap.add_argument("--pinceladas", type=int, default=3000)
    ap.add_argument("--solo", default="", help="corre solo los experimentos cuyo nombre empieza asi")
    a = ap.parse_args()
    os.makedirs(SALIDA, exist_ok=True)
    T = a.pinceladas
    cfgs = []
    for s in range(3):                                                   # E1
        cfgs.append((f"E1_AG_s{s}", a.imagen, T, dict(estilo="libre", semilla=s)))
        cfgs.append((f"E1_aleatoria_s{s}", a.imagen, T, dict(estilo="libre", semilla=s, busqueda_aleatoria=True)))
    for lam in (0.0, 0.04, 0.15):                                        # E2
        cfgs.append((f"E2_vangogh_lambda{lam}", a.imagen, T, dict(estilo="vangogh", lambda_flujo=lam)))
    cfgs.append(("E1b_aleatoria_mismo_tiempo", a.imagen, T,                # E1b: 21*13 = 273 evals/etapa
                 dict(estilo="libre", busqueda_aleatoria=True, poblacion=21)))
    cfgs.append(("E3_K3", a.imagen, T, dict(estilo="libre", K=3)))        # E3 (K=1 = E1_AG_s0)
    cfgs = [c for c in cfgs if c[0].startswith(a.solo)]

    with Pool(a.procesos) as pool:
        for _ in pool.imap(correr, cfgs):
            pass
    res = {}                                    # resumen con TODO lo que haya en la carpeta
    for d in sorted(os.listdir(SALIDA)):
        f = os.path.join(SALIDA, d, "res.json")
        if os.path.exists(f):
            res[d] = json.load(open(f))
    if not all(f"E1_{g}_s{s}" in res for g in ("AG", "aleatoria") for s in range(3)):
        return

    # ---- resumen ----
    with open(os.path.join(SALIDA, "resumen.csv"), "w") as f:
        f.write("experimento,mse,psnr,ssim,desalineacion,evaluaciones,rechazadas,tiempo_s\n")
        for r in res.values():
            f.write(f"{r['nombre']},{r['mse']:.6f},{r['psnr']:.3f},{r['ssim']:.4f},{r['desalineacion']:.4f},"
                    f"{r['evaluaciones']},{r['rechazadas']},{r['tiempo_s']:.1f}\n")
    for grupo in ("AG", "aleatoria"):
        m = [res[f"E1_{grupo}_s{s}"]["mse"] for s in range(3)]
        print(f"E1 {grupo}: MSE = {np.mean(m):.5f} +- {np.std(m):.5f}")

    # ---- grafica E1 ----
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    for grupo, color in (("AG", "tab:blue"), ("aleatoria", "tab:orange")):
        for s in range(3):
            n, m = zip(*res[f"E1_{grupo}_s{s}"]["curva"])
            ax.plot(n, m, color=color, lw=1, alpha=0.8,
                    label=("AG (torneo + BLX + mutación)" if grupo == "AG" else "Búsqueda aleatoria guiada") if s == 0 else None)
    ax.set_yscale("log"); ax.set_xlabel("pinceladas"); ax.set_ylabel("MSE normalizado")
    ax.grid(alpha=0.3); ax.legend(); fig.tight_layout()
    fig.savefig(os.path.join(SALIDA, "convergencia_ag_vs_aleatoria.png"), dpi=150); plt.close(fig)

    # ---- panel E2 (lambda de flujo) ----
    if not all(f"E2_vangogh_lambda{l}" in res for l in (0.0, 0.04, 0.15)):
        return
    ims = [Image.open(os.path.join(SALIDA, f"E2_vangogh_lambda{l}", "resultado.jpg")) for l in (0.0, 0.04, 0.15)]
    w, h = ims[0].size
    panel = Image.new("RGB", (3 * w + 20, h), "white")
    for i, im in enumerate(ims):
        panel.paste(im, (i * (w + 10), 0))
    panel.save(os.path.join(SALIDA, "panel_lambda_flujo.jpg"), quality=90)


if __name__ == "__main__":
    main()
