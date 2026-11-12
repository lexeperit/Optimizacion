# Informe: códigos de Angie y Leo

Este informe explica qué hace cada código, dónde fallaba, qué se corrigió en esta rama (`claude/codigos-angie-leo`) y qué les falta para ser un algoritmo evolutivo completo.

Archivos que se analizan:

| Integrante | Archivo | Estado en esta rama |
|---|---|---|
| Leo | `Leo_codigo/vanGogh.py` | Corregido, corre |
| Angie | `pincelada y randomizer.ipynb` (raíz) | Corregido, corre |
| Angie | `Angie_codigo/vanGogh.ipynb` | Sin cambios: es el borrador anterior, reemplazado por el notebook de la raíz |

Las correcciones se marcaron con `# CORREGIDO` para que se puedan encontrar fácilmente.

---

## 1. Idea general que comparten los dos códigos

Los dos siguen el mismo planteamiento:

- **Gen** = una pincelada (posición, ángulo, tamaño, grosor y color).
- **Individuo (cromosoma)** = una imagen formada por 100 pinceladas.
- **Población** = 10 imágenes.
- **Fitness** = qué tanto se parece la imagen pintada a la original. Se busca el valor **más bajo**:

```
fitness = MSE_en_pixeles_pintados / 65025  +  λ · (1 − porcentaje_cubierto)
```

  - `MSE_en_pixeles_pintados`: error cuadrático medio, calculado **solo** en los píxeles donde hay pincelada. `65025 = 255²` lo normaliza a [0, 1].
  - `porcentaje_cubierto`: fracción de la imagen tapada por pinceladas. Se lleva en el **`hedge_array`**, una matriz de 0 y 1 del tamaño de la imagen.
  - `λ` (`hedge_lambda`): peso del término de cobertura. Sin él, al algoritmo le convendría pintar muy poco, porque solo se mide el error donde pintó.

- **Color de la pincelada:** se toma de un píxel de la imagen original.

Ninguno de los dos tiene todavía la parte **evolutiva**: crean la población al azar, calculan el fitness y eligen la mejor. Eso es **búsqueda aleatoria**, no un algoritmo evolutivo (ver la sección 5).

---

## 2. Código de Leo: `Leo_codigo/vanGogh.py`

### 2.1 Qué hace, parte por parte

| Parte | Qué hace |
|---|---|
| Constantes | `pincelada_size = 30` (largo), `pincelada_thickness = 10` (grosor), `number_imagenes = 10` (población), `number_pincelada = 100` (pinceladas por imagen), `hedge_lambda = 0.2` |
| `Pincelada` (namedtuple) | Guarda `position_x, position_y, angule, size, thickness, color` |
| `limit_values(size, angule, random_value, shape, "cos"/"sin")` | Calcula la coordenada final de la línea: `inicio + size·cos(ángulo)` en x, o `inicio + size·sin(ángulo)` en y. Si se sale de la imagen, la recorta al borde |
| `generate_pincelada(img_array)` | Crea una pincelada al azar: punto inicial aleatorio, ángulo aleatorio de 0 a 359° (pasado a radianes) y color del píxel original **en ese punto**. El tamaño y el grosor son fijos |
| `draw_pincelada(...)` | Dibuja la línea en la imagen. Si recibe un `hedge_array` no vacío, dibuja la misma línea en blanco en una imagen temporal y marca esos píxeles como cubiertos |
| `pincel_coverage(hedge_array, array_tmp)` | Pone 1 en el `hedge_array` donde la imagen temporal es blanca |
| `generate_img(cromosome, ...)` | Dibuja todas las pinceladas de un individuo |
| `oo_mse(original, generada, hedge_array)` | Calcula el fitness con la fórmula de la sección 1. Si no hay nada pintado, el error es el máximo (65025) |
| Programa principal | Abre la imagen, crea 10 individuos de 100 pinceladas, calcula el fitness de cada uno, elige el de menor fitness y lo muestra |

### 2.2 Dónde fallaba (corregido)

