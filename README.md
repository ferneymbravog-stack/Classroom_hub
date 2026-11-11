# ClassroomHub 🎓

**ClassroomHub** es una aplicación web desarrollada con **Django** y persistencia relacional en **MySQL / MariaDB** para la gestión y consulta de recursos de aprendizaje. Este proyecto evolucionó del Laboratorio 6 (datos estáticos en memoria) al Laboratorio 7 incorporando modelos de datos, migraciones, relaciones relacionales 1:N, panel de administración Django y pruebas automatizadas sobre una base de datos aislada.

---

## 🚀 Características

- **Persistencia en MySQL / MariaDB:** Conexión mediante `django.db.backends.mysql` y el controlador `mysqlclient`.
- **Configuración segura con `.env`:** Separación de credenciales usando `python-dotenv` y plantilla segura `.env.example`.
- **Modelos y relaciones (1:N):**
  - `Category`: Categoría de aprendizaje con nombre único.
  - `Resource`: Recurso con título, descripción, disponibilidad, tipo y relación protegida (`on_delete=models.PROTECT`).
- **Evolución con migraciones:** Migración inicial (`0001_initial.py`) y adición del campo `resource_type` (`0002_resource_resource_type.py`) sin pérdida de datos.
- **Django Admin integrado:** Panel en `/admin/` con filtros, barras de búsqueda y optimización `select_related`.
- **Vistas dinámicas del ORM:** `/resources/` consulta registros reales mediante el ORM y `/resources/available/` permite consultar solo los disponibles.
- **Suite de pruebas aislada:** 11 pruebas automatizadas (`TestCase`) que operan en la base descartable `test_classroom_hub`.

---

## 🛠️ Tecnologías utilizadas

- **Python 3.15**
- **Django 6.1.3**
- **MariaDB 10.11+ / MySQL 8.0+**
- **mysqlclient 2.3.0**
- **python-dotenv 1.2.4**
- **HTML5 & CSS3**

---

## 📂 Estructura del proyecto

```text
classroom-hub/
├── config/                 # Configuración principal del proyecto
│   ├── settings.py         # Ajustes globales y base de datos MySQL
│   ├── urls.py             # Enrutamiento raíz y panel /admin/
│   └── wsgi.py
├── pages/                  # Aplicación de páginas y modelos
│   ├── migrations/         # Migraciones versionadas (0001, 0002)
│   ├── templates/pages/    # Plantillas HTML
│   │   ├── base.html       # Estructura común y navegación
│   │   ├── home.html       # Página de inicio
│   │   ├── resources.html  # Catálogo persistente de recursos
│   │   └── about.html      # Información del proyecto
│   ├── admin.py            # Registro de modelos en Django Admin
│   ├── models.py           # Modelos Category y Resource
│   ├── tests.py            # Suite de 11 pruebas TestCase
│   ├── urls.py             # Rutas propias de la app
│   └── views.py            # Vistas conectadas al ORM
├── manage.py               # Utilidad de administración de Django
├── .env.example            # Plantilla de variables de entorno
├── .gitignore              # Excluye .env, .venv, pycache
└── requirements.txt        # Dependencias del proyecto
```

---

## 💻 Instalación y ejecución local

1. **Clonar el repositorio:**
   ```bash
   git clone git@github.com:ferneymbravog-stack/Classroom_hub.git
   cd Classroom_hub/classroom-hub
   ```

