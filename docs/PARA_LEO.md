# Para Leo: qué pasó con tu código

Lectura de ~5 minutos. El documento completo es `DOCUMENTACION.md`, en la raíz del repositorio.

## 1. Tu `vanGogh.py` corregido
Está en **`Leo_codigo/vanGogh_corregido.py`**. Tu original no se tocó. Cada cambio está marcado con `# CORREGIDO`:

| Problema | Corrección |
|---|---|
| `generate_img` recorría `range(len(list_pincelada))`, una **variable global**, en vez del cromosoma recibido | `range(len(cromosome))` |
| `roger.jpg` no está en el repositorio | La ruta se pasa como argumento (por defecto `../Angie_codigo/vanGogh2.jpeg`) |
| El mejor individuo se dibujaba **encima de la última imagen evaluada** (lienzo sucio) | Se dibuja en un lienzo nuevo, y además se guarda `mejor_individuo.png` |

> Ese archivo sigue siendo **búsqueda aleatoria**: genera 10 individuos y elige el mejor, sin selección, cruza ni mutación.

## 2. `ea_vangogh.py` (tu AG anterior) → código principal
Los operadores de `Leo_codigo/ea_vangogh.py` ahora viven en la clase **`AlgoritmoEvolutivo`** de `pintor_evolutivo/pintor_evolutivo.py`:

| Tu idea | Dónde quedó | Qué se mejoró |
|---|---|---|
| Genes reales normalizados en [0,1] | `Pincelada.from_Genes` | 9 → **10 genes** (se agrega la `curvatura`, para los arcos de Angie) |
| Torneo (k=3) | `torneo()` | Sin cambios |
| Cruza BLX-α (α=0.3) | `cruza_BLX()` | El ángulo es **circular**: se "desenrolla" antes de mezclar (0.98 y 0.02 ya no dan 0.5) |
| Mutación gaussiana con σ decreciente | `mutacion_Gaussiana()` | σ distinta por tipo de gen: el paso en x,y es proporcional al tamaño del trazo |
| Elitismo | `evolucionar_Etapa()` | Sin cambios |
| Etapas de lo grueso a lo fino | `largo_de_capa()` | Decaimiento geométrico en lugar de lineal |
| Campo de flujo (diferencias centrales) | `campo_de_flujo()` | Ahora usa el **tensor de estructura** (más estable) y además calcula la **coherencia** |
| Penalización λ·mean(\|sin Δθ\|)·1e-3 | `calculate_Fitness()` | Se pondera por **área del trazo × coherencia** y se elimina el `1e-3` arbitrario. Así compite en las mismas unidades que el MSE |

## 3. Cambios de diseño (y su justificación)
1. **K = 1 pincelada por cromosoma**, en lugar de 5. Con el mismo número de pinceladas, K=1 deja un error mucho menor (experimento E3, 3000 pinceladas: **MSE 0.00462 con K=1 contra 0.00760 con K=3**, es decir 64% más error). Con K>1, una pincelada buena queda "amarrada" a otras malas.
2. **Solo se pinta si mejora.** Antes, el mejor de cada etapa siempre se pintaba, aunque empeorara el lienzo. Ahora una etapa que no mejora se rechaza.
3. **Evaluación incremental.** Antes cada evaluación copiaba el lienzo y dibujaba sobre toda la imagen. Ahora solo se recalcula la caja envolvente del trazo, con un mapa de error por píxel y una pila de deshacer. Es exacto y cientos de veces más rápido.
4. **Focos guiados por el error.** Las pinceladas nuevas se sortean donde el lienzo más difiere del objetivo, no en cualquier lugar.
5. **Salida en alta resolución.** Las pinceladas son vectoriales: el AG trabaja a 300–400 px y la pintura se vuelve a dibujar ×3.

## 4. El experimento que defiende el AG (E1)
Con el **mismo número de evaluaciones de fitness** (3 semillas, 3000 pinceladas):

| Método | MSE final |
|---|---|
| AG (torneo + BLX + mutación + elitismo) | **0.00462 ± 0.00002** |
| Búsqueda aleatoria guiada (lo que hacía `vanGogh.py`, pero guiada) | 0.00517 ± 0.00002 |

El AG tiene **~11% menos error**. Si al profesor le preguntan "¿para qué el AG si la inicialización ya es buena?", esta es la respuesta. Los detalles, incluida la comparación con el mismo *tiempo*, están en `resultados/experimentos/`.

## 5. Cómo probarlo
```bash
cd pintor_evolutivo
python pintor_evolutivo.py ../imagenes/torii.jpg --estilo vangogh --pinceladas 3000
python experimentos.py ../imagenes/torii.jpg --procesos 2
```
