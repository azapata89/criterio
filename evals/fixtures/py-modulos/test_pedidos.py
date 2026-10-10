import unittest

from pedidos import total


class PedidosTest(unittest.TestCase):
    def test_total(self):
        self.assertEqual(total([(2.0, 3), (1.5, 2)]), 9.0)


if __name__ == "__main__":
    unittest.main()
