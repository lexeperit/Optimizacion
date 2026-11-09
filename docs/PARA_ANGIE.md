# Para Angie: qué pasó con tu código

Lectura de ~5 minutos. El documento completo es `DOCUMENTACION.md`, en la raíz del repositorio.

## 1. Tu notebook corregido
Está en **`Angie_codigo/pincelada_y_randomizer_corregido.ipynb`**. Tu original, `pincelada y randomizer.ipynb` en la raíz, no se tocó. Cada cambio está marcado con `# CORREGIDO` y el notebook ya corre completo.

| Dónde | Problema | Corrección |
|---|---|---|
| `create_Chromosomes` (tu captura de pantalla) | El parámetro se llamaba `pincelada_randomizer`, pero adentro se usaba `randomizer`. Usaba la variable global `algoritmo_evol` en vez de `self`. Faltaba `img_evol.update_Hedge_Array()`. | Parámetro renombrado a `randomizer`, uso de `self`, la línea que faltaba y `j` en el ciclo interno |
| `generate_Random_Pincelada` | `size` usaba `(min_size, min_size)` | `(min_size, max_size)` |
| `random_Color` | `y` se sorteaba con `img_width` | `img_height` (con imágenes horizontales se salía de la imagen) |
| `random_Points` | Con ángulos mayores a 90°, `x_length` es negativo y la caja quedaba mal: había puntos fuera de la imagen | La caja se calcula con `max(0, ±x_length)` |
| `random_Start_End` | `% 359` | `% 360` |
| `generate_image` | No regresaba la imagen | `return image` |
| `mean_square_error` | Usaba `img_original` e `img_evol`, que no existen, y restaba el objeto en vez de su imagen | `img_original_RGB` y `np.array(img_evolutiva.image)` |
| `calculate_Fitness` | No reiniciaba `self.fitness` ni dibujaba la imagen antes de medir | Ahora hace las dos cosas |
| `hedge_lambda = 0` | Como el error solo se mide donde se pintó, conviene pintar **poco** | `0.2`, igual que en el código de Leo |
| `.show()` | Abre una ventana externa | `display()`, que se ve dentro de Jupyter |

> Tu notebook sigue siendo **búsqueda aleatoria**: crea 10 imágenes al azar y elige la mejor. Le faltaba la parte evolutiva, que es lo que agrega el código nuevo.

## 2. Tus clases son el esqueleto del código nuevo
El programa principal es **`pintor_evolutivo/pintor_evolutivo.py`** (y el notebook `Pintor_Evolutivo.ipynb`). Usa **tus cuatro clases con sus mismos nombres y métodos**:

| Tu clase | Qué conserva | Qué cambió y por qué |
|---|---|---|
| `Pincelada` | `points, size, width, angle, color, tipo ("line"/"arc"), start, end, print()` | Agrega `alpha` (transparencia) y `curvatura`. Se construye desde **genes** con `from_Genes`. Los arcos se dibujan como polilínea, pero `start`/`end` siguen calculándose como en `ImageDraw.arc` |
| `Pincelada_Randomizer` | `generate_Random_Pincelada, random_Color, random_Tipo, random_Value_In_Range, clamp` | Ahora es **guiado**: el color se toma *en la posición de la pincelada* y no de un punto cualquiera, y la posición se elige donde el lienzo tiene más error. Regresa genes en [0,1] para que el AG pueda cruzarlos y mutarlos |
| `ImagenEvolutiva` | `lista_pinceladas, hedge_array, add_Pincelada, update_Hedge_Array, generate_image` | Ahora es **el lienzo** que se va pintando, no un individuo. Guarda un mapa de error por píxel para evaluar rápido |
| `AlgoritmoEvolutivo` | `create_Chromosomes, calculate_Fitness, show_Best_Option, list_chromosomes, fitness, number_chromosomes, number_generaciones` | Agrega la evolución: `torneo`, `cruza_BLX`, `mutacion_Gaussiana`, elitismo y `evolucionar_Etapa` |

## 3. El cambio de diseño más importante
En tu versión, **un cromosoma era una imagen completa de 100 pinceladas** (≈ 100 × 7 = 700 variables). Optimizar eso directamente es muy difícil, porque cambiar una pincelada apenas mueve el fitness de toda la imagen.

En la versión nueva, **el lienzo funciona como memoria** y el AG evoluciona **una pincelada a la vez** (10 genes). La pincelada se coloca *encima* de lo ya pintado y solo se acepta si reduce el error. Al repetir esto miles de veces se obtiene la pintura. Es como pinta una persona: capa por capa, de lo grueso a lo fino.

## 4. Para la presentación, lo que te toca explicar
- Qué es el fenotipo (`Pincelada`) frente al genotipo (10 números en [0,1]), y cómo `from_Genes` traduce uno al otro.
- Por qué existen `line` y `arc`: los arcos permiten los remolinos de Van Gogh, y en Monet casi no se usan (`prob_arco` 0.15).
- Para qué sirve el `hedge_array`: medir la cobertura (qué porcentaje del lienzo ya se pintó). En el código nuevo el error se mide en **toda** la imagen, así que el término de cobertura es opcional (`--lambda_hedge`).

## 5. Cómo probarlo
```bash
cd pintor_evolutivo
python pintor_evolutivo.py ../imagenes/torii.jpg --estilo monet --pinceladas 3000
```
O abre `pintor_evolutivo/Pintor_Evolutivo.ipynb` y ejecuta *Run All*. La sección 13 muestra pinceladas aleatorias, como tu demo original.
