import unittest

from envio import costo_envio
from pedidos import total


class PedidosTest(unittest.TestCase):
    def test_total_simple(self):
        self.assertEqual(total([(2.0, 3), (1.5, 2)]), 9.0)

    def test_envio(self):
        self.assertEqual(costo_envio(99), 10)
        self.assertEqual(costo_envio(100), 0)


if __name__ == "__main__":
    unittest.main()
