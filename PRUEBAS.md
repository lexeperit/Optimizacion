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
