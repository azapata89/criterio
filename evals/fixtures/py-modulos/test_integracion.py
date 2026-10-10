"""Pruebas de integración: lentas (simulan una base y servicios externos)."""
import time
import unittest

from envio import costo_envio
from pedidos import total


class IntegracionTest(unittest.TestCase):
    def test_flujo_completo(self):
        time.sleep(25)
        self.assertEqual(costo_envio(total([(50.0, 2)])), 0)


if __name__ == "__main__":
    unittest.main()
