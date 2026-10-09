---
name: lente-db
description: Checklist de base de datos (migraciones seguras, índices, N+1, transacciones) con docs oficiales de PostgreSQL, MySQL, Laravel y Django. Úsala antes de crear o modificar migraciones, esquemas, archivos SQL, modelos/ORM o consultas, o cuando haya consultas lentas.
---

# Lente: base de datos

## Cómo usarla
1. Busca en `docs/knowledge/INDEX.md` las notas con área `db`.
2. Identifica el motor y su versión en la configuración o en el lockfile. Las reglas de bloqueo cambian entre PostgreSQL y MySQL, y entre versiones.
3. Aplica solo los puntos que afectan al cambio. Reporta cada uno como **verificado**, con evidencia, o como **riesgo**, con qué falta.

## Checklist, ordenada por costo del error
1. **Reversible y probada:** la migración tiene `down` o reversa, y se probó sobre una copia con volumen real antes de llegar a producción.
2. **Índices sin bloquear:** en PostgreSQL, sobre tablas grandes, usar `CREATE INDEX CONCURRENTLY` fuera de una transacción. En Django eso es `AddIndexConcurrently` con `atomic = False`.
3. **ALTER TABLE en tablas calientes:** evitar operaciones que toman `ACCESS EXCLUSIVE` y reescriben la tabla. Los constraints se agregan con `NOT VALID` y se validan después. Fijar `lock_timeout`.
4. **MySQL:** comprobar el `ALGORITHM` (INSTANT/INPLACE/COPY) y el `LOCK` de cada DDL.
5. **Cambios incompatibles en pasos:** expandir, migrar los datos y después contraer. Por ejemplo, renombrar o borrar una columna en dos deploys.
6. **N+1:**
   - Laravel: `Model::preventLazyLoading(! app()->isProduction())`.
   - Django: `select_related`/`prefetch_related`.
   - Contar queries en los tests (`assertNumQueries`).
7. **EXPLAIN:** pasar `EXPLAIN (ANALYZE, BUFFERS)` por las queries nuevas o lentas. Un Seq Scan sobre una tabla grande con un filtro selectivo pide un índice.
8. **Transacciones:** las escrituras en varias tablas van dentro de `DB::transaction` o `transaction.atomic`, sin llamadas HTTP dentro.
9. **Queries lentas visibles:** `DB::whenQueryingForLongerThan`/`DB::listen` en Laravel; Debug Toolbar o Silk en Django.

## Fuentes (verificadas 2026-10-09)
- PostgreSQL: [ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html), [CREATE INDEX (concurrently)](https://www.postgresql.org/docs/current/sql-createindex.html), [locking](https://www.postgresql.org/docs/current/explicit-locking.html), [EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html), [isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- MySQL 8.4: [EXPLAIN](https://dev.mysql.com/doc/refman/8.4/en/explain.html), [online DDL](https://dev.mysql.com/doc/refman/8.4/en/innodb-online-ddl-operations.html)
- Laravel: [migrations](https://laravel.com/docs/migrations), [relationships / preventLazyLoading](https://laravel.com/docs/eloquent-relationships), [database](https://laravel.com/docs/database)
- Django: [migrations](https://docs.djangoproject.com/en/stable/topics/migrations/), [writing migrations](https://docs.djangoproject.com/en/stable/howto/writing-migrations/), [optimization](https://docs.djangoproject.com/en/stable/topics/db/optimization/), [transactions](https://docs.djangoproject.com/en/stable/topics/db/transactions/)
- Práctica de referencia: [strong_migrations](https://github.com/ankane/strong_migrations) · Herramientas: [laravel-debugbar](https://github.com/fruitcake/laravel-debugbar), [django-debug-toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/), [django-silk](https://github.com/jazzband/django-silk)
