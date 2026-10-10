import unittest

from envio import costo_envio


class EnvioTest(unittest.TestCase):
    def test_envio(self):
        self.assertEqual(costo_envio(99), 10)
        self.assertEqual(costo_envio(100), 0)


if __name__ == "__main__":
    unittest.main()
