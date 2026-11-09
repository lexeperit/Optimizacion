# Resultados

## Arcos japoneses (`imagenes/torii.jpg`), 20,000 pinceladas
Trabajo a 400×533 px y salida a 1200×1599 px. Comando:
`python pintor_evolutivo.py ../imagenes/torii.jpg --estilo <vangogh|monet> --pinceladas 20000 --ancho 400 --escala_salida 3`

| | Van Gogh | Monet |
|---|---|---|
| Resultado | [`torii_vangogh/resultado.png`](torii_vangogh/resultado.png) | [`torii_monet/resultado.png`](torii_monet/resultado.png) |
| Foto vs. pintura | [`comparacion.jpg`](torii_vangogh/comparacion.jpg) | [`comparacion.jpg`](torii_monet/comparacion.jpg) |
| Animación | [`timelapse.gif`](torii_vangogh/timelapse.gif) | [`timelapse.gif`](torii_monet/timelapse.gif) |
| MSE / PSNR / SSIM | 0.00418 / 23.79 dB / 0.732 | 0.00074 / 31.30 dB / 0.887 |
| Tiempo | 9.9 min | 11.1 min |

**Capturas del avance:** `progreso_00025.jpg`, `00050`, `00100`, `00200`, `00400`, `00800`, `01600`, `03200`, `06400`, `12800` y `20000`, en cada carpeta.

Otros archivos: `metricas.json` (resumen), `historial.csv` (cada etapa), `convergencia.png`, `objetivo_estilizado.png` y `pinceladas.json` (las 20,000 pinceladas, para reanudar o volver a dibujar).

## Experimentos (`experimentos/`)
`resumen.csv` concentra todas las cifras. Los detalles están en `DOCUMENTACION.md`, sección 9.2.
- **E1 / E1b:** AG contra búsqueda aleatoria guiada, con las mismas evaluaciones y con el mismo tiempo (`convergencia_ag_vs_aleatoria.png`).
- **E2:** efecto de λ_flujo en Van Gogh (`panel_lambda_flujo.jpg`).
- **E3:** K = 3 contra K = 1 pinceladas por cromosoma.

Los archivos `log_*.txt` son la salida de consola de cada corrida.
