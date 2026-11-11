# Laboratorio 9 — Formularios y CRUD con Django

**Archivos:** `pages/forms.py` (`ResourceForm`), vistas `ResourceDetailView/CreateView/UpdateView/DeleteView`, rutas `resources/new/`, `<pk>/`, `<pk>/edit/`, `<pk>/delete/`, plantillas `resource_detail.html`, `resource_form.html`, `resource_confirm_delete.html`, enlaces en `resources.html` y `base.html`.

- `ModelForm` con campos explícitos y `clean_title` (mínimo 3 caracteres).
- Permisos por operación: `add_resource`, `change_resource`, `delete_resource` (grupo `Catalog editors`).
- Eliminación: GET confirma, POST elimina (CSRF activo).
- Pruebas (clase `ResourceCrudTests`) de permisos, validación, 404 y CSRF.

Respuestas a las preguntas de la sección 13: ver README y el código; la validación vive en el formulario, la decisión de operación en la vista y la autorización en los mixins.