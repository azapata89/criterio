---
name: lente-seguridad
description: Checklist de seguridad con fuentes OWASP y docs oficiales. Úsala antes de modificar autenticación, autorización, sesiones, rutas o controladores que reciben input del usuario, uploads, manejo de secretos o .env, o cuando el usuario pida una revisión de seguridad.
---

# Lente: seguridad

## Cómo usarla
1. Busca en `docs/knowledge/INDEX.md` las notas con área `security` y léelas si tocan este cambio.
2. Aplica solo los puntos que afectan al cambio actual. No recorras la lista entera por rutina.
3. Para cada punto aplicado, reporta su estado:
   - **verificado**, con evidencia `archivo:línea`, comando o test;
   - **riesgo**, con qué falta.
4. Si citas una práctica, enlaza la fuente de abajo. Si el proyecto usa otra versión del framework, consulta la doc de esa versión antes de afirmar.

## Checklist, ordenada por costo del error
1. **Autorización por recurso (IDOR):** cada endpoint o acción comprueba que el usuario es dueño del recurso. Debe haber un test que pida el ID de otro usuario y espere 403/404.
2. **SQL parametrizado:** nada de concatenar input. Revisa `DB::raw`, `whereRaw`, `.raw()`, `.extra()` y `$queryRawUnsafe`.
3. **Validación en servidor con allowlist:** FormRequest, serializers/forms, Pydantic o zod. La validación del cliente no cuenta.
4. **Secretos:** ninguno en el repo ni en el bundle del cliente (`NEXT_PUBLIC_*`, `.env` commiteado). Si alguno se filtró, hay que rotarlo.
5. **Contraseñas:** bcrypt o argon2 del framework. Login y reset con rate limit.
6. **Sesión:** cookies `HttpOnly`, `Secure` y `SameSite`. La sesión se regenera al hacer login.
7. **CSRF** activo en rutas que cambian estado, y cualquier exclusión justificada. En Server Actions de Next, la auth va dentro de cada acción.
8. **Salida sin escapar** con datos del usuario: `v-html`, `{!! !!}`, `dangerouslySetInnerHTML`, `|safe`, `mark_safe`.
9. **Uploads:** tipo validado por contenido y tamaño limitado; renombrar y guardar fuera del webroot.
10. **Dependencias y logs:**
    - Correr `npm audit`/`pnpm audit`, `composer audit` y `pip-audit`, sin vulnerabilidades altas sin revisar.
    - Los logs registran eventos de auth, sin tokens ni PII.

## Fuentes (verificadas 2026-10-09)
- OWASP Cheat Sheets: [Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html), [SQL Injection](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html), [Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html), [Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html), [IDOR](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html), [Session](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html), [Secrets](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html), [CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html), [XSS](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html), [File Upload](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html), [Logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [OWASP ASVS 5.0](https://owasp.org/www-project-application-security-verification-standard/) · [OWASP Top 10:2025](https://top10.owasp.org/2025/)
- Laravel: [validation](https://laravel.com/docs/validation), [authorization](https://laravel.com/docs/authorization), [csrf](https://laravel.com/docs/csrf), [encryption](https://laravel.com/docs/encryption), [hashing](https://laravel.com/docs/hashing)
- Django: [security](https://docs.djangoproject.com/en/stable/topics/security/), [deployment checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/) · FastAPI: [security](https://fastapi.tiangolo.com/tutorial/security/)
- Node: [security best practices](https://nodejs.org/en/learn/getting-started/security-best-practices) · Next.js: [data security](https://nextjs.org/docs/app/guides/data-security), [authentication](https://nextjs.org/docs/app/guides/authentication)
- Auditoría: [npm audit](https://docs.npmjs.com/cli/commands/npm-audit/), [pnpm audit](https://pnpm.io/cli/audit), [composer audit](https://getcomposer.org/doc/03-cli.md#audit), [pip-audit](https://github.com/pypa/pip-audit)
