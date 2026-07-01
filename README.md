# Backend — Sistema de Gestión de Licencias de Conducir

API REST desarrollada con Django y Django REST Framework que digitaliza y optimiza el proceso de obtención de la licencia de conducir. El sistema permite a un ciudadano registrar su trámite, subir los documentos requeridos en cada paso, y le recomienda la sucursal más conveniente según su zona de residencia, la distancia y la afluencia histórica de personas, ayudando a reducir los tiempos de espera.

---

## 📌 ¿Qué hace el sistema?

El backend expone una API que permite:

- **Registrar y validar trámites de licencia** mediante el número de cédula (con validación de formato y de código de provincia).
- **Gestionar el trámite por pasos**: carga de cédula, examen de sangre, examen psicosensométrico y confirmación de pago.
- **Administrar sucursales y zonas geográficas** (latitud/longitud) sobre las cuales se calculan distancias.
- **Monitorear la afluencia** (tiempo de espera promedio) de cada sucursal según el día y la hora.
- **Recomendar la sucursal óptima** para un trámite, combinando el tiempo de viaje estimado (a partir de la distancia con la fórmula de Haversine) y el tiempo de espera histórico, devolviendo además el ahorro de tiempo estimado frente a la peor opción.
- **Calcular el top 3 de sucursales con mayor afluencia** en un día/hora determinados.
- **Autenticación de usuarios mediante JWT** (login y refresh token).

Está pensado como el backend de una aplicación que ayuda a los ciudadanos a elegir, de forma inteligente, dónde y cuándo realizar su trámite de licencia para evitar largas esperas.

---

## 🧠 Core del proyecto

El núcleo funcional del sistema es el módulo **`gestion_licencias`**, organizado en capas para separar responsabilidades:

```bash
gestion_licencias/
├── models.py                      # Entidades del dominio (Sucursal, Zona, TramiteLicencia, AfluenciaHistorica)
├── serializers.py                 # Validación y transformación de datos (DRF)
├── views.py                       # ViewSets / Endpoints HTTP
├── repositories/
│   └── sucursal_repository.py     # Acceso a datos (capa de persistencia)
├── services/
│   ├── monitoreo_service.py       # Lógica de monitoreo de afluencia
│   └── recomendacion_service.py   # Lógica de recomendación de sucursal
├── strategies/
│   ├── base.py                    # Contrato de estrategia de recomendación
│   └── estrategia_default.py      # Estrategia concreta (score = tiempo de viaje + espera)
└── factories/
    └── recomendacion_factory.py   # Construcción de la estrategia a usar
```

El corazón del sistema es el motor de recomendación: Dado un trámite (con su zona) y un día/hora, calcula para cada sucursal la distancia geográfica, el tiempo de viaje estimado y el tiempo de espera histórico, los combina en un score mediante una estrategia intercambiable, y devuelve la sucursal con el mejor puntaje.

---

## 🏗️ Patrones de diseño aplicados

| Patrón | Dónde se aplica | Propósito |
|---|---|---|
| **Repository** | `repositories/sucursal_repository.py` | Encapsula el acceso a los datos de `Sucursal` y `AfluenciaHistorica`, desacoplando al `RecomendacionService` del ORM de Django. |
| **Service Layer** | `services/monitoreo_service.py`, `services/recomendacion_service.py` | Concentra la lógica de negocio fuera de las vistas, dejando a los `ViewSet` enfocados solo en manejar peticiones/respuestas HTTP. |
| **Strategy** | `strategies/base.py`, `strategies/estrategia_default.py` | Encapsula el algoritmo de cálculo del *score* de recomendación (`calcular_score`) detrás de una interfaz común, permitiendo agregar nuevas estrategias (por ejemplo, priorizar espera sobre distancia) sin tocar el servicio que las usa. |
| **Factory Method** | `factories/recomendacion_factory.py` | Centraliza la creación de la estrategia de recomendación adecuada, evitando que el servicio dependa de una clase concreta (`EstrategiaDefault`) y facilitando agregar nuevas estrategias en el futuro. |

---

## 🧱 Principios SOLID aplicados