| # | Problema | Por qué falla | Corrección |
|---|---|---|---|
| 1 | `Image.open("roger.jpg")` | Esa imagen no está en el repositorio: el programa termina con `FileNotFoundError` | Se usa `../Angie_codigo/vanGogh2.jpeg` |
| 2 | `generate_img` recorre `range(len(list_pincelada))` | `list_pincelada` es una variable **global** que existe por casualidad, porque fue la última lista creada en el ciclo principal. Si los individuos tuvieran distinto número de pinceladas, fallaría | `range(len(cromosome))` |
| 3 | El mejor se dibuja sobre `img_evol` | `img_evol` es la **última** imagen evaluada, que ya tiene pinceladas. El mejor individuo se dibujaba encima de otro y la imagen mostrada era una mezcla | Se crea un lienzo nuevo antes de dibujar al mejor |

### 2.3 Observaciones que no impiden correr (no se cambiaron)
- La variable `cromosome` en realidad es la **población** (lista de individuos), y `list_pincelada` es el cromosoma. Conviene renombrarlas para no confundirse al explicar.
- Todas las pinceladas miden lo mismo (30 × 10). El tamaño y el grosor no se optimizan.
- No hay transparencia: cada pincelada tapa por completo lo de abajo.
- Con 100 pinceladas de 30 × 10 se cubre solo una parte de la imagen, así que el término de cobertura domina el fitness. Por eso los 10 valores salen muy parecidos (≈ 0.19–0.20).
- `if len(hedge_array) != 0` se usa como interruptor para "medir cobertura o no". Funciona, pero un parámetro booleano sería más claro.

---

## 3. Código de Angie: `pincelada y randomizer.ipynb`

### 3.1 Qué hace, celda por celda

| Celda | Contenido | Qué hace |
|---|---|---|
| 1 | imports | `random, math, PIL, numpy` |
| 2 | Carga de imagen | Abre `vanGogh2.jpeg` y guarda como **variables globales** `img_width`, `img_height` e `img_original_RGB` (arreglo numpy). Las demás clases dependen de ellas |
| 3 | `class Pincelada` | Atributos: `points` (lista de puntos), `size` (largo), `width` (grosor), `angle`, `color`, `tipo` (`"line"` o `"arc"`), y `start`/`end` para arcos. Tiene `print()` para ver sus datos |
| 4 | `class Pincelada_Randomizer` | Genera pinceladas al azar dentro de rangos (`min/max_size`, `min/max_angle`, `min/max_width`, `factor_arco`). `generate_Random_Pincelada()` elige color, tipo, grosor, tamaño, ángulo y puntos. `random_Points()` calcula el segundo punto con `size·cos/sin(angle)`. Para arcos arma la caja `[(x_min,y_min),(x_max+15,y_max+10)]` que pide `ImageDraw.arc` y adelgaza el trazo con `factor_arco` |
| 5 | `class ImagenEvolutiva` | Un **individuo**: `lista_pinceladas` y `hedge_array`. `add_Pincelada()` agrega una pincelada. `update_Hedge_Array()` dibuja todas en blanco y marca la cobertura. `generate_image()` dibuja la imagen con sus colores |
| 6 | `class AlgoritmoEvolutivo` | `number_chromosomes` (10 imágenes), `number_genes` (100 pinceladas), `hedge_lambda`, `fitness`, `list_chromosomes`. Métodos: `mean_square_error()` (misma fórmula que Leo), `calculate_Fitness()`, `show_Best_Option()` y `create_Chromosomes()` |
| 7–10 | Ejecución | Crea el randomizer y el algoritmo, genera la población, calcula y muestra el fitness |
| 11 | (nueva) | `show_Best_Option()`: muestra la mejor imagen |
| 12 | Hedge | Imprime el `hedge_array` de una imagen |
| 13–14 | Demo | Genera 500 pinceladas al azar (el comentario dice 50) y las dibuja para ver cómo se ven |

**Lo que aporta respecto a Leo:** diseño orientado a objetos, pinceladas curvas (`arc`), y tamaño, grosor y ángulo variables con rangos configurables.

### 3.2 Dónde fallaba (corregido)

