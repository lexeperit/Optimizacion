# Pintor Evolutivo: documentación del proyecto

Algoritmo genético que replica una imagen con pinceladas al estilo de **Van Gogh** o de **Monet**.
Materia: Optimización. Base teórica: Engelbrecht, *Computational Intelligence*, 2.ª ed., caps. 8 y 9.

---

## Índice
1. [Qué hay en el repositorio](#1-qué-hay-en-el-repositorio)
2. [Punto de partida: el código de cada integrante](#2-punto-de-partida-el-código-de-cada-integrante)
3. [Cómo se arreglaron los códigos por separado](#3-cómo-se-arreglaron-los-códigos-por-separado)
4. [Cómo se combinaron](#4-cómo-se-combinaron)
5. [Formulación del problema de optimización](#5-formulación-del-problema-de-optimización)
6. [El algoritmo genético paso a paso](#6-el-algoritmo-genético-paso-a-paso)
7. [Estilos: Van Gogh y Monet](#7-estilos-van-gogh-y-monet)
8. [Por qué funciona así (decisiones de diseño)](#8-por-qué-funciona-así-decisiones-de-diseño)
9. [Resultados](#9-resultados)
10. [Tiempos de ejecución](#10-tiempos-de-ejecución)
11. [Alcances](#11-alcances)
12. [Limitaciones](#12-limitaciones)
13. [Qué se omitió y qué debería considerarse](#13-qué-se-omitió-y-qué-debería-considerarse)
14. [Cómo defenderlo (preguntas probables)](#14-cómo-defenderlo-preguntas-probables)
15. [Cómo usar el código (local y notebook)](#15-cómo-usar-el-código-local-y-notebook)
16. [Cómo generar el reporte en Overleaf](#16-cómo-generar-el-reporte-en-overleaf)

---

## 1. Qué hay en el repositorio

```
Optimizacion/
├── DOCUMENTACION.md                 ← este documento
├── docs/PARA_ANGIE.md, PARA_LEO.md  ← resúmenes personales (5 min cada uno)
├── imagenes/torii.jpg               ← imagen de entrada (arcos japoneses)
├── pintor_evolutivo/                ← ★ CÓDIGO PRINCIPAL (combinado)
│   ├── pintor_evolutivo.py          ← algoritmo completo + línea de comandos
│   ├── Pintor_Evolutivo.ipynb       ← mismo algoritmo, por partes (Jupyter / Colab)
│   ├── construir_notebook.py        ← genera el notebook a partir del .py
│   └── experimentos.py              ← experimentos del reporte (AG vs aleatorio, λ, K)
├── resultados/
│   ├── torii_vangogh/               ← capturas, resultado, métricas (20,000 pinceladas)
│   ├── torii_monet/                 ← ídem
│   └── experimentos/                ← E1, E1b, E2, E3
├── reporte/                         ← proyecto LaTeX para Overleaf (+ reporte_overleaf.zip)
├── Angie_codigo/
│   ├── pincelada_y_randomizer_corregido.ipynb  ← notebook de Angie corregido
│   └── vanGogh.ipynb, vanGogh2.jpeg            ← versión anterior de Angie (sin cambios)
├── Leo_codigo/
│   ├── vanGogh_corregido.py         ← vanGogh.py de Leo corregido
│   ├── ea_vangogh.py, GUIA.md       ← primera versión del AG (antecedente del código principal)
│   └── vanGogh.py                   ← original (sin cambios)
└── pincelada y randomizer.ipynb     ← notebook original de Angie (sin cambios)
```

Los archivos **originales no se modificaron**. Las correcciones están en copias con el sufijo `_corregido`.

---

## 2. Punto de partida: el código de cada integrante

| Integrante | Archivo | Qué aportaba | Qué le faltaba |
|---|---|---|---|
| **Angie** | `pincelada y randomizer.ipynb` | Diseño orientado a objetos: `Pincelada` (con `points, size, width, angle, color, tipo, start, end`), `Pincelada_Randomizer`, `ImagenEvolutiva` (con `lista_pinceladas` y `hedge_array`) y `AlgoritmoEvolutivo`. Pinceladas **`line` y `arc`**. | Errores que impedían correrlo (sección 3). **No había evolución**: crea imágenes al azar y elige la mejor. |
| **Leo** | `vanGogh.py` | Fitness = MSE en los píxeles pintados + λ·(1 − cobertura), con `hedge_array`. Color tomado de la imagen. | **Búsqueda aleatoria**, sin operadores genéticos. Algunos errores (sección 3). |
| **Leo** | `ea_vangogh.py` | **AG completo**: genes reales en [0,1], torneo, BLX-α, mutación gaussiana con σ decreciente, elitismo, etapas de lo grueso a lo fino y campo de flujo. | Pinceladas solo rectas (sin arcos), evaluación lenta (todo el lienzo), K=5 pinceladas por cromosoma, penalización de flujo con escala arbitraria (`1e-3`) y siempre pintaba al mejor aunque empeorara. |

---

## 3. Cómo se arreglaron los códigos por separado

### 3.1 Angie: `Angie_codigo/pincelada_y_randomizer_corregido.ipynb`
Ya corre de principio a fin (se ejecutó para verificarlo y las salidas quedaron guardadas). Cada cambio está marcado con `# CORREGIDO`.

| Dónde | Error | Corrección |
|---|---|---|
| `create_Chromosomes` (**la captura de pantalla**) | El parámetro `pincelada_randomizer` no se usaba y adentro se usaba la global `randomizer`. Usaba la global `algoritmo_evol` en vez de `self`. Reutilizaba `i` en el ciclo interno. **Faltaba `img_evol.update_Hedge_Array()`**. | Parámetro renombrado a `randomizer`, uso de `self`, `j` en el ciclo interno y la línea agregada |
| `generate_Random_Pincelada` | `random_Value_In_Range(self.min_size, self.min_size)` | `(self.min_size, self.max_size)` |
| `random_Color` | `y = randint(0, img_width-1)` | `img_height-1` |
| `random_Points` | Con ángulo > 90°, `x_length < 0` y la caja de posiciones válidas sale mal: hay puntos fuera de la imagen | La caja usa `max(0, -x_length)` y `max(0, x_length)` |
| `random_Start_End` | `% 359` | `% 360` |
| `generate_image` | No regresaba la imagen, así que `show_Best_Option` fallaba | `return image` |
| `mean_square_error` | Usaba `img_original` e `img_evol`, que no existen, y hacía `img_evolutiva.astype`, que es un objeto y no un arreglo | `img_original_RGB` y `np.array(img_evolutiva.image)` |
| `calculate_Fitness` | No reiniciaba `self.fitness` y medía imágenes sin dibujar | `self.fitness = []` y `generate_image()` antes de medir |
| `hedge_lambda = 0` | Como el MSE solo se mide en los píxeles pintados, sin el término de cobertura conviene pintar poco | `0.2`, como en el código de Leo |
| Celda del `hedge_array` | Usaba `img_evol`, que no existe fuera de la clase | Usa `algoritmo_evol.list_chromosomes[0]` |
| `.show()` | Abre un visor externo | `display()` dentro del notebook |

### 3.2 Leo: `Leo_codigo/vanGogh_corregido.py`
| Error | Corrección |
|---|---|
| `generate_img` recorre `range(len(list_pincelada))`, una variable **global**, y no el cromosoma recibido | `range(len(cromosome))` |
| `roger.jpg` no existe en el repositorio | La ruta se recibe como argumento (por defecto `../Angie_codigo/vanGogh2.jpeg`) |
| El mejor individuo se dibujaba sobre la **última imagen evaluada** (lienzo sucio) | Lienzo nuevo, más `mejor_individuo.png` |

Uso: `python vanGogh_corregido.py [ruta_imagen]`. Sigue siendo búsqueda aleatoria a propósito: se corrigió, no se reescribió.

---

## 4. Cómo se combinaron

El código principal (`pintor_evolutivo/pintor_evolutivo.py`) usa **las clases de Angie como esqueleto** y **los operadores de Leo como motor**:

| Concepto | Origen | Dónde está ahora (sección del código) |
|---|---|---|
| Clase `Pincelada` (`points, size, width, angle, color, tipo, start, end, print`) | Angie | §4. Se agregan `alpha`, `curvatura` y `from_Genes` (genotipo → fenotipo) |
| Pinceladas `line` / `arc` | Angie | §4. El gen `curvatura` decide el tipo; `start`/`end` siguen el formato de `ImageDraw.arc` |
| `Pincelada_Randomizer` (`generate_Random_Pincelada, random_Color, random_Tipo, random_Value_In_Range, clamp`) | Angie | §7. Ahora **guiado**: posición cerca de un foco de error, color *en esa posición* y ángulo del flujo |
| `ImagenEvolutiva` (`lista_pinceladas, hedge_array, add_Pincelada, update_Hedge_Array, generate_image`) | Angie (y `hedge_array` de Leo) | §6. Ahora es **el lienzo** acumulado, con un mapa de error para evaluar rápido |
| `AlgoritmoEvolutivo` (`create_Chromosomes, calculate_Fitness, show_Best_Option, list_chromosomes, fitness`) | Angie (nombres) | §8 |
| Genes reales normalizados en [0,1] | Leo | §1 y §4 (10 genes) |
| Torneo, BLX-α, mutación gaussiana con σ decreciente, elitismo | Leo | §8: `torneo`, `cruza_BLX`, `mutacion_Gaussiana`, `evolucionar_Etapa` |
| Etapas de lo grueso a lo fino | Leo | §9: `largo_de_capa` |
| Campo de flujo para el estilo Van Gogh | Leo | §3: `campo_de_flujo`, mejorado con el tensor de estructura y la coherencia |
| Fitness MSE + λ·(1 − cobertura) | Leo y Angie | §8: `calculate_Fitness`. El término de cobertura sigue disponible (`--lambda_hedge`) |

**Cambio de diseño central:** en el código original, *un cromosoma = una imagen completa de 100 pinceladas*. En el nuevo, el **lienzo es la memoria** y *un cromosoma = la siguiente pincelada* (10 genes). La sección 8 explica por qué.

---

## 5. Formulación del problema de optimización

- **Variables de decisión:** n pinceladas, cada una con 10 genes en [0,1]:
  `x, y` (centro), `ángulo` (0–π), `largo`, `grosor`, `alpha` (opacidad), `r, g, b` (color), `curvatura` (0.5 = recta).
- **Espacio de búsqueda:** [0,1]^(10n). Con n = 20,000 son **200,000 variables continuas**. Es no diferenciable (los trazos se rasterizan), multimodal y muy alto dimensional.
- **Función objetivo global:** MSE normalizado entre el lienzo pintado y la imagen objetivo.
- **Restricciones:** de caja ([0,1]), que se mantienen *reparando* (recorte a [0,1] y módulo 1 para el ángulo).
- **Descomposición:** se resuelve como **secuencia de subproblemas de 10 variables**. En la etapa t se busca la pincelada s que minimiza

```
f(s) = MSE(lienzo_t + s, objetivo)
     + λ_flujo · área(s) · w(x,y) · sin²(ángulo − flujo(x,y)) / N
     + λ_hedge · (1 − cobertura)
```

  - `MSE` = Σ‖L − O‖² / (N · 3 · 255²), en [0,1].
  - `w = 0.25 + 0.75·coherencia`: la penalización pesa más donde la dirección del flujo es clara.
  - Por defecto `λ_hedge = 0`, porque el MSE se mide en **toda** la imagen y eso ya castiga las zonas sin pintar.

---

## 6. El algoritmo genético paso a paso

```
1. Estilizar el objetivo; calcular flujo y coherencia; lienzo ← color promedio.
2. Mientras pinceladas < total:
   a. Escala de la etapa: L = W·ℓ_ini·(ℓ_fin/ℓ_ini)^(t^γ),  t = pinceladas/total
   b. Foco ~ error local del lienzo (suavizado)
   c. Población inicial: 16 pinceladas cerca del foco (color de la imagen, ángulo del flujo)
   d. 12 generaciones:  elitismo + torneo(3) + BLX-α(0.3, pc=0.8) + mutación gaussiana(pm=0.25, σ↓)
   e. Si el mejor mejora el fitness del lienzo → se pinta; si no → etapa rechazada
3. Guardar capturas en 25, 50, 100, …, total pinceladas.
```

| Parámetro | Valor | Dónde se cambia |
|---|---|---|
| Población | 16 | `--poblacion` |
| Generaciones por etapa | 12 | `--generaciones` |
| Pinceladas por cromosoma (K) | 1 | `--K` |
| Torneo | 3 | `AlgoritmoEvolutivo(tam_torneo=)` |
| BLX-α / pc | 0.3 / 0.8 | `alpha_blx`, `pc` |
| Mutación pm / σ₀ | 0.25 / 0.12 (σ baja hasta 0.2σ₀) | `pm`, `sigma0` |
| Evaluaciones por etapa | 16 × 13 = 208 | — |

---

## 7. Estilos: Van Gogh y Monet

| | Van Gogh | Monet |
|---|---|---|
| Objetivo estilizado | saturación ×1.45, contraste ×1.12 | saturación ×1.2, contraste ×0.92, brillo ×1.05, **suavizado** |
| Pinceladas | **largas**, razón largo/grosor 2.6–4.5 | **cortas y anchas**, 1.3–2.2 |
| Opacidad | 0.80–1.00 (empaste) | 0.45–0.85 (veladuras) |
| Curvas | hasta 1.4 rad, 50% arcos al inicio | hasta 0.5 rad, 15% arcos |
| Ángulo inicial | 100% según el flujo | 25% según el flujo, el resto al azar |
| λ_flujo (fitness) | 0.04 | 0 |
| Variación de color inicial | 0.04 | 0.09 (color quebrado) |
| Textura de cerdas | 0.45 (7 cerdas) | 0.30 (5 cerdas) |

Agregar un pintor nuevo consiste en agregar un diccionario a `ESTILOS`. El algoritmo no cambia. El estilo `libre` (sin estilo) se usa como línea base en los experimentos.

---

## 8. Por qué funciona así (decisiones de diseño)

1. **Descomposición secuencial (lienzo = memoria).** Optimizar 200,000 variables a la vez con un AG es inviable: cada pincelada aporta una fracción ínfima al fitness global y la búsqueda se diluye. Al resolver una pincelada a la vez sobre lo ya pintado, cada subproblema es pequeño (10 variables) y su efecto en el fitness es claro. Es lo que hace un pintor: capa por capa.
2. **K = 1.** Con K = 3, una pincelada buena queda "amarrada" a dos malas en el mismo individuo, y cada pincelada recibe un tercio de las evaluaciones. El experimento E3 muestra 64% más error con K = 3.
3. **Evaluación incremental.** Medir el MSE de toda la imagen en cada evaluación es lento. El lienzo guarda `err_map` y solo se recalcula la caja envolvente del trazo: ΔE = E_nuevo(caja) − E_viejo(caja). El resultado es **exacto** y cientos de veces más rápido, lo que permite ~10⁷ evaluaciones en minutos.
4. **Inicialización heurística + focos por error.** Igual que la idea de Angie de tomar el color de la imagen, pero en la posición correcta. Así el AG parte de soluciones razonables y gasta su presupuesto en refinar.
5. **De lo grueso a lo fino.** Las pinceladas grandes fijan rápido las masas de color y las finas ponen el detalle.
6. **Aceptar solo si mejora.** Garantiza que el MSE nunca sube (convergencia monótona).
7. **Genes normalizados + ángulo circular.** Todos los genes viven en [0,1], así que los mismos operadores sirven para todos. Para el ángulo, 0.98 y 0.02 son vecinos: BLX los "desenrolla" antes de mezclarlos.
8. **Mutación con escala por gen.** Mover la posición "un píxel" no significa lo mismo con trazos de 60 px que de 5 px. Por eso el paso en x,y es proporcional al tamaño de la etapa.
9. **Salida vectorial en alta resolución.** El AG trabaja a 400 px y las pinceladas guardadas se vuelven a dibujar a 1200 px con antialiasing y textura de cerdas.

---

## 9. Resultados

### 9.1 Imagen de los arcos japoneses (20,000 pinceladas, trabajo 400×533 → salida 1200×1599)

| Estilo | MSE | PSNR | SSIM | Etapas (rechazadas) | Evaluaciones | Tiempo* |
|---|---|---|---|---|---|---|
| Van Gogh | 0.00418 | 23.79 dB | 0.732 | 21,749 (1,749) | 4.52 M | 9.9 min |
| Monet | 0.00074 | 31.30 dB | 0.887 | 25,656 (5,656) | 5.34 M | 11.1 min |

\*En la nube, con 4 procesos simultáneos en 4 núcleos. Las métricas se miden contra el **objetivo estilizado** de cada estilo. Monet obtiene mejores cifras porque su objetivo está suavizado.

Desalineación media de los trazos respecto al flujo: **0.0065** en Van Gogh contra **0.141** en Monet, donde la orientación es libre. El término de flujo sí produce el rasgo de estilo buscado.

**Capturas:** `resultados/torii_vangogh/progreso_00025.jpg … progreso_20000.jpg` (y lo mismo para Monet). También están `timelapse.gif`, `comparacion.jpg` (foto | pintura), `convergencia.png`, `metricas.json`, `historial.csv` y `pinceladas.json` (todas las pinceladas, para reanudar o volver a dibujar).

### 9.2 Experimentos (300×400 px, 3000 pinceladas; `resultados/experimentos/resumen.csv`)

| Experimento | Resultado | Conclusión |
|---|---|---|
| **E1** AG vs búsqueda aleatoria guiada, **mismas evaluaciones** (3 semillas) | AG **0.00462 ± 0.00002** vs aleatoria 0.00517 ± 0.00002 | La evolución reduce el error **~11%**, con una diferencia ~30× mayor que la desviación estándar |
| **E1b** Búsqueda aleatoria con ~30% más evaluaciones (≈ mismo tiempo que el AG) | Aleatoria 0.00496 (73 s) vs AG 0.00462 (74 s) | A igual tiempo el AG sigue teniendo ~7% menos error |
| **E2** Van Gogh con λ_flujo = 0 / 0.04 / 0.15 | Desalineación 0.064 / 0.017 / 0.004; MSE 0.00635 / 0.00645 / 0.00662 | El término de flujo **alinea** los trazos a cambio de +1.6% / +4.3% de error: compromiso explícito entre estilo y fidelidad |
| **E3** K = 3 vs K = 1 | MSE 0.00760 vs 0.00462 | K = 1 es mucho mejor |

Durante el ajuste preliminar, con pocas evaluaciones por etapa (8 individuos × 9 evaluaciones) el AG y la búsqueda aleatoria quedaron **empatados**. La ventaja del AG aparece cuando hay suficientes generaciones para que la cruza y la mutación exploten las buenas soluciones. Conviene mencionarlo en la defensa: es un resultado honesto y tiene explicación.

---

## 10. Tiempos de ejecución

Medidos en este entorno (CPU en la nube, 1 núcleo por corrida):

| Corrida | Tiempo |
|---|---|
| 600 pinceladas, 300 px | ~8 s |
| 3000 pinceladas, 300 px (experimentos y notebook) | ~75 s por estilo |
| 6000 pinceladas, 300 px | ~1.5–2 min |
| 20,000 pinceladas, 400 px | 9.9 min (Van Gogh), 11.1 min (Monet), con 4 corridas simultáneas |

- El tiempo crece **casi linealmente** con las pinceladas: ~20–30 ms por pincelada (208 evaluaciones cada una).
- En una laptop (por ejemplo la ASUS TUF A16 de Leo, que midió ~1.45 veces más lento) cuenta con ~15 min por estilo para 20,000 pinceladas. Se pueden correr **los dos estilos a la vez** en dos terminales, porque cada uno usa un solo núcleo.
- La memoria es baja (< 300 MB).

---

## 11. Alcances
- Funciona con **cualquier imagen** (jpg/png) y cualquier relación de aspecto.
- **Dos estilos** listos (más uno sin estilo). Un estilo nuevo es un diccionario de parámetros.
- Salida en **alta resolución** (escalable, porque las pinceladas son vectoriales).
- **Reanudable** (`--continuar`): ideal para dejarlo corriendo en la laptop.
- Mismo código en script y notebook (Jupyter y Colab).
- Experimentos reproducibles (semillas fijas).

## 12. Limitaciones
1. **Voraz (greedy):** una pincelada ya pintada no se vuelve a optimizar. El óptimo es local respecto al problema global.
2. **El estilo es por reglas**, no se aprende de pinturas reales. No hay una métrica objetiva de "qué tan Van Gogh" es el resultado, así que esa evaluación es cualitativa.
3. **El MSE en RGB no es perceptual.** El SSIM se reporta, pero no se optimiza.
4. **Costo:** ~10⁷ evaluaciones para un resultado de alta calidad. Python + Pillow limita la velocidad (unos 1,000 trazos por segundo).
5. **Ajuste con una sola imagen:** P, G y σ₀ se ajustaron con los arcos japoneses.
6. **La textura de cerdas no se evalúa** en el fitness (solo es visual). Su efecto en el error es pequeño y de media cero.
7. La "variación de color" de Monet (color quebrado) solo se aplica al inicializar. El AG tiende a corregirla porque el MSE premia el color exacto.
8. `--continuar` debe usarse con el mismo `--pinceladas`: si cambias el total, la escala de las pinceladas se recalcula y vuelven a salir trazos grandes encima de los finos.

## 13. Qué se omitió y qué debería considerarse
- **Comparar con otros algoritmos del libro:** Estrategias Evolutivas (1+λ) o (μ,λ) con σ autoadaptativo (cap. 12), Programación Evolutiva (cap. 11) o PSO (cap. 16). El fitness ya está listo para eso.
- **Re-optimizar pinceladas viejas** (por ejemplo, cada 1000 etapas, mutar las ya colocadas): quita el carácter voraz.
- **Fitness perceptual:** SSIM, espacio Lab o pérdida de estilo con una pintura de referencia (transferencia de estilo).
- **Paleta restringida:** limitar los genes de color a la paleta real de Van Gogh o Monet.
- **Paralelizar** la evaluación de la población (multiprocessing o numba).
- **Ajuste de hiperparámetros** con más imágenes y más semillas, y pruebas estadísticas (Wilcoxon) en E1.
- **Evaluación humana del estilo** (encuesta) para compensar la falta de una métrica objetiva.
- El término `λ_hedge` (cobertura) quedó en 0. Se puede reportar un experimento que muestre que es redundante cuando el MSE se mide en toda la imagen.

## 14. Cómo defenderlo (preguntas probables)

**¿Por qué un AG y no descenso de gradiente?** La función es no diferenciable (rasterizado), discontinua en la geometría y multimodal. El AG solo necesita evaluar la función.

**¿Por qué no un cromosoma con todas las pinceladas?** Con 200,000 variables cada pincelada influye muy poco en el fitness y la búsqueda se diluye. La descomposición secuencial convierte el problema en miles de subproblemas de 10 variables bien condicionados. Es una estrategia voraz: se pierde la optimalidad global a cambio de que el problema sea tratable.

**¿El AG realmente aporta o todo lo hace la inicialización?** El experimento E1 responde: con el mismo número de evaluaciones, el AG tiene ~11% menos error, con diferencias ~30× mayores que la desviación entre semillas. A igual tiempo (E1b) también gana.

**¿Dónde está el "estilo" en la optimización?** En tres lugares: (1) el espacio de búsqueda (forma, opacidad y curvatura permitidas), (2) el objetivo estilizado y (3) el término λ_flujo de la función de aptitud. E2 muestra que λ_flujo controla el compromiso entre estilo y fidelidad.

**¿Por qué BLX-α?** Es el operador de cruza estándar para codificación real (Eshelman y Schaffer, 1993; Engelbrecht cap. 9). Con α > 0 puede explorar fuera del segmento entre los padres.

**¿Por qué σ decreciente?** Al inicio se explora y al final se explota alrededor del mejor (Engelbrecht cap. 9, mutación gaussiana).

**¿Por qué elitismo y aceptar solo si mejora?** El elitismo asegura que la mejor solución de la etapa no se pierda. La regla de aceptación asegura que el MSE global sea monótonamente no creciente.

**¿Cómo se eligieron los parámetros?** Con un ajuste preliminar (población 8–16, generaciones 8–20, σ₀ 0.05–0.25, K 1–3). Los resultados fueron poco sensibles a σ₀ y muy sensibles a K y a las evaluaciones por etapa.

**¿Qué pasa con otra imagen?** Funciona igual. Solo cambia la ruta. `Angie_codigo/vanGogh2.jpeg` también sirve.

## 15. Cómo usar el código (local y notebook)

### 15.1 Instalación (una sola vez)
Windows (PowerShell), con el entorno virtual que ya usan:
```powershell
& "$env:USERPROFILE\.venvs\optimizacion\Scripts\Activate.ps1"
cd <ruta>\Optimizacion
python -m pip install -r requirements.txt
```
Mac/Linux:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 15.2 Corrida rápida (1–2 min)
```bash
cd pintor_evolutivo
python pintor_evolutivo.py ../imagenes/torii.jpg --estilo vangogh --pinceladas 3000
```
El resultado queda en `pintor_evolutivo/salida_local/vangogh/` (no se sube a git).

### 15.3 Resultado "muy bueno" (dejarlo corriendo en la laptop)
Abre **dos terminales**, una por estilo:
```bash
python pintor_evolutivo.py ../imagenes/torii.jpg --estilo vangogh --pinceladas 20000 --ancho 400 --escala_salida 3 --salida salida_local/vangogh_20k
```
```bash
python pintor_evolutivo.py ../imagenes/torii.jpg --estilo monet --pinceladas 20000 --ancho 400 --escala_salida 3 --salida salida_local/monet_20k
```
- Tiempo esperado: **~15 min por estilo** en una laptop (aquí tardó 10–11 min; la laptop de Leo midió ~1.45 veces más lento que este entorno con `ea_vangogh.py`).
- Cada captura (`progreso_XXXXX.jpg`) aparece en la carpeta mientras corre, así que puedes abrirlas para ver el avance.
- Si se interrumpe (cerraste la laptop, Ctrl+C), **reanuda** con el mismo comando más `--continuar`.
- Para todavía más calidad: `--pinceladas 40000 --ancho 500`, que tarda unas 2–3 veces más.
- Para que Windows no suspenda la laptop: *Configuración → Sistema → Energía → Suspender: Nunca* (con el cargador conectado).

### 15.4 Todas las opciones
| Opción | Por defecto | Qué hace |
|---|---|---|
| `--estilo` | vangogh | `vangogh`, `monet` o `libre` |
| `--pinceladas` | 6000 | Total de pinceladas |
| `--ancho` | 300 | Resolución de trabajo del AG |
| `--escala_salida` | 3 | La salida mide `ancho × escala` |
| `--poblacion` / `--generaciones` / `--K` | 16 / 12 / 1 | Parámetros del AG |
| `--lambda_flujo` | el del estilo | Peso del término de flujo |
| `--lambda_hedge` | 0 | Peso del término de cobertura (idea original) |
| `--busqueda_aleatoria` | — | Línea base sin evolución (mismas evaluaciones) |
| `--semilla` | 0 | Reproducibilidad |
| `--salida` / `--continuar` | `salida_local/<estilo>` | Carpeta de salida y reanudación |

### 15.5 Experimentos del reporte
```bash
python experimentos.py ../imagenes/torii.jpg --procesos 2
```
Tarda ~10 min con 2 procesos y escribe en `resultados/experimentos/`.

### 15.6 Notebook (Jupyter o Google Colab)
- **Jupyter local:** `pip install notebook` y luego `jupyter notebook pintor_evolutivo/Pintor_Evolutivo.ipynb`. Ejecuta *Run All*. Con los parámetros por defecto (3000 pinceladas) cada estilo tarda 1–2 min.
- **Colab:** *Archivo → Subir notebook*, elige `Pintor_Evolutivo.ipynb` y ejecuta todo. La primera celda pide subir la imagen (`torii.jpg`).
- Para un resultado muy bueno, cambia en la sección 11 `PINCELADAS = 20000` y `ANCHO = 400`. En Colab la sesión gratuita puede desconectarse en corridas largas; para esas, mejor el script local.
- Si modificas `pintor_evolutivo.py`, regenera el notebook con `python construir_notebook.py` para que ambos sigan iguales. Con `--ejecutar` lo corre y guarda las salidas.

## 16. Cómo generar el reporte en Overleaf
1. En Overleaf: *New Project → Upload Project* y sube **`reporte/reporte_overleaf.zip`**.
2. Compilador: pdfLaTeX (el predeterminado). Compila `main.tex`.
3. Llena los nombres en `\author{...}` y la institución.
4. Si vuelves a correr los experimentos, regenera figuras y cifras con `python reporte/generar_figuras.py`. Las cifras del texto vienen de `numeros.tex`, así que no hay que copiarlas a mano.
