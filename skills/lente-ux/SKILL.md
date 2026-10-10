---
name: lente-ux
description: Checklist de UX y accesibilidad (WCAG 2.2, NN/g, GOV.UK, MDN, Core Web Vitals) con verificación real (axe + Playwright, capturas). Úsala antes de crear o modificar pantallas, formularios, vistas Vue/React/Blade, estilos o flujos de usuario, y cuando el usuario pida revisar usabilidad, accesibilidad o la experiencia en celular.
---

# Lente: UX y accesibilidad

## Cómo usarla
1. **Primero el contexto.** Antes de tocar la pantalla, escribe en 1-3 líneas quién la usa, en qué dispositivo y en qué condiciones: campo o escritorio, señal, sol o guantes, prisa. Busca en `docs/knowledge/INDEX.md` las notas con área `frontend` o `producto`.
2. Aplica solo los puntos que afectan a la pantalla. Reporta cada uno como **verificado**, con su evidencia, o como **sin verificar**.
3. **No afirmes que una pantalla «es accesible» o «se ve bien» sin haberla verificado.** Verificar significa una de estas tres cosas: axe sin violaciones, una captura que revisaste o una prueba manual que describes. La automatización solo detecta una parte de los problemas: Deque reporta 57,38 %, y 0 % en orden y visibilidad del foco.

## Checklist, ordenada por costo del error
**Uso en campo y celular**
1. **No perder datos:**
   - si el envío falla por la red, se conserva lo escrito y lo adjuntado (borrador local en `localStorage` o IndexedDB, o no limpiar el formulario);
   - hay reintento visible;
   - no dependas solo de Background Sync, porque no es Baseline.
2. **Estado del envío:** mostrar que está subiendo, si falló o si llegó, por archivo cuando hay varios.
3. **Foto: decide y justifica.**
   - `capture="environment"` abre la cámara trasera, pero en algunos dispositivos impide elegir de la galería.
   - Permitir la galería deja tomar la foto sin señal y subirla después.
4. **Geolocalización:**
   - se pide tras una acción del usuario y solo funciona en HTTPS;
   - si la deniega, hay un camino alternativo, como escribir la ubicación o continuar sin ella.
5. A 360 px no hay scroll horizontal, y los objetivos táctiles miden al menos 24×24 px (WCAG 2.5.8).

**Accesibilidad (WCAG 2.2 AA)**
6. **Campos:** cada uno tiene `<label>` o nombre accesible. El placeholder no sirve como etiqueta. Los grupos van en `fieldset`/`legend`.
7. **Errores:** se muestran como texto junto al campo y en un resumen, no solo con color, y se anuncian (`role="alert"`, `aria-describedby`, `aria-invalid`).
8. **Teclado y foco:**
   - todo se puede hacer con teclado;
   - el foco se ve y ningún header sticky o toast lo tapa (2.4.11);
   - los modales no atrapan el foco.
9. **Contraste:** texto 4,5:1, y bordes de inputs, íconos y foco 3:1.
10. **Login:** permite pegar la contraseña y usar gestores de contraseñas (3.3.8).

**Usabilidad**
11. **Validación:** se valida al enviar y no al salir del campo. Tras un error del servidor (422) se conservan los datos.
12. **Estados de listas y tablas:** vacía (explica y ofrece la primera acción), cargando y error con reintento. Sin spinner si tarda menos de 1 s, y con progreso si pasa de 10 s.
13. **Acciones destructivas:** piden confirmación o permiten deshacer.
14. **Fechas, números y moneda:** con `Intl` en `es-CO` y `timeZone: "America/Bogota"`, nunca concatenando a mano.

## Verificación, si el proyecto tiene Playwright
- `new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze()` debe dar `violations: []`. Córrelo también con el modal abierto o con el formulario mostrando errores.
- Toma capturas a 360 px y a 1280 px con `page.screenshot()` y **míralas**, porque son imágenes que puedes leer. Antes de tomarlas, escribe qué esperas ver y compáralo.
- Si no hay Playwright ni navegador, dilo: «Sin verificar: render y accesibilidad automática».
- Prueba manual del flujo principal con teclado.

## Contexto Colombia
La Resolución MinTIC 1519 de 2020 (art. 3) exige WCAG 2.1 AA a los sujetos obligados desde el 1-ene-2022. Es relevante si el cliente es una entidad pública.

## Fuentes (verificadas 2026-10-09)
- W3C: [WCAG 2.2](https://www.w3.org/TR/WCAG22/), [qué hay de nuevo](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/), [quick reference](https://www.w3.org/WAI/WCAG22/quickref/), [ARIA APG](https://www.w3.org/WAI/ARIA/apg/)
- NN/g: [10 heurísticas](https://www.nngroup.com/articles/ten-usability-heuristics/), [errores en formularios](https://www.nngroup.com/articles/errors-forms-design-guidelines/), [estados vacíos](https://www.nngroup.com/articles/empty-state-interface-design/), [indicadores de progreso](https://www.nngroup.com/articles/progress-indicators/)
- GOV.UK: [mensajes de error](https://design-system.service.gov.uk/components/error-message/), [validación](https://design-system.service.gov.uk/patterns/validation/)
- MDN: [capture](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/capture), [Geolocation](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API), [Background Sync](https://developer.mozilla.org/en-US/docs/Web/API/Background_Synchronization_API), [Intl.DateTimeFormat](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat) · web.dev: [offline cookbook](https://web.dev/articles/offline-cookbook), [Core Web Vitals](https://web.dev/articles/vitals)
- Verificación: [Playwright accessibility testing](https://playwright.dev/docs/accessibility-testing), [visual comparisons](https://playwright.dev/docs/test-snapshots), [Deque: cobertura automática 57,38 %](https://www.deque.com/automated-accessibility-coverage-report/)
- Colombia: [Resolución MinTIC 1519 de 2020](https://normograma.mintic.gov.co/mintic/compilacion/docs/resolucion_mintic_1519_2020.htm)