| # | Dónde | Problema | Por qué falla | Corrección |
|---|---|---|---|---|
| 1 | Celda 2 | `Image.open("vanGogh2.jpeg")` | El notebook está en la raíz y la imagen en `Angie_codigo/`: `FileNotFoundError` | Ruta `Angie_codigo/vanGogh2.jpeg` |
| 2 | `create_Chromosomes` (**tu captura**) | El parámetro se llamaba `pincelada_randomizer`, pero adentro se usaba `randomizer` | Funcionaba solo porque existía una variable global con ese nombre | Parámetro renombrado a `randomizer` |
| 3 | `create_Chromosomes` | Usaba `algoritmo_evol.` (variable global) en vez de `self.` | Si el objeto se llama distinto, falla | `self.` |
| 4 | `create_Chromosomes` | Los dos ciclos usaban `i` | El ciclo interno pisa la variable del externo (aquí no rompía, pero es un error clásico) | Ciclo interno con `j` |
| 5 | `create_Chromosomes` (**tu captura**) | Faltaba `img_evol.update_Hedge_Array()` | Sin esa línea el `hedge_array` queda en ceros: no hay píxeles "pintados" y el fitness siempre sale en su valor máximo, `1.0`. Por eso tu salida era `[1.0, 1.0, …]` | Se agregó la línea |
| 6 | `mean_square_error` | `img_original` no existe | `NameError`: la variable se llama `img_original_RGB` | `img_original_RGB` |
| 7 | `mean_square_error` | `img_evolutiva.astype(...)` | `img_evolutiva` es un **objeto** `ImagenEvolutiva`, no un arreglo: `AttributeError` | `np.array(img_evolutiva.image)` |
| 8 | `mean_square_error` | `img_evol.hedge_array` | `img_evol` no existe dentro del método | `img_evolutiva.hedge_array` |
| 9 | `calculate_Fitness` | No dibujaba la imagen antes de medir | `img_evolutiva.image` no existe hasta llamar `generate_image()` | Se llama `generate_image()` antes |
| 10 | `calculate_Fitness` | No vaciaba `self.fitness` | Al llamarlo dos veces la lista crecía a 20, 30… valores y `show_Best_Option` elegía mal | `self.fitness = []` al inicio |
| 11 | `generate_image` | No regresaba la imagen | `show_Best_Option` hacía `None.show()`: `AttributeError` | `return image` |
| 12 | Celda del hedge | `img_evol.update_Hedge_Array()` | `img_evol` no existe fuera de la clase: `NameError` | Se toma `algoritmo_evol.list_chromosomes[0]` |
| 13 | `generate_Random_Pincelada` | `random_Value_In_Range(self.min_size, self.min_size)` | El tamaño siempre era `min_size`: `max_size` nunca se usaba | `(self.min_size, self.max_size)` |
| 14 | `random_Color` | `y = random.randint(0, img_width-1)` | La `y` debe ir hasta la altura. Con imágenes horizontales se sale del arreglo (`IndexError`); con esta imagen vertical solo nunca toma colores de la parte de abajo | `img_height-1` |
| 15 | `random_Points` | Con ángulos > 90° el `x_length` es **negativo** (y con > 180° también `y_length`) | El rango de `randint` queda mal y el segundo punto puede salir de la imagen | Se usa `abs(x_length)` y `abs(y_length)` |

### 3.3 Observaciones que no impiden correr (no se cambiaron)
- **`% 359` en `random_Start_End`**: se deja así por decisión de Angie (360° equivale a 0°). Nota: `% 360` da valores de 0 a 359 y nunca llega a 360, así que con `% 359` lo único que cambia es que el ángulo 359° no aparece. En la práctica la diferencia es de un grado.
- **`hedge_lambda = 0`**: con λ = 0 el término de cobertura desaparece y solo se mide el error donde se pintó. El algoritmo preferiría imágenes con **pocas** pinceladas bien coloreadas. Leo usa 0.2. Es una decisión de diseño que el equipo debe tomar.
- **`random_Color` toma un píxel cualquiera** de la imagen, no el píxel donde cae la pincelada. Leo sí lo toma en la posición, y eso da imágenes mucho más parecidas desde el inicio.
- `parametros_chromosomas` (en `AlgoritmoEvolutivo`) se define pero **no se usa**. Los rangos que se aplican son los del `Pincelada_Randomizer`.
- `angle` significa dos cosas distintas: inclinación en las líneas y apertura en los arcos.
- La caja del arco con `+15` y `+10` es un "parche" para que no quede de alto o ancho cero.
- Dependen de **variables globales** (`img_width`, `img_height`, `img_original_RGB`). Por eso las celdas deben correrse en orden.
- `points=[]` como valor por defecto en `__init__` es una trampa conocida de Python: la lista se comparte entre objetos. Aquí no rompe nada porque siempre se reasigna.
- Los `del` al final de los métodos no hacen falta: Python libera esas variables solo.
- `.show()` abre la imagen en el visor del sistema operativo (en Windows, la app Fotos). Dentro de Jupyter se vería en el notebook con `display(img)`.