- **S — Single Responsibility Principle**
  Cada clase tiene una única razón para cambiar: `SucursalRepository` solo accede a datos, `MonitoreoService` solo calcula el estado de afluencia, `RecomendacionService` solo orquesta la recomendación, y los `ViewSet` solo traducen HTTP ↔ lógica de negocio.

- **O — Open/Closed Principle**
  El sistema de recomendación está abierto a extensión y cerrado a modificación: se pueden agregar nuevas estrategias de cálculo (`RecommendationStrategy`) sin modificar `RecomendacionService`, simplemente registrándolas en `RecomendacionFactory`.

- **L — Liskov Substitution Principle**
  Cualquier subclase de `RecommendationStrategy` (como `EstrategiaDefault`) puede sustituir a la clase base sin alterar el comportamiento esperado por `RecomendacionService`, ya que todas implementan el mismo contrato `calcular_score(tiempo_viaje, espera)`.

- **I — Interface Segregation Principle**
  La interfaz `RecommendationStrategy` define únicamente el método que las estrategias concretas necesitan implementar (`calcular_score`), evitando forzar a las clases a depender de métodos que no usan.

- **D — Dependency Inversion Principle**
  `RecomendacionService` no depende directamente del ORM (`Sucursal.objects`, `AfluenciaHistorica.objects`) ni de una estrategia concreta, depende de abstracciones: el `SucursalRepository` para el acceso a datos y la estrategia entregada por `RecomendacionFactory`. Esto desacopla la lógica de negocio de los detalles de implementación.

---

## 🛠️ Tecnologías utilizadas

- **Python 3.11**
- **Django 5.x** + **Django REST Framework**
- **Simple JWT** (autenticación por tokens)
- **django-cors-headers** (manejo de CORS)
- **PostgreSQL** en producción (vía `psycopg2-binary` y `dj-database-url`) / **SQLite** en desarrollo local
- **Gunicorn** (servidor WSGI de producción)
- **WhiteNoise** (servir archivos estáticos en producción)
- **Pillow** (manejo de archivos/imágenes)

---

## 🚀 Instalación y ejecución local 

### 1. Clonar el repositorio


https://github.com/DavidPuga04/backproyectolic.git


### 2. Crear y activar un entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo de ejemplo y completa los valores:

```bash
cp .env.example .env
```

Para desarrollo local basta con dejar `DATABASE_URL` vacío (se usará SQLite automáticamente):

```env
SECRET_KEY=tu_clave_secreta
DEBUG=True
ALLOWED_HOSTS=*
DATABASE_URL=
```

### 5. Aplicar las migraciones

```bash
python manage.py migrate
```

### 6. Poblar la base de datos con datos de prueba

```bash
python poblar_datos.py
```

### 7. Crear un superusuario (para acceder al panel de administración)

```bash
python manage.py createsuperuser
```

### 8. Levantar el servidor de desarrollo
```bash
python manage.py runserver
```

La API quedará disponible en `http://127.0.0.1:8000/`.

---

## 🔗 Endpoints principales

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/login/` | Autenticación, obtención de token JWT |
| `POST` | `/api/token/refresh/` | Refrescar token de acceso |
| `GET / POST` | `/api/tramites/` | Listar / crear trámites de licencia |
| `GET / PUT / DELETE` | `/api/tramites/{id}/` | Detalle, actualizar o eliminar un trámite |
| `POST` | `/api/tramites/validar_cedula/` | Validar formato de cédula |
| `GET` | `/api/tramites/listar_monitoreo/` | Estado de afluencia de todas las sucursales |
| `GET` | `/api/tramites/{id}/recomendar_sucursal/?dia=&hora=` | Recomendación de la mejor sucursal para un trámite |
| `GET` | `/api/tramites/top_sucursales_afluencia/?dia=&hora=` | Top 3 sucursales con mayor afluencia |
| `GET / POST` | `/api/zonas/` | Listar / crear zonas geográficas |
| `GET` | `/admin/` | Panel de administración de Django |

---

## ☁️ Despliegue

Esta parte es el backend del proyecto y se encuentra deployado en Render

🔗 Link del delploy: https://backproyectolic.onrender.com

---

## 🎥 Video explicativo

🔗 Video en YouTube: https://youtu.be/2HbLpgHYXms

---

## ✍️ Autor

*David Puga* /
 david.puga@udla.edu.ec
