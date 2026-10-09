---
name: lente-qa
description: Checklist de calidad de tests (comportamiento sobre implementación, regresión de bugs, flaky, E2E) con docs oficiales de pytest, Vitest, PHPUnit/Pest, Laravel, Django y Playwright. Úsala antes de escribir o modificar tests, al corregir un bug, o cuando un test falle de forma intermitente.
---

# Lente: QA

## Cómo usarla
1. Busca en `docs/knowledge/INDEX.md` las notas con área `qa`, como convenciones de tests o comandos.
2. Usa el runner y las convenciones que ya tiene el proyecto. No introduzcas otro framework de tests.
3. Aplica solo los puntos que afectan al cambio. Al final reporta el comando que corriste y su resultado.

## Checklist, ordenada por costo del error
1. **Regresión:** cada bug corregido lleva un test que falla sin el fix y pasa con él. Comprueba las dos cosas: primero sin el fix, después con él.
2. **Comportamiento observable:** los asserts van sobre la respuesta HTTP, el estado en la DB o el DOM visible, no sobre llamadas internas ni métodos privados.
3. **Mocks solo en fronteras externas** (red, reloj, pagos). La DB se prueba real, con `RefreshDatabase` o fixtures transaccionales.
4. **Aislamiento:** cada test corre solo y en cualquier orden. Sin estado compartido y sin depender de la hora ni de la zona horaria.
5. **E2E:** locators por rol o por texto visible, y aserciones web-first con auto-wait. Nada de `sleep` fijos.
6. **Flaky:** se pone en cuarentena y se arregla la causa. No se suben los reintentos para taparlo.
7. **Más allá del happy path:** cubrir errores y límites, como vacío, máximo o sin permiso.
8. **Velocidad:** los unit tests tardan segundos; E2E solo para los flujos críticos.

## Fuentes (verificadas 2026-10-09)
- pytest: [good practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html), [flaky](https://docs.pytest.org/en/stable/explanation/flaky.html), [fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [Vitest guide](https://vitest.dev/guide/) · [PHPUnit](https://docs.phpunit.de/) · [Pest](https://pestphp.com/docs/writing-tests)
- Laravel: [testing](https://laravel.com/docs/testing), [HTTP tests](https://laravel.com/docs/http-tests), [database testing](https://laravel.com/docs/database-testing) · Django: [testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- Playwright: [best practices](https://playwright.dev/docs/best-practices), [retries](https://playwright.dev/docs/test-retries) · [Testing Library: guiding principles](https://testing-library.com/docs/guiding-principles/)
- [Google Testing Blog: flaky tests](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)
