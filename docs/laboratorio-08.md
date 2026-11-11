# Laboratorio 8 — Autenticación, sesiones y permisos

**Archivos:** vistas `signup`, `dashboard`, `resource_review` en `pages/views.py`; rutas `accounts/*`, `dashboard/`, `resources/review/`; plantillas `signup.html`, `login.html`, `dashboard.html`, `review.html`; menú sensible a sesión en `base.html`.

- Registro con `UserCreationForm` (cuentas sin privilegios).
- Login/logout (logout por POST), contador de visitas en sesión.
- Revisión protegida con `pages.view_resource` (grupo `Catalog reviewers`).
- Pruebas (clase `AuthenticationTests`, 18).