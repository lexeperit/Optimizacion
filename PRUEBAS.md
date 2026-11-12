# Pruebas de las fases 1 y 2

Imagen `Angie_codigo/vanGogh2.jpeg`, población 10, 100 pinceladas, 100 generaciones, λ = 0.2,
torneo 3, cruza 80%, mutación 5%. Fase 2: `prob_fusion = 0.5`, `max_fusion = 3`.
Cada fila es el promedio de 5 semillas (1 a 5).

| Variante | Fitness final (media ± d.e.) | Cobertura | Fusiones aceptadas | Tiempo por corrida |
|---|---|---|---|---|
| Fase 1 (sin fusión) | 0.1494 ± 0.0006 | 36.3% | — | 8 s |
| Fase 2, distancia 15 px | 0.1478 ± 0.0014 | 37.1% | 127 de 187 | 11 s |
| **Fase 2, distancia 25 px** | **0.1465 ± 0.0012** | 37.6% | 258 de 447 | 14 s |
| Fase 2, distancia 40 px | 0.1461 ± 0.0010 | 37.6% | 262 de 454 | 14 s |
| Control: quitar una pincelada al azar + nueva + aceptar si no empeora | 0.1482 ± 0.0007 | — | 131 de 457 | — |

- Con distancia 25 px, las 5 semillas con fusión terminan mejor que las 5 sin fusión.
- El **control** usa el mismo mecanismo, pero en lugar de fusionar quita una pincelada al azar. Mejora menos (0.1482 contra 0.1465) y se acepta la mitad de veces (29% contra 58%). Unas dos terceras partes de la mejora vienen de la fusión misma y el resto de meter una pincelada nueva con aceptación.
- Distancia 40 px casi no mejora sobre 25 px. Se dejó 25 px.
- La suma de la `particion` de la mejor imagen queda alrededor de 112: con 100 posiciones representa unas 112 pinceladas originales.

## ¿Qué parámetro hay que subir para aproximarse mejor a la imagen?

Algoritmo de la fase 2, semilla 1. **PSNR total** compara la mejor imagen contra la original en *todos* los píxeles, incluido el fondo negro sin pintar: más alto es mejor. El fitness solo mide donde se pintó, por eso no sirve para saber qué tanto se parece la imagen completa.

| Prueba | Población | Pinceladas | Generaciones | prob_mutation | Fitness | Cobertura | PSNR total | Tiempo* |
|---|---|---|---|---|---|---|---|---|
| Base (fase 2) | 10 | 100 | 100 | 0.05 | 0.1447 | 39% | 7.3 dB | 13 s |
| Más generaciones | 10 | 100 | 400 | 0.05 | 0.1376 | 42% | 7.4 dB | 55 s |
| Más población | 30 | 100 | 100 | 0.05 | 0.1445 | 38% | 7.2 dB | 43 s |
| Más pinceladas | 10 | 300 | 300 | 0.01 | 0.0680 | 79% | 10.7 dB | 69 s |
| Más pinceladas | 10 | 600 | 300 | 0.005 | 0.0383 | 93% | 13.6 dB | 106 s |
| Igual, pero mutación sin ajustar | 10 | 600 | 300 | 0.05 | 0.0508 | 89% | 12.4 dB | 104 s |
| Más pinceladas | 10 | 1000 | 300 | 0.003 | 0.0292 | 97% | 14.6 dB | 151 s |
| **Más pinceladas y generaciones** | 10 | 1000 | 1000 | 0.003 | **0.0196** | 99% | **16.9 dB** | 500 s |
| Pinceladas chicas (20–35 px, grosor 8–12) | 10 | 2000 | 300 | 0.0015 | 0.0368 | 93% | 13.7 dB | 248 s |
| Pinceladas chicas (20–35 px, grosor 8–12) | 10 | 2000 | 1000 | 0.0015 | 0.0260 | 96% | 15.3 dB | 821 s |

