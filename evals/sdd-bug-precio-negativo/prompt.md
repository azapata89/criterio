---
tags: [sdd, bug]
plugins: ["eval-hooks"]
max_turns: 30
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write, Bash]
---

Bug: `formatearPrecio(-1500)` devuelve '$ -1.500' y debería devolver '-$ 1.500'. Corrígelo.
