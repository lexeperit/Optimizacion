# Guía: Algoritmo evolutivo para pintar estilo Van Gogh

## 1. ¿Dónde estaba el equipo?
| Código | Qué hace | Qué falta / problemas |
|---|---|---|
| `Leo_codigo/vanGogh.py` | Crea 10 individuos de 100 pinceladas al azar, los dibuja y evalúa un fitness (MSE + cobertura). Muestra el mejor. | **No hay evolución**: sin selección, cruza, mutación ni generaciones. Es solo búsqueda aleatoria. Necesita `roger.jpg`, que no está en el repo. |
| `Angie_codigo/vanGogh.ipynb` | Refactor en clases (`Pincelada`, `ImageGenerator`, `AlgoritmoEvolutivo`). Agrega arcos. | No corre: `_init_` en vez de `__init__`, falta `self`, `y_1` no definido, funciones marcadas "NO ESTÁ LISTO". |

**Fitness actual de Leo/Angie:** `MSE en píxeles pintados / 255² + λ·(1 − %cobertura)`.
El término de cobertura existe porque, si solo mides el error donde pintaste, al algoritmo le conviene pintar poco. La nueva versión lo evita: arranca con un lienzo del color promedio y mide el MSE en **toda** la imagen.

## 2. Formulación (lo que hace `ea_vangogh.py`)

**Representación (genotipo).** Cada pincelada tiene 9 genes reales en [0,1]:

| gen | significado | decodificación |
|---|---|---|
| x, y | posición del centro | ×(ancho−1), ×(alto−1) |
| ángulo | orientación ("ángulo de ataque") | ×π |
| largo | longitud del trazo | 2 + g·largo_max |
| grosor | ancho del pincel | 1 + g·grosor_max |
| alpha | transparencia | 60 a 255 |
| r, g, b | color | ×255 |

**Cromosoma** = bloque de K pinceladas (K=5 por defecto), es decir, una matriz K×9.

**Pintura por etapas.** Evolucionar 800 pinceladas a la vez sería un problema de 7200 dimensiones, muy difícil de optimizar. Por eso, en cada etapa se corre un AG pequeño que encuentra las mejores K pinceladas para pintar **encima** del lienzo actual. Cuando termina la etapa, esas pinceladas quedan fijas y empieza la siguiente. Así trabaja un pintor real: por capas.

**Coarse-to-fine.** El tamaño máximo de las pinceladas baja con las etapas. Primero se pintan manchas grandes y al final los detalles.

**Fitness (minimizar):**
```
f = MSE(lienzo + pinceladas, objetivo)/255²  +  λ_flujo · mean|sin(θ_pincelada − θ_flujo)| · 1e-3
```
El segundo término es el **"estilo Van Gogh"**. `θ_flujo` es la dirección perpendicular al gradiente de la imagen (operador de diferencias tipo Sobel), es decir, la dirección de los contornos. Premiar las pinceladas que siguen esos contornos produce los trazos arremolinados característicos.

**Operadores (Engelbrecht, cap. 9, AG de codificación real):**
- Inicialización heurística: el color se toma del píxel objetivo y el ángulo del campo de flujo.
- Selección por torneo (k=3).
- Cruza BLX-α (α=0.3), con probabilidad pc=0.8.
- Mutación gaussiana por gen (pm=0.3). σ decrece linealmente con las generaciones (exploración → explotación). El ángulo se trata como circular.
- Elitismo de 1.

## 3. Cómo correrlo
```bash
cd Leo_codigo
python3 ea_vangogh.py ../Angie_codigo/vanGogh2.jpeg --pinceladas 800 --salida salida
```
Parámetros: `--K`, `--poblacion`, `--generaciones`, `--lambda_flujo`, `--ancho`, `--semilla`.
Salidas: `resultado.png`, `progreso_XXXX.png`, `fitness.csv` y `comparacion.png` (objetivo | 85 pinceladas | 800 pinceladas).

Resultado con 800 pinceladas a 200 px de ancho: ~38 s de ejecución, fitness de 0.0129 (≈ etapa 85) a 0.0109.

## 4. Ideas para seguir (avance propio / experimentos para el reporte)
1. **Comparar algoritmos:** AG vs Estrategia Evolutiva (1+λ) con σ autoadaptativo vs Programación Evolutiva. Todos usan la misma función de fitness.
2. **Barrido de λ_flujo** (0, 5, 20): muestra cómo cambia el "estilo".
3. **Pinceladas curvas** (arcos o Bézier, como proponía Angie) y bordes suaves.
4. **Fitness perceptual:** SSIM o comparar en espacio Lab en lugar de RGB.
5. **Transferencia de estilo:** usar una foto como objetivo y tomar la *paleta* de colores de una pintura de Van Gogh, de modo que los genes r,g,b se restrinjan a esa paleta.
6. Graficar `fitness.csv` (convergencia) y repetir con varias semillas para obtener estadísticas.
