# Pendientes de la fase 0 (Base)

Fuente: `decisions/0004-plan.md`. Actualizado el 2026-10-09.
Cada punto se cierra con su test en verde o con una prueba documentada.

## Hecho
- [x] El restablecimiento de datos de demostración solo funciona con `DEMO_HABILITADO=true` (por defecto `false`); sin ella la ruta da 404, el comando se niega y el servicio lanza una excepción. Tests: `tests/Feature/DemoTest.php`.

## Bloqueado
- [ ] **Servidor de demostración: agregar `DEMO_HABILITADO=true` a su archivo de entorno.** Bloqueado hasta que el responsable lo agregue; el script de despliegue solo la escribe en archivos nuevos. Al desbloquear, comprobar que el cron aparece en `schedule:list`.

## Por hacer
- [ ] Quitar la copia de alertas a un correo externo (`ALERTA_CORREO_COPIA`): sale de la configuración, `.env.example`, `phpunit.xml` y el script de despliegue.
- [ ] Sin contraseñas por defecto en el código (`config/demo.php`). El administrador inicial se crea por comando con datos del entorno.
- [ ] El script de arranque no siembra datos de demostración en una base vacía.
- [ ] Verificar el arranque real del contenedor (base vacía y con datos, con y sin la variable). El cambio aún no se ha probado en un contenedor.
- [ ] Migrar la base E2E antes de las pruebas: el servidor web de Playwright arranca antes de reiniciar la base, así que en una base nueva `/login` da 500 y Playwright se agota a los 60 s.
- [ ] CI con tests, E2E, `composer audit` y `npm audit`. Depende del punto anterior.
- [ ] Backups diarios fuera del servidor y una restauración probada y documentada.
- [ ] Archivo de entorno del servidor con permisos 600. El gestor de secretos queda aplazado.
