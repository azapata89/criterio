---
name: lente-qa
description: Calidad y estrategia de pruebas: radio de impacto mientras trabajas y suite completa antes de cerrar o hacer push; tests de comportamiento, regresión de bugs, flaky y E2E, con docs oficiales de pytest, Vitest, PHPUnit/Pest, Laravel, Django y Playwright. Úsala antes de escribir, modificar o correr tests, al corregir un bug, o cuando un test falle de forma intermitente.
---

# Lente: QA

## Cómo usarla
1. Busca en `docs/knowledge/INDEX.md` las notas con área `qa`, como convenciones de tests o comandos.
2. Usa el runner y las convenciones que ya tiene el proyecto. No introduzcas otro framework de tests.
3. Aplica solo los puntos que afectan al cambio. Al final reporta el comando que corriste y su resultado.

## Pruebas por radio de impacto
- **Mientras trabajas:** corre solo las pruebas de lo que tocaste y de lo que depende de ello (el módulo, su CRUD, sus pantallas). Son rápidas y dan retroalimentación inmediata.
- **Antes de cerrar la tarea o de hacer push:** corre **una vez** la suite completa, aunque sea lenta. Ninguna deducción del tipo «esto no debería afectar» reemplaza correrla. Si de verdad no se puede correr, decláralo como sin verificar.
- **Pruebas que dependen del entorno** (fuentes, capturas, anchos, zona horaria): córrelas en el mismo sistema que el CI, por ejemplo con la imagen Docker de Playwright, no solo en local.
- Agrupa los push: un commit por tarea y un push por bloque de tareas, con la suite completa verde antes del push.

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
