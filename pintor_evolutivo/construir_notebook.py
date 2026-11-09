"""
Construye Pintor_Evolutivo.ipynb a partir de pintor_evolutivo.py.

Cada seccion "# %% N. Titulo" del script se vuelve una celda de codigo, precedida por una
celda de texto que la explica. Asi el notebook y el script tienen EXACTAMENTE el mismo
algoritmo: si cambias el .py, vuelve a correr este archivo.

    python construir_notebook.py            # solo construye
    python construir_notebook.py --ejecutar # construye y ejecuta (guarda las salidas)
"""
import re
import subprocess
import sys

import nbformat as nbf

FUENTE = "pintor_evolutivo.py"
DESTINO = "Pintor_Evolutivo.ipynb"

INTRO = r"""# Pintor Evolutivo: replicar una imagen con pinceladas estilo Van Gogh y Monet

**Materia:** Optimización. **Base teórica:** A. P. Engelbrecht, *Computational Intelligence: An Introduction*, 2.ª ed., caps. 8 (Computación Evolutiva) y 9 (Algoritmos Genéticos).

**Idea:** un algoritmo genético (AG) de codificación real coloca, una por una, miles de pinceladas sobre un lienzo. Cada pincelada se describe con 10 genes (posición, ángulo, largo, grosor, transparencia, color RGB y curvatura). El AG busca la pincelada que más reduce la diferencia entre el lienzo y la imagen objetivo. El estilo (Van Gogh o Monet) cambia la forma de las pinceladas, la manera de interpretar la foto y la función de fitness.

**Este notebook combina el trabajo del equipo:**
| Aporte | De quién |
|---|---|
| Clases `Pincelada`, `Pincelada_Randomizer`, `ImagenEvolutiva`, `AlgoritmoEvolutivo`; pinceladas `line`/`arc`; color tomado de la imagen; `hedge_array` | Angie |
| Genes reales en [0,1], torneo, cruza BLX-α, mutación gaussiana con σ decreciente, elitismo, pintura por etapas (de lo grueso a lo fino), campo de flujo | Leo |

**Cómo usarlo:**
- **Jupyter local:** abre este archivo desde la carpeta `pintor_evolutivo/` del repositorio y ejecuta *Run All*.
- **Google Colab:** sube el notebook y ejecuta todo. La primera celda te pedirá subir la imagen si no la encuentra.

El código de las secciones 1–10 es **idéntico** al de `pintor_evolutivo.py`: el notebook se genera con `construir_notebook.py`.
"""

PREPARACION = r'''# Preparacion: localizar la imagen de entrada (en Colab permite subirla)
import os, sys
EN_COLAB = "google.colab" in sys.modules
RUTA_IMAGEN = "../imagenes/torii.jpg"          # cambia aqui la imagen de entrada
if not os.path.exists(RUTA_IMAGEN):
    if EN_COLAB:
        from google.colab import files
        print("Sube la imagen de entrada (jpg/png):")
        subida = files.upload()
        RUTA_IMAGEN = next(iter(subida))
    else:
        raise FileNotFoundError(f"No encuentro {RUTA_IMAGEN}: cambia RUTA_IMAGEN")
print("Imagen de entrada:", RUTA_IMAGEN)'''

