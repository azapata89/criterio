---
name: lente-benchmarks
description: Método correcto para medir rendimiento (baseline, warmup, varianza, entorno estable) con hyperfine, pyperf, pytest-benchmark, Vitest bench, PHPBench y k6. Úsala cuando se vaya a medir, comparar u optimizar rendimiento, o antes de afirmar que algo es más rápido o más lento.
---

# Lente: benchmarks

## Regla principal
No afirmes que algo es más rápido o más lento sin una medición hecha con este método. Si no se puede medir, di «no medido».

## Cómo usarla
1. Busca en `docs/knowledge/INDEX.md` las notas con área `perf`, como benchmarks previos o una baseline guardada.
2. Elige la herramienta según el nivel que quieras medir:
   - comando o CLI: `hyperfine`;
   - función Python: `pyperf` o `pytest-benchmark`;
   - JS/TS: `vitest bench`, que es experimental;
   - PHP: `PHPBench`;
   - HTTP: `k6`.
3. Reporta en una tabla: baseline y cambio, con media o mediana ± desviación, número de corridas y máquina. Interpreta el resultado en una línea.

## Checklist
1. **Baseline en las mismas condiciones:** misma máquina, misma sesión y mismos datos, comparando la rama main contra el cambio. Nunca contra números de otra corrida.
2. **Warmup y varias corridas** (`hyperfine --warmup N`; pyperf ya lo hace). Reportar media o mediana ± desviación, no un solo número.
3. **Ruido:** una diferencia dentro de la varianza no es una mejora. Si hay outliers, repetir.
4. **Entorno estable:** cerrar otros procesos y, si se puede, usar `pyperf system tune`. Anotar el hardware.
5. **Cachés:** decidir si se mide en frío o en caliente y prepararlas explícitamente (`hyperfine --prepare`).
6. **Microbenchmarks:**
   - usar el resultado calculado, para que el compilador o el JIT no eliminen el trabajo;
   - usar datos realistas;
   - confirmar con un benchmark de más alto nivel.

   Este punto es práctica general, no tiene fuente verificada.
7. **Guardar y comparar:** `pytest-benchmark --benchmark-autosave` / `--benchmark-compare-fail`, o las referencias de PHPBench.
8. **HTTP:** k6 con thresholds de p95/p99 y tasa de error, rampa de carga y un entorno parecido a producción. El promedio solo no basta.

## Fuentes (verificadas 2026-10-09)
- [hyperfine](https://github.com/sharkdp/hyperfine) · pyperf: [docs](https://pyperf.readthedocs.io/en/latest/), [system tune](https://pyperf.readthedocs.io/en/latest/system.html), [run benchmark](https://pyperf.readthedocs.io/en/latest/run_benchmark.html)
- [pytest-benchmark](https://pytest-benchmark.readthedocs.io/en/latest/usage.html) · [Vitest benchmarking](https://vitest.dev/guide/benchmarking) · [PHPBench](https://phpbench.readthedocs.io/en/latest/)
- k6: [docs](https://grafana.com/docs/k6/latest/), [test types](https://grafana.com/docs/k6/latest/testing-guides/test-types/), [thresholds](https://grafana.com/docs/k6/latest/using-k6/thresholds/)
