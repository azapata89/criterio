import assert from 'node:assert/strict'
import { formatearPrecio as f } from '../src/precio.js'

const casos = [
  [() => f(-1500), '-$ 1.500'],
  [() => f(-1234567), '-$ 1.234.567'],
  [() => f(1234567), '$ 1.234.567'],
  [() => f(0), '$ 0'],
  [() => f(1499.5), '$ 1.500'],
  [() => f(-0.4), '$ 0'],
  [() => f(999), '$ 999'],
]
let fallas = 0
for (const [fn, esperado] of casos) {
  try { assert.equal(fn(), esperado) } catch { fallas++ }
}
console.log(fallas ? `OCULTOS_FALLA ${fallas}` : 'OCULTOS_OK')