EXPLICACIONES = {
    "1": r"""## 1. Librerías y constantes
Solo se usan **NumPy** y **Pillow** (y matplotlib para las gráficas). Cada pincelada es un vector de **10 genes reales en [0, 1]**:

| índice | gen | significado |
|---|---|---|
| 0, 1 | x, y | centro de la pincelada |
| 2 | ángulo | orientación del trazo ("ángulo de ataque"), de 0 a π |
| 3 | largo | longitud, relativa al tamaño de la etapa |
| 4 | grosor | ancho del pincel (vía la relación largo/grosor del estilo) |
| 5 | alpha | transparencia (opacidad) |
| 6–8 | r, g, b | color |
| 9 | curvatura | 0.5 = recta (`line`); lejos de 0.5 = arco (`arc`) |

Normalizar todo a [0, 1] permite usar **los mismos operadores** (cruza y mutación) para todos los genes.""",
    "2": r"""## 2. Estilos artísticos
Un estilo es un diccionario de parámetros que actúa en tres lugares:

1. **Objetivo estilizado:** cómo "ve" la foto el pintor. Van Gogh satura y contrasta; Monet aclara y suaviza (el impresionismo no reproduce detalles finos).
2. **Forma de la pincelada:** Van Gogh usa trazos largos, opacos (empaste) y curvos que siguen el flujo. Monet usa toques cortos, anchos y semitransparentes.
3. **Fitness:** `lambda_flujo` premia que la pincelada siga las líneas de la imagen (Van Gogh) o lo desactiva (Monet).

El estilo `libre` no aplica ningún estilo y sirve como línea base en los experimentos.""",
    "3": r"""## 3. Imagen objetivo y campo de flujo
- El AG trabaja a **baja resolución** (300–400 px de ancho) para que sea rápido. El resultado se vuelve a dibujar en alta resolución, porque las pinceladas son vectoriales.
- **Campo de flujo:** con el *tensor de estructura* $J=\mathrm{suavizado}\begin{pmatrix}g_x^2 & g_xg_y\\ g_xg_y & g_y^2\end{pmatrix}$ se obtiene la dirección dominante del gradiente $\theta=\tfrac12\operatorname{atan2}(2J_{xy},J_{xx}-J_{yy})$. El **flujo** es perpendicular a ella, $\theta+\pi/2$, es decir, corre *a lo largo* de los bordes. La **coherencia** en [0, 1] indica qué tan clara es esa dirección.""",
    "4": r"""## 4. Clase `Pincelada` (fenotipo)
Conserva los atributos del diseño de Angie (`points`, `size`, `width`, `angle`, `color`, `tipo`, `start`, `end`) y agrega `alpha` y `curvatura`.
- `from_Genes` es la **decodificación genotipo → fenotipo**: convierte los 10 números en [0,1] a píxeles, grados y colores.
- Los arcos se dibujan como una polilínea sobre un círculo de radio `size/|curvatura|`. `start` y `end` equivalen a los ángulos de `ImageDraw.arc` que usaba Angie.""",
    "5": r"""## 5. Rasterizado
Para evaluar rápido, cada pincelada se dibuja **solo dentro de su caja envolvente**, no en todo el lienzo. La mezcla es *alpha blending*:
$$\text{nuevo} = \text{viejo}\,(1-a) + \text{color}\,a$$
La textura de cerdas (rayas paralelas al trazo) es solo visual. Se aplica al pintar de verdad, no al evaluar.""",
    "6": r"""## 6. Clase `ImagenEvolutiva` (el lienzo)
- Guarda `lista_pinceladas` y `hedge_array` (mapa de cobertura), como en el diseño de Angie y Leo.
- Mantiene `err_map`, el error de cada píxel. Así, **evaluar** una pincelada solo requiere recalcular el error dentro de su caja: $\Delta E = E_{\text{nuevo}}(\text{caja}) - E_{\text{viejo}}(\text{caja})$. El resultado es exacto y cientos de veces más rápido que medir toda la imagen.
- `evaluar` pinta, mide y **deshace**. `add_Pincelada` pinta de verdad, tanto en baja como en alta resolución.""",
    "7": r"""## 7. Clase `Pincelada_Randomizer` (inicialización)
Es la idea de Angie de generar pinceladas al azar, pero **guiada** (inicialización heurística):
- la posición se elige cerca de un **foco**, que se sortea con probabilidad proporcional al error del lienzo;
- el color se toma de la imagen **en esa posición** (más una pequeña variación);
- el ángulo sigue el flujo (Van Gogh) o es aleatorio (Monet);
- el tipo `line`/`arc` se elige al azar.""",
    "8": r"""## 8. Clase `AlgoritmoEvolutivo` (AG de codificación real)
**Cromosoma** = matriz $K\times10$ ($K$ pinceladas; por defecto $K=1$). **Población** = 16 cromosomas, **12 generaciones** por etapa.

**Fitness (minimizar):**
$$f = \underbrace{\frac{\sum_{p}\lVert L_p - O_p\rVert^2}{N\cdot 3\cdot 255^2}}_{\text{MSE normalizado}} \;+\; \lambda_{\text{flujo}}\,\frac{1}{N}\sum_k A_k\,w_k\,\sin^2(\theta_k-\phi(x_k,y_k)) \;+\; \lambda_{\text{hedge}}\,(1-\text{cobertura})$$
donde $A_k$ es el área del trazo, $w_k = 0.25+0.75\cdot\text{coherencia}$ y $\phi$ es el flujo.

**Operadores (Engelbrecht, cap. 9):**
- *Selección por torneo* de tamaño 3.
- *Cruza BLX-α* (α = 0.3): cada gen del hijo se toma de $U[\min-\alpha d,\ \max+\alpha d]$. El ángulo se "desenrolla" antes de cruzar porque es circular.
- *Mutación gaussiana* con probabilidad $p_m=0.25$ por gen. σ baja de σ₀ a 0.2σ₀ con las generaciones (de explorar a explotar), y el paso en x,y es proporcional al tamaño del trazo.
- *Elitismo:* el mejor individuo pasa intacto a la siguiente generación.""",
    "9": r"""## 9. Ciclo principal (de lo grueso a lo fino)
En cada **etapa** se corre un AG completo para encontrar la mejor pincelada nueva. Esa pincelada **solo se pinta si mejora** el fitness del lienzo; si no mejora, la etapa se rechaza. El largo de las pinceladas baja geométricamente con el avance:
$$L(t) = W\cdot \ell_{ini}\left(\frac{\ell_{fin}}{\ell_{ini}}\right)^{t^{\gamma}},\qquad t=\frac{\text{pinceladas}}{\text{total}}$$
Así trabaja un pintor: primero manchas grandes y al final los detalles. Se guarda una **captura** en 25, 50, 100, 200… pinceladas, junto con `pinceladas.json` para poder reanudar la corrida.""",
    "10": r"""## 10. Utilidades
- **SSIM** (similitud estructural), calculada sin librerías extra.
- **Timelapse** en GIF con las capturas.
- **Gráfica de convergencia** del MSE y del PSNR contra el número de pinceladas.""",
}

CELDAS_FINALES = [
    ("md", r"""## 11. Parámetros del experimento
Con los valores de abajo cada estilo tarda **1–2 minutos**. Para un resultado **muy bueno** usa `PINCELADAS = 20000` y `ANCHO = 400`, que toma ~15 min por estilo en una laptop. Las mismas corridas se pueden hacer desde la terminal con `pintor_evolutivo.py`."""),
    ("code", r'''PINCELADAS = 3000      # total de pinceladas por estilo (20000 = resultado muy bueno)
ANCHO = 300            # resolucion de trabajo del AG (400 = mas detalle, mas lento)
ESCALA_SALIDA = 3      # la imagen final mide ANCHO * ESCALA_SALIDA
SEMILLA = 0
CARPETA = "salida_notebook"

import matplotlib.pyplot as plt
from IPython.display import display

def miniatura(img, ancho=320):
    return img.resize((ancho, round(img.height * ancho / img.width)))'''),
    ("md", r"""## 12. Exploración: objetivo estilizado y campo de flujo
De izquierda a derecha: la foto, cómo la "ve" Van Gogh (objetivo estilizado), la coherencia del flujo (zonas claras = bordes con dirección definida) y el flujo dibujado como segmentos."""),
    ("code", r'''pintor_vg = Pintor(RUTA_IMAGEN, "vangogh", ANCHO, ESCALA_SALIDA, SEMILLA)
H, W = pintor_vg.objetivo.shape[:2]
fig, ax = plt.subplots(1, 4, figsize=(14, 5))
ax[0].imshow(pintor_vg.original); ax[0].set_title("Foto original")
ax[1].imshow(pintor_vg.objetivo.astype("uint8")); ax[1].set_title("Objetivo estilizado (Van Gogh)")
ax[2].imshow(pintor_vg.coherencia, cmap="gray"); ax[2].set_title("Coherencia del flujo")
ax[3].imshow(pintor_vg.objetivo.astype("uint8"), alpha=0.4); ax[3].set_title("Campo de flujo")
paso = max(6, W // 30)
for y in range(paso // 2, H, paso):
    for x in range(paso // 2, W, paso):
        a = pintor_vg.flujo[y, x]; d = 0.45 * paso
        ax[3].plot([x - d * np.cos(a), x + d * np.cos(a)], [y - d * np.sin(a), y + d * np.sin(a)], "k-", lw=0.8)
for a in ax: a.axis("off")
plt.tight_layout(); plt.show()'''),
    ("md", r"""## 13. Pinceladas aleatorias (idea original de Angie)
Antes de evolucionar, así se ven 400 pinceladas generadas por `Pincelada_Randomizer` con focos al azar. Esto equivale a la **población inicial** de cada etapa."""),
    ("code", r'''demo = ImagenEvolutiva(pintor_vg.objetivo, pintor_vg.estilo, escala_salida=1)
rng_demo = np.random.default_rng(1)
for i in range(400):
    L = largo_de_capa(i / 400, pintor_vg.estilo, W)
    foco = (rng_demo.uniform(0, W - 1), rng_demo.uniform(0, H - 1))
    genes = pintor_vg.randomizer.generate_Random_Pincelada(foco, L)
    if i == 0:
        genes_ejemplo = genes.copy()
    demo.add_Pincelada(Pincelada.from_Genes(genes, L, pintor_vg.estilo, H, W, semilla=i))
print("Ejemplo de pincelada (fenotipo):")
demo.lista_pinceladas[0].print()
print("Sus genes (genotipo):", {k: round(float(v), 3) for k, v in zip(NOMBRES_GENES, genes_ejemplo)})
display(miniatura(demo.generate_image(), 300))'''),
    ("md", r"""## 14. Una etapa del AG por dentro
Se corre **una** etapa y se grafica el mejor fitness de cada generación. La línea punteada es el fitness del lienzo **sin** la pincelada nueva: el AG tiene que quedar por debajo de ella para que la pincelada se acepte."""),
    ("code", r'''L0 = largo_de_capa(0, pintor_vg.estilo, W)
mejor, f_mejor = pintor_vg.ag.evolucionar_Etapa(L0)
plt.figure(figsize=(5, 3))
plt.plot(pintor_vg.ag.mejor_por_generacion, "o-", label="mejor de la generacion")
plt.axhline(pintor_vg.ag.fitness_Actual(), ls="--", c="gray", label="lienzo sin la pincelada")
plt.xlabel("generacion"); plt.ylabel("fitness"); plt.legend(); plt.grid(alpha=.3); plt.show()
for g in mejor:
    Pincelada.from_Genes(g, L0, pintor_vg.estilo, H, W).print()'''),
    ("md", r"""## 15. Pintar estilo **Van Gogh**
Se muestran las capturas guardadas durante la evolución (25, 50, 100, … pinceladas)."""),
    ("code", r'''import time
pintor_vg = Pintor(RUTA_IMAGEN, "vangogh", ANCHO, ESCALA_SALIDA, SEMILLA)   # empieza de cero
capturas_vg = []
t0 = time.time()
pintor_vg.pintar(PINCELADAS, os.path.join(CARPETA, "vangogh"),
                 al_capturar=lambda p, n: capturas_vg.append((n, miniatura(p.lienzo.generate_image(), 240))))
print(f"Tiempo: {time.time() - t0:.0f} s")
cols = 5; filas = (len(capturas_vg) + cols - 1) // cols
fig, ax = plt.subplots(filas, cols, figsize=(3 * cols, 4 * filas))
for a in ax.ravel(): a.axis("off")
for a, (n, im) in zip(ax.ravel(), capturas_vg):
    a.imshow(im); a.set_title(f"{n} pinceladas")
plt.tight_layout(); plt.show()'''),
    ("code", r'''import json
print(json.dumps(json.load(open(os.path.join(CARPETA, "vangogh", "metricas.json"))), indent=1))
display(miniatura(Image.open(os.path.join(CARPETA, "vangogh", "comparacion.jpg")), 700))
display(Image.open(os.path.join(CARPETA, "vangogh", "convergencia.png")))'''),
    ("md", r"""## 16. Pintar estilo **Monet**
Es el mismo algoritmo con otro diccionario de estilo: toques cortos y semitransparentes, un objetivo suavizado y sin término de flujo."""),
    ("code", r'''pintor_mo = Pintor(RUTA_IMAGEN, "monet", ANCHO, ESCALA_SALIDA, SEMILLA)
capturas_mo = []
t0 = time.time()
pintor_mo.pintar(PINCELADAS, os.path.join(CARPETA, "monet"),
                 al_capturar=lambda p, n: capturas_mo.append((n, miniatura(p.lienzo.generate_image(), 240))))
print(f"Tiempo: {time.time() - t0:.0f} s")
fig, ax = plt.subplots(filas, cols, figsize=(3 * cols, 4 * filas))
for a in ax.ravel(): a.axis("off")
for a, (n, im) in zip(ax.ravel(), capturas_mo):
    a.imshow(im); a.set_title(f"{n} pinceladas")
plt.tight_layout(); plt.show()
print(json.dumps(json.load(open(os.path.join(CARPETA, "monet", "metricas.json"))), indent=1))
display(miniatura(Image.open(os.path.join(CARPETA, "monet", "comparacion.jpg")), 700))'''),
    ("md", r"""## 17. (Opcional) ¿El AG le gana a la búsqueda aleatoria?
Se compara con la misma cantidad de evaluaciones de fitness: el AG (16 individuos × 13 evaluaciones) contra 208 pinceladas aleatorias guiadas por etapa de las que se elige la mejor. Esta es la forma correcta de defender que la **evolución** (selección, cruza y mutación) aporta algo más allá de la buena inicialización. Pon `EJECUTAR = True` para correrlo (~3 min)."""),
    ("code", r'''EJECUTAR = False
if EJECUTAR:
    curvas = {}
    for nombre, aleatoria in (("AG", False), ("Busqueda aleatoria", True)):
        p = Pintor(RUTA_IMAGEN, "libre", 300, 1, SEMILLA, busqueda_aleatoria=aleatoria)
        p.pintar(2000, None, verbose=False)
        curvas[nombre] = p.historial
        print(f"{nombre:20s} MSE final = {p.lienzo.mse():.5f}  evaluaciones = {p.ag.evaluaciones}")
    plt.figure(figsize=(5, 3))
    for nombre, h in curvas.items():
        plt.plot([x["pinceladas"] for x in h], [x["mse"] for x in h], label=nombre)
    plt.yscale("log"); plt.xlabel("pinceladas"); plt.ylabel("MSE"); plt.legend(); plt.grid(alpha=.3); plt.show()'''),
    ("md", r"""## 18. Conclusiones rápidas
- El AG por etapas reproduce la imagen con pinceladas visibles. El **estilo** sale de tres fuentes: la forma de las pinceladas, el objetivo estilizado y el término de flujo en el fitness.
- Con el mismo número de evaluaciones, el AG obtiene menor error que la búsqueda aleatoria guiada (ver `resultados/experimentos`).
- Más pinceladas y una resolución mayor mejoran la fidelidad, pero el tiempo crece casi linealmente con el número de pinceladas.
- Ver `DOCUMENTACION.md` en la raíz del repositorio para limitaciones, alcances y cómo defender el trabajo."""),
]


def secciones(texto):
    partes = re.split(r"^# %% ", texto, flags=re.M)
    for p in partes[1:]:
        titulo, _, cuerpo = p.partition("\n")
        yield titulo.strip(), cuerpo.strip("\n")


def construir():
    texto = open(FUENTE, encoding="utf-8").read()
    nb = nbf.v4.new_notebook()
    celdas = [nbf.v4.new_markdown_cell(INTRO), nbf.v4.new_code_cell(PREPARACION)]
    for titulo, cuerpo in secciones(texto):
        if titulo.startswith("[cli]"):
            continue
        num = titulo.split(".")[0]
        celdas.append(nbf.v4.new_markdown_cell(EXPLICACIONES[num]))
        celdas.append(nbf.v4.new_code_cell(f"# {titulo}\n" + cuerpo))
    for tipo, src in CELDAS_FINALES:
        celdas.append(nbf.v4.new_markdown_cell(src) if tipo == "md" else nbf.v4.new_code_cell(src))
    nb.cells = celdas
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata["language_info"] = {"name": "python"}
    nbf.write(nb, DESTINO)
    print("Notebook escrito:", DESTINO, f"({len(celdas)} celdas)")


if __name__ == "__main__":
    construir()
    if "--ejecutar" in sys.argv:
        subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute",
                        "--inplace", "--ExecutePreprocessor.timeout=-1", DESTINO], check=True)
        print("Notebook ejecutado y guardado con salidas.")
