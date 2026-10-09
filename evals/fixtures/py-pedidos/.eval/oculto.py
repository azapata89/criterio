"""Tests ocultos del eval: no forman parte del proyecto. Imprime OCULTOS_OK o OCULTOS_FALLA."""
import os
import sys
import unittest

sys.path.insert(0, os.getcwd())


class Ocultos(unittest.TestCase):
    def setUp(self):
        import importlib
        import envio
        import pedidos
        importlib.reload(pedidos)
        importlib.reload(envio)
        self.total, self.envio = pedidos.total, envio.costo_envio

    def test_sin_descuento_bajo_10(self):
        self.assertAlmostEqual(self.total([(10.0, 9)]), 90.0, places=2)

    def test_5_por_ciento_desde_10(self):
        self.assertAlmostEqual(self.total([(10.0, 10)]), 95.0, places=2)

    def test_10_por_ciento_desde_50_no_acumula(self):
        self.assertAlmostEqual(self.total([(2.0, 50)]), 90.0, places=2)

    def test_por_linea(self):
        self.assertAlmostEqual(self.total([(1.0, 6), (1.0, 6)]), 12.0, places=2)
        self.assertAlmostEqual(self.total([(1.0, 10), (1.0, 1)]), 10.5, places=2)

    def test_vacio(self):
        self.assertEqual(self.total([]), 0)

    def test_envio_no_cambia(self):
        self.assertEqual(self.envio(99), 10)
        self.assertEqual(self.envio(100), 0)


if __name__ == "__main__":
    r = unittest.main(exit=False, verbosity=0).result
    print("OCULTOS_OK" if r.wasSuccessful() else f"OCULTOS_FALLA {len(r.failures) + len(r.errors)}")
