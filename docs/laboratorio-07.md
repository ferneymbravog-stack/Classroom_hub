# Laboratorio 7 — Modelos, migraciones y MySQL/MariaDB

**Archivos:** `pages/models.py`, `pages/migrations/0001_initial.py`, `pages/migrations/0002_resource_resource_type.py`, `pages/admin.py`, `config/settings.py` (MySQL + `.env`), `pages/templates/pages/resources.html`, `DB.sql`, `.env.example`.

- Modelos `Category` y `Resource` (relación 1:N con `on_delete=PROTECT`).
- Campo `resource_type` añadido por segunda migración.
- Django Admin con filtros y búsqueda.
- Vistas `/resources/` y `/resources/available/` conectadas al ORM.
- Pruebas (clase `ClassroomHubTests`, 11) sobre `test_classroom_hub`.