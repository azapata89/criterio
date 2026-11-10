# La base de criterio existe pero nunca se decidió si va al repo (sin commit, sin ignorar).
mkdir -p docs/knowledge/decisions docs/knowledge/learnings docs/knowledge/research
printf '# Base de conocimiento del proyecto\n\n## Stack\n- Vue 3\n\n## Notas\n<!-- kb:auto:start -->\n<!-- kb:auto:end -->\n' > docs/knowledge/INDEX.md
printf '# Pendientes\n\n## Ahora\n\n## Siguiente\n- [ ] Agregar paginación al listado\n\n## Bloqueadas\n\n## Hecho\n' > docs/knowledge/PENDIENTES.md
