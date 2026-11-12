# Optimizacion

Rama `claude/codigos-angie-leo`: los códigos de Angie y Leo corregidos y las fases 1, 2 y 3 del algoritmo evolutivo.
El análisis de los códigos originales está en [`INFORME_CODIGOS.md`](INFORME_CODIGOS.md).

## Archivos
| Archivo | Qué es |
|---|---|
| `Leo_codigo/vanGogh.py` | Código de Leo (corregido) |
| `pincelada y randomizer.ipynb` | Notebook de Angie (corregido) |
| `vanGogh_evolutivo.py` | Fase 1: algoritmo evolutivo (script) |
| `vanGogh_evolutivo.ipynb` | Fase 1: el mismo código, por celdas |
| `vanGogh_evolutivo_fase2.py` / `.ipynb` | Fase 2: fase 1 + fusión de pinceladas |
| `fase3_vangogh.py` / `.ipynb` | Fase 3: fase 2 + estilo Van Gogh (pinceladas, imagen objetivo y dirección del contorno) |
| `fase3_monet.py` / `.ipynb` | Fase 3: fase 2 + estilo Monet (pinceladas e imagen objetivo, sin fusión) |
| `fase4_noche_estrellada.py` / `.ipynb` | Fase 4: Van Gogh con cerdas en cada pincelada, reproduciendo *La noche estrellada* |
| `medida_estilo.py` | Medida simple de estilo (paleta, bordes y coherencia) contra *La noche estrellada* |
| `imagenes/torii.jpg` | Imagen de entrada de la fase 3 (arcos japoneses) |
| `imagenes/noche_estrellada.jpg` | *La noche estrellada* (referencia de estilo e imagen de entrada de la fase 4) |
| `PRUEBAS.md` | Resultados de las pruebas |

## Cómo correrlos
Requisitos: Python 3 y `pip install numpy pillow matplotlib notebook`.

**Leo** (desde la carpeta `Leo_codigo`):
```
cd Leo_codigo
python vanGogh.py
```

**Angie** y **fase 1**: desde la raíz del repositorio, porque la ruta de la imagen es `Angie_codigo/vanGogh2.jpeg`.
```
jupyter notebook "pincelada y randomizer.ipynb"
python vanGogh_evolutivo.py
jupyter notebook vanGogh_evolutivo.ipynb
python vanGogh_evolutivo_fase2.py
python fase3_vangogh.py
python fase3_monet.py
python fase4_noche_estrellada.py
```
Las fases 1 y 2 guardan la mejor imagen cada 10 generaciones y la gráfica del fitness en `resultados_fase1/` o `resultados_fase2/`.
La fase 3 guarda cada 50 generaciones (`cada_cuanto`) en `resultados_fase3_vangogh/` o `resultados_fase3_monet/`, junto con la imagen objetivo, `resultado.png` y `fitness.png`; al final imprime la medición del estilo. La carpeta se cambia en `carpeta_salida`.
Los dos estilos se pueden correr al mismo tiempo en dos terminales.
Los parámetros se cambian al inicio del archivo (en el notebook, en la segunda celda).
La fase 4 guarda en `resultados_fase4_noche/`.