2. **Crear y activar el entorno virtual:**
   ```bash
   python -m venv .venv
   # En Windows:
   .\.venv\Scripts\Activate.ps1
   # En Linux / macOS:
   source .venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la base de datos MySQL / MariaDB:**
   Desde el cliente de base de datos (`mysql -u root`):
   ```sql
   CREATE DATABASE IF NOT EXISTS classroom_hub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER IF NOT EXISTS 'classroomhub_user'@'127.0.0.1' IDENTIFIED BY 'tu_clave_privada';
   GRANT ALL PRIVILEGES ON classroom_hub.* TO 'classroomhub_user'@'127.0.0.1';
   GRANT ALL PRIVILEGES ON test_classroom_hub.* TO 'classroomhub_user'@'127.0.0.1';
   FLUSH PRIVILEGES;
   ```

5. **Configurar el archivo `.env`:**
   Copia la plantilla:
   ```bash
   cp .env.example .env
   ```
   Edita `.env` con tus credenciales:
   ```ini
   DB_NAME=classroom_hub
   DB_USER=classroomhub_user
   DB_PASSWORD=tu_clave_privada
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```

6. **Ejecutar las migraciones:**
   ```bash
   python manage.py migrate
   ```

7. **Crear superusuario para Django Admin:**
   ```bash
   python manage.py createsuperuser
   ```

8. **Iniciar el servidor de desarrollo:**
   ```bash
   python manage.py runserver
   ```
   - Catálogo público: [http://127.0.0.1:8000/resources/](http://127.0.0.1:8000/resources/)
   - Solo disponibles: [http://127.0.0.1:8000/resources/available/](http://127.0.0.1:8000/resources/available/)
   - Panel de administración: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🧪 Pruebas automatizadas

Para ejecutar las 11 pruebas en la base de datos aislada (`test_classroom_hub`):

```bash
python manage.py test pages
```

---

## Laboratorio 9: CRUD protegido de recursos

Los recursos se gestionan desde la interfaz propia de ClassroomHub (sin Django Admin) con `ModelForm`, vistas genéricas y permisos por operación.

### Rutas

```text
GET  /resources/                 (público)
GET  /resources/<pk>/            (público)
GET  /resources/new/             (pages.add_resource)
POST /resources/new/
GET  /resources/<pk>/edit/       (pages.change_resource)
POST /resources/<pk>/edit/
GET  /resources/<pk>/delete/     (confirmación, no elimina)
POST /resources/<pk>/delete/     (pages.delete_resource)
```

### Control de acceso

| Operación | Anónimo | Cuenta común | Catalog reviewers | Catalog editors |
|---|---|---|---|---|
| Ver lista y detalle | Sí | Sí | Sí | Sí |
| Panel personal | No | Sí | Sí | Sí |
| Revisión del catálogo | No | No | Sí | Sí |
| Crear / editar / eliminar | No | No | No | Sí |

Anónimo → redirección al login; autenticado sin permiso → 403.

### Preparar una cuenta editora

1. Entra a `/admin/` con un superusuario y crea algunas **Categories** de ejemplo.
2. Crea el grupo `Catalog editors` (permisos view/add/change/delete de `resource`) desde Admin o con el shell:
   ```python
   from django.contrib.auth.models import Group, Permission
   from django.contrib.contenttypes.models import ContentType
   from pages.models import Resource

   ct = ContentType.objects.get_for_model(Resource)
   codes = ["view_resource", "add_resource", "change_resource", "delete_resource"]
   perms = list(Permission.objects.filter(content_type=ct, codename__in=codes))
   assert len(perms) == len(codes)
   group, _ = Group.objects.get_or_create(name="Catalog editors")
   group.permissions.add(*perms)
   ```
3. Desde Admin asigna el grupo **solo** a una cuenta de demostración.

> **Los permisos nunca se asignan mediante el formulario de registro público**: `/accounts/signup/` crea cuentas sin privilegios. No marques `is_staff` para usar el CRUD.

### Pruebas

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test pages
```

Las pruebas usan la base descartable `test_classroom_hub`. Incluyen las de los laboratorios 7 (modelos/ORM), 8 (autenticación) y 9 (CRUD, permisos, validación y CSRF).

### Organización por laboratorio

Ver `docs/laboratorio-07.md`, `docs/laboratorio-08.md` y `docs/laboratorio-09.md`. Cada laboratorio tiene su commit y su tag (`lab-07`, `lab-08`, `lab-09`).