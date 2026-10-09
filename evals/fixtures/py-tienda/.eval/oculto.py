"""Tests ocultos del eval de cupones. Imprime OCULTOS_OK o OCULTOS_FALLA n."""
import os
import sys
import unittest

sys.path.insert(0, os.getcwd())


class Ocultos(unittest.TestCase):
    def co(self, items, cupon=None):
        from checkout import checkout
        r = checkout(items, cupon) if cupon is not None else checkout(items)
        return {k: round(float(r[k]), 2) for k in ("subtotal", "descuento_cupon", "envio", "total")}

    def test_sin_cupon(self):
        self.assertEqual(self.co([(20.0, 2)]), {"subtotal": 40.0, "descuento_cupon": 0.0, "envio": 10.0, "total": 50.0})

    def test_cupon_valido_envio_sobre_total_previo(self):
        self.assertEqual(self.co([(50.0, 2)], "BIENVENIDA"),
                         {"subtotal": 100.0, "descuento_cupon": 15.0, "envio": 0.0, "total": 85.0})

    def test_minimo_no_alcanzado(self):
        self.assertEqual(self.co([(20.0, 2)], "BIENVENIDA"),
                         {"subtotal": 40.0, "descuento_cupon": 0.0, "envio": 10.0, "total": 50.0})

    def test_cupon_sobre_total_con_volumen(self):
        self.assertEqual(self.co([(10.0, 10)], "BIENVENIDA"),
                         {"subtotal": 95.0, "descuento_cupon": 14.25, "envio": 10.0, "total": 90.75})

    def test_modulos_existentes_no_cambian(self):
        from envio import costo_envio
        from pedidos import total
        self.assertEqual((costo_envio(99), costo_envio(100)), (10, 0))
        self.assertAlmostEqual(total([(2.0, 50)]), 90.0)


if __name__ == "__main__":
    r = unittest.main(exit=False, verbosity=0).result
    print("OCULTOS_OK" if r.wasSuccessful() else f"OCULTOS_FALLA {len(r.failures) + len(r.errors)}")
