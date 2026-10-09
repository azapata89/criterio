import { test } from 'node:test'
import assert from 'node:assert/strict'
import { formatearPrecio } from '../src/precio.js'

test('miles con punto', () => {
  assert.equal(formatearPrecio(1234567), '$ 1.234.567')
})