### 3.4 `Angie_codigo/vanGogh.ipynb` (borrador anterior)
Es la primera versión del notebook. No se modificó porque el de la raíz la reemplaza. Tenía `_init_` en lugar de `__init__` (por eso el constructor nunca se ejecutaba), métodos sin `self`, una variable `y_1` sin definir en `create_two_random_Points` y funciones marcadas "NO ESTÁ LISTO".

---

## 4. Comparación rápida

| | Leo | Angie |
|---|---|---|
| Estilo | Funciones sueltas + namedtuple | Clases (programación orientada a objetos) |
| Tipos de pincelada | Solo líneas | Líneas y arcos |
| Tamaño y grosor | Fijos | Aleatorios dentro de rangos |
| Color | Píxel en la posición de la pincelada ✔ | Píxel aleatorio de toda la imagen |
| Fitness | MSE en lo pintado + λ·(1 − cobertura), λ = 0.2 | La misma fórmula, con λ = 0 |
| Cobertura | Se calcula al dibujar cada pincelada | Se calcula al final, dibujando todas en blanco |
| Evolución | No | No |

---

## 5. Qué les falta para ser un algoritmo evolutivo

Según Engelbrecht (cap. 8, algoritmo evolutivo genérico), los pasos son:

```
1. Inicializar la población                      ← YA EXISTE (create_Chromosomes / ciclo de Leo)
2. Mientras no se cumpla el criterio de paro:    ← FALTA (ciclo de generaciones)
   a. Evaluar el fitness de cada individuo       ← YA EXISTE (calculate_Fitness / oo_mse)
   b. Seleccionar padres                          ← FALTA (p. ej. torneo o ruleta)
   c. Cruzar padres para crear hijos              ← FALTA (p. ej. intercambiar pinceladas entre dos imágenes)
   d. Mutar a los hijos                           ← FALTA (p. ej. mover, girar o recolorear una pincelada)
   e. Formar la nueva generación                  ← FALTA (reemplazo; opcional: elitismo)
3. Regresar el mejor individuo                    ← YA EXISTE (show_Best_Option / best_option)
```

En concreto, falta:
1. **Ciclo de generaciones** con un número de generaciones (o un criterio de paro).
2. **Selección** de padres según su fitness.
3. **Cruza:** con su representación, lo natural es un *cruce de un punto* sobre la lista de pinceladas. El hijo toma las primeras k pinceladas de un padre y las demás del otro.
4. **Mutación:** cambiar al azar algún atributo de una pincelada (posición, ángulo, tamaño o color) o reemplazarla por una nueva con el randomizer.
5. **Reemplazo y elitismo:** decidir quién pasa a la siguiente generación y conservar siempre al mejor.
6. **Registro** del mejor fitness por generación, para poder graficar la convergencia en el reporte.
7. **El "estilo" de Van Gogh/Monet:** por ahora solo se copia el color de la imagen. Habría que definir qué rasgo del pintor se va a imitar (largo y forma del trazo, orientación, transparencia) y cómo entra en el fitness o en los rangos del randomizer.

Recomendación: tomar como base el notebook de Angie, que ya tiene las clases, y llevar a él la idea de Leo de tomar el color **en la posición** de la pincelada. Después agregar los pasos 1–6 como métodos de `AlgoritmoEvolutivo`.

---

## 6. Cómo correrlos

Ver las instrucciones de la respuesta en el chat o el archivo `README.md` de esta rama.