\*En este entorno, con 3–4 corridas a la vez. En una laptop puede ser ~1.5 veces más.

Conclusiones:
- **Lo que más importa es el número de pinceladas.** Con 100 la imagen nunca pasa de ~40% pintada, así que sin importar cuántas generaciones corran, lo negro domina.
- **`prob_mutation` hay que ajustarla al número de pinceladas**, a unas 3/`number_pinceladas`. Con 600 pinceladas y 0.05 se reemplazan ~30 pinceladas por hijo en cada generación, y el resultado empeora.
- **Más generaciones ayudan cuando ya hay suficientes pinceladas**: con 1000, pasar de 300 a 1000 generaciones sube de 14.6 a 16.9 dB y la curva todavía no se aplana.
- **Más población no mejoró** en las mismas generaciones, y el tiempo crece en proporción.
- **Las pinceladas chicas todavía no convienen**: con 2000 pinceladas chicas y 1000 generaciones quedó peor que con 1000 normales. Necesitan muchas más generaciones.

## Fase 3: estilos (imagen `imagenes/torii.jpg` reducida a 400 px de ancho, semilla 1)

| | Van Gogh (`fase3_vangogh.py`) | Monet (`fase3_monet.py`) |
|---|---|---|
| Pinceladas / generaciones | 1000 / 1000 | 2500 / 1000 |
| Fitness inicial → final | 0.0871 → 0.0387 | 0.0479 → 0.0209 |
| PSNR contra su imagen objetivo | 14.0 dB | 16.4 dB |
| Largo promedio | 75 px | 17 px |
| Arcos | 56.6% | 8.2% |
| Líneas que siguen el contorno (±20°) | 99.5% | 21.5% (lo que daría el azar) |
| Saturación promedio (foto: 75) | 106.8 | 72.1 |
| Fusiones aceptadas | 830 de 4470 | — (apagada) |
| Tiempo en este entorno | 10.4 min | 3.6 min |

- En Van Gogh el 99.5% de líneas siguiendo el contorno es por construcción (el randomizer las genera así). Lo útil es compararlo contra Monet, donde la orientación es libre.
- Monet tiene mejor PSNR porque su objetivo está desenfocado (menos detalle que reproducir) y sus trazos son chicos.
- En Van Gogh se aceptan menos fusiones que en la fase 2 (19% contra 58%): los trazos largos y curvos casi nunca quedan con los dos extremos a menos de 25 px.

### Van Gogh más fiel (1000 generaciones, semilla 1)

| Variante | Pinceladas | Largo | Grosor | Arcos | Apertura arcos | PSNR | Largo prom. | Tiempo* |
|---|---|---|---|---|---|---|---|---|
| Original de la fase 3 | 1000 | 60–90 | 10–16 | 60% | 60–180 | 14.0 dB | 75 px | 10.4 min |
| Igual, menos arcos | 1000 | 60–90 | 10–16 | 30% | 40–120 | 14.3 dB | 76 px | 8.7 min |
| **Medianas** | 1500 | 40–60 | 8–14 | 40% | 40–120 | **14.4 dB** | 50 px | 11.2 min |
| Cortas, menos arcos | 1500 | 30–50 | 8–12 | 30% | 40–120 | 13.7 dB | 40 px | 10.5 min |
| Cortas | 1500 | 30–50 | 8–12 | 60% | 60–180 | 13.3 dB | 40 px | 11.7 min |

\*Con 4 corridas a la vez. Con 1500 pinceladas se usó `prob_mutation = 0.002`.

- Las diferencias de PSNR son chicas (menos de 0.5 dB). A la vista, las variantes medianas y cortas muestran mejor la forma del arco (travesaño superior y columnas).
- Las cortas tienen menor PSNR porque necesitan más generaciones, como ya se vio en la fase 2.
- Menos arcos y con menos apertura quita remolinos encima de las columnas y mejora un poco la fidelidad.
