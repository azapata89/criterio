import { test, expect } from 'vitest'
import { sum } from './sum.js'

test('suma', () => expect(sum(2, 3)).toBe(5))
