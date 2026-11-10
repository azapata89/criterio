---
name: lente-ml
description: Oportunidades de machine learning e IA (modelos predictivos, LLM, agentes, automatización): decide si vale la pena con evidencia del repo (dato, etiqueta, línea base sin ML, costo del error, privacidad y sesgo), con fuentes oficiales de Google, scikit-learn, NIST, OMS y Anthropic. Úsala cuando pidan buscar, evaluar o priorizar usos de ML/IA en un sistema, o antes de proponer un modelo, un LLM o un agente.
---

# Lente: ML e IA

## Cómo usarla
1. Busca en `docs/knowledge/INDEX.md` las notas con área `producto`, `db` o `security`.
2. Primero mapea qué datos guarda el sistema: esquema, migraciones, modelos ORM y eventos. No propongas nada antes de saber qué existe.
3. Cada oportunidad se respalda con un archivo o tabla del repo. Las ideas típicas del sector («predecir X», «chatbot») sin evidencia en el repo son hipótesis y se presentan así.
4. Al final entrega una tabla priorizada: oportunidad, dato que la sostiene (con ruta), etiqueta, línea base, costo del error, riesgo y **siguiente paso concreto**. Si falta el dato, el siguiente paso es empezar a registrarlo, no entrenar.

## Datos reales
- **No abras exports, dumps ni CSV de producción** con datos de personas, aunque estén en el repo. El esquema y el código bastan para evaluar la factibilidad. Si hace falta ver datos, pide una muestra anonimizada o sintética.
- Los datos de salud son sensibles: en Colombia, por el art. 5 de la Ley 1581 de 2012, y en otros países, por normas equivalentes. Para cada oportunidad, indica qué dato sensible usa y si debe salir del sistema, por ejemplo hacia una API de LLM.

## Checklist, ordenada por costo del error
1. **¿Existe la etiqueta?** Para predecir algo, el sistema debe registrar el resultado que se quiere predecir (por ejemplo, si el paciente asistió). Si no lo registra, no hay modelo posible: primero se instrumenta y se acumula historia.
2. **¿Se comporta igual sin ML?** Antes de un modelo, mide el problema y prueba una regla simple. Un modelo solo se justifica si supera a esa línea base en una métrica acordada.
3. **Costo del error y quién lo paga:** no es lo mismo un recordatorio de más que priorizar o negar una atención. Si la salida influye en decisiones clínicas, puede ser software de uso médico, con exigencias regulatorias. Debe haber una persona que decida.
4. **Sesgo:** ¿la decisión perjudica a un grupo, como por edad, zona o tipo de afiliación? Por ejemplo, el sobreagendamiento por riesgo de inasistencia puede castigar a los pacientes con más barreras de acceso. Mide la métrica por grupo, no solo la global.
5. **Fuga de datos (leakage):** una variable que no existe en el momento de predecir infla la métrica y luego falla en producción. Para cada variable candidata, busca en el código **dónde y cuándo se escribe** (INSERT/UPDATE, jobs, eventos) y compáralo con el momento de la predicción. Nombra explícitamente las que quedan descartadas por eso. Desconfía de lo que se registra en el mismo evento que la etiqueta, como un pago o un check-in.
6. **LLM y agentes:** la solución más simple primero (un prompt con buenos datos, antes que un agente). Define cómo se evalúa la calidad antes de construir, y qué datos se envían al proveedor.
7. **Volumen y frecuencia:** ¿hay suficientes casos y se repite la decisión lo bastante para que valga la pena automatizarla?
8. **Operación:** quién reentrena, cómo se monitorea la deriva y qué pasa si el modelo falla (siempre hay un comportamiento por defecto sin ML).

## Fuentes (verificadas 2026-11-10)
- Google, [Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml): regla 1, «Don't be afraid to launch a product without machine learning»; regla 2, «First, design and implement metrics».
- scikit-learn, [Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html): fuga de datos.
- Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents): «finding the simplest solution possible, and only increasing complexity when needed».
- NIST, [AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) (Govern, Map, Measure, Manage) y su perfil de IA generativa NIST-AI-600-1.
- OMS, [Ethics and governance of artificial intelligence for health](https://www.who.int/publications/i/item/9789240029200) (2021).
- [Fairlearn](https://fairlearn.org/): evaluación y mitigación de sesgo.
- FDA, [Clinical Decision Support Software](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software) (enero de 2026): cuándo el software de apoyo clínico es dispositivo médico.
- [Ley 1581 de 2012](https://normas.cra.gov.co/Gestor/Docs/ley_1581_2012.htm), art. 5: datos relativos a la salud como datos sensibles.
