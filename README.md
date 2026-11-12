# Optimizacion

Rama `claude/codigos-angie-leo`: los códigos de Angie y Leo corregidos y la **fase 1** del algoritmo evolutivo.
El análisis de los códigos originales está en [`INFORME_CODIGOS.md`](INFORME_CODIGOS.md).

## Archivos
| Archivo | Qué es |
|---|---|
| `Leo_codigo/vanGogh.py` | Código de Leo (corregido) |
| `pincelada y randomizer.ipynb` | Notebook de Angie (corregido) |
| `vanGogh_evolutivo.py` | Fase 1: algoritmo evolutivo (script) |
| `vanGogh_evolutivo.ipynb` | Fase 1: el mismo código, por celdas |

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
```
La fase 1 guarda la mejor imagen cada 10 generaciones y la gráfica del fitness en `resultados_fase1/`.
Los parámetros se cambian al inicio del archivo (en el notebook, en la segunda celda).
