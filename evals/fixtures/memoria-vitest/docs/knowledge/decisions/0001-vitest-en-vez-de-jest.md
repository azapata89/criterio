---
type: decision
title: Usamos Vitest (no Jest) para los tests
status: active
area: qa
verified_at: 2026-10-09
sources: [package.json]
refs: [package.json]
---

## Contexto
Proyecto Vue 3 sobre Vite. Había que elegir runner de tests.

## Opciones consideradas
- Vitest: reutiliza la config de Vite.
- Jest: requiere config y transformaciones propias.

## Decisión
Vitest, porque reutiliza la config de Vite y evita mantener dos pipelines.

## Consecuencias
- Una sola config para dev, build y tests.

## Confirmación
`package.json` tiene `vitest` y no `jest`.
