import unittest

from envio import costo_envio
from pedidos import total


class TiendaTest(unittest.TestCase):
    def test_total_con_volumen(self):
        self.assertAlmostEqual(total([(10.0, 10)]), 95.0)

    def test_envio(self):
        self.assertEqual(costo_envio(99), 10)
        self.assertEqual(costo_envio(100), 0)


if __name__ == "__main__":
    unittest.main()
