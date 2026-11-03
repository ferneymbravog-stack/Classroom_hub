# ClassroomHub 🎓

**ClassroomHub** es una aplicación web desarrollada con **Django** orientada a la gestión y consulta de recursos de aprendizaje. Este proyecto pone en práctica la arquitectura modular de Django, el enrutamiento de URLs a nivel de proyecto y de aplicación, vistas basadas en funciones, herencia de plantillas HTML y pruebas automatizadas.

---

## 🚀 Características

- **Enrutamiento modular:** Separación clara entre las rutas principales (`config/urls.py`) y las rutas de la aplicación (`pages/urls.py`) mediante `include()`.
- **Vistas dinámicas:** Contextos enviados desde las funciones de vista hacia las plantillas (`home`, `resources`, `about`).
- **Diseño limpio y moderno:** Interfaz basada en tarjetas (*Card UI*), responsiva y estilizada con CSS nativo.
- **Herencia de plantillas:** Uso de `base.html` con bloques reutilizables (`{% block content %}`, `{% block title %}`) y navegación persistente.
- **Suite de pruebas:** Tests unitarios automatizados que verifican códigos de estado HTTP, plantillas renderizadas y resolución de rutas 404.

---

## 🛠️ Tecnologías utilizadas

- **Python 3.12+**
- **Django 6.1+**
- **HTML5 & CSS3**
- **SQLite3**

---

## 📂 Estructura del proyecto

```text
classroom-hub/
├── config/                 # Configuración principal del proyecto
│   ├── settings.py         # Ajustes globales y aplicaciones instaladas
│   ├── urls.py             # Enrutamiento raíz
│   └── wsgi.py
├── pages/                  # Aplicación de páginas estáticas y dinámicas
│   ├── templates/pages/    # Plantillas HTML
│   │   ├── base.html       # Estructura común y navegación
│   │   ├── home.html       # Página de inicio
│   │   ├── resources.html  # Catálogo de recursos
│   │   └── about.html      # Información del proyecto
│   ├── tests.py            # Pruebas automatizadas
│   ├── urls.py             # Rutas propias de la app
│   └── views.py            # Vistas (home, resources, about)
├── manage.py               # Utilidad de administración de Django
└── requirements.txt        # Dependencias del proyecto
```

---

## 💻 Instalación y ejecución local

1. **Clonar el repositorio:**
   ```bash
   git clone git@github.com:ferneymbravog-stack/Classroom_hub.git
   cd Classroom_hub/classroom-hub
   ```

2. **Crear y activar un entorno virtual:**
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Linux / macOS:
   source .venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar las migraciones:**
   ```bash
   python manage.py migrate
   ```

5. **Iniciar el servidor de desarrollo:**
   ```bash
   python manage.py runserver
   ```
   Accede desde tu navegador en: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🧪 Ejecutar pruebas unitarias

Para verificar el correcto funcionamiento de las vistas y rutas:

```bash
python manage.py test pages
```
