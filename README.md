# 🚀 API REST - Sistema de Gestión de Tareas

Un servidor API Flask que proporciona funcionalidades de registro de usuarios, autenticación y gestión de tareas con persistencia en SQLite.

## 📋 Características

- ✅ **Registro de Usuarios**: Endpoint POST `/registro` con contraseñas hasheadas
- ✅ **Inicio de Sesión**: Endpoint POST `/login` con verificación de credenciales
- ✅ **Gestión de Tareas**: Endpoint GET `/tareas` con HTML de bienvenida
- ✅ **Base de Datos SQLite**: Persistencia de datos
- ✅ **Seguridad**: Contraseñas hasheadas con bcrypt
- ✅ **Sesiones**: Sistema de autenticación con sesiones

## 🛠️ Instalación

1. **Clonar o descargar el proyecto**
2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Ejecución

```bash
python servidor.py
```

El servidor se ejecutará en `http://localhost:5000`

## 📡 Endpoints Disponibles

### 1. Registro de Usuario
- **URL**: `POST /registro`
- **Descripción**: Registra un nuevo usuario
- **Body**:
  ```json
  {
    "usuario": "nombre_usuario",
    "contraseña": "1234"
  }
  ```
- **Respuesta exitosa** (201):
  ```json
  {
    "mensaje": "Usuario registrado exitosamente"
  }
  ```

### 2. Inicio de Sesión
- **URL**: `POST /login`
- **Descripción**: Inicia sesión con credenciales
- **Body**:
  ```json
  {
    "usuario": "nombre_usuario",
    "contraseña": "1234"
  }
  ```
- **Respuesta exitosa** (200):
  ```json
  {
    "mensaje": "Inicio de sesión exitoso",
    "usuario": "nombre_usuario"
  }
  ```

### 3. Página de Tareas (Bienvenida)
- **URL**: `GET /tareas`
- **Descripción**: Muestra página HTML de bienvenida (requiere autenticación)
- **Respuesta**: Página HTML con información del usuario y características del sistema

### 4. Cerrar Sesión
- **URL**: `GET /logout`
- **Descripción**: Cierra la sesión actual
- **Respuesta** (200):
  ```json
  {
    "mensaje": "Sesión cerrada exitosamente"
  }
  ```

### 5. Información de la API
- **URL**: `GET /`
- **Descripción**: Muestra información general de la API
- **Respuesta**:
  ```json
  {
    "mensaje": "API REST de Gestión de Tareas",
    "endpoints": {
      "registro": "POST /registro - Registrar nuevo usuario",
      "login": "POST /login - Iniciar sesión",
      "tareas": "GET /tareas - Ver página de bienvenida (requiere autenticación)",
      "logout": "GET /logout - Cerrar sesión"
    }
  }
  ```

## 🧪 Pruebas con cURL

### Registrar un usuario:
```bash
curl -X POST http://localhost:5000/registro \
  -H "Content-Type: application/json" \
  -d '{"usuario": "testuser", "contraseña": "1234"}'
```

### Iniciar sesión:
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"usuario": "testuser", "contraseña": "1234"}' \
  -c cookies.txt
```

### Acceder a tareas (con cookies):
```bash
curl -X GET http://localhost:5000/tareas \
  -b cookies.txt
```

### Cerrar sesión:
```bash
curl -X GET http://localhost:5000/logout \
  -b cookies.txt
```

## 🗄️ Base de Datos

El sistema utiliza SQLite con dos tablas principales:

### Tabla `usuarios`:
- `id`: Identificador único
- `usuario`: Nombre de usuario (único)
- `contraseña`: Hash de la contraseña
- `fecha_registro`: Timestamp de registro

### Tabla `tareas`:
- `id`: Identificador único
- `usuario_id`: Referencia al usuario
- `titulo`: Título de la tarea
- `descripcion`: Descripción de la tarea
- `completada`: Estado de la tarea
- `fecha_creacion`: Timestamp de creación

## 🔒 Seguridad

- **Contraseñas hasheadas**: Se utilizan hashes bcrypt para almacenar contraseñas
- **Sesiones**: Sistema de sesiones para mantener la autenticación
- **Validación**: Validación de datos de entrada
- **Manejo de errores**: Respuestas de error apropiadas

## 📁 Estructura del Proyecto

```
API_REST/
├── servidor.py          # Servidor principal
├── requirements.txt     # Dependencias
├── README.md           # Documentación
└── usuarios.db         # Base de datos SQLite (se crea automáticamente)
```

## 🎨 Características de la UI

La página de bienvenida incluye:
- Diseño moderno y responsivo
- Gradientes y animaciones CSS
- Información del usuario autenticado
- Tarjetas de características del sistema
- Lista de endpoints disponibles
- Botón de cierre de sesión

## ⚠️ Notas Importantes

- En producción, cambiar la `secret_key` por una clave segura
- La base de datos se crea automáticamente al ejecutar el servidor
- El modo debug está habilitado para desarrollo
- Las contraseñas nunca se almacenan en texto plano

## 🎨 Capturas de pantalla de pruebas exitosas.
![image](https://github.com/user-attachments/assets/1359aaf5-8f83-4ee9-8fae-a0ca77054e1b)

![image](https://github.com/user-attachments/assets/0de932a0-c5b6-4b5d-936e-ea55684e25ae)

## 🧠 Respuestas Conceptuales:
### 🔐 ¿Por qué hashear contraseñas?
Hashear contraseñas es fundamental por seguridad. Si una base de datos es comprometida, las contraseñas almacenadas en texto plano pueden ser leídas fácilmente. Al hashearlas:
- Se vuelven ilegibles para terceros.
- Aumentás la seguridad de los usuarios.
- Es una práctica estándar recomendada por OWASP.
- Librerías como werkzeug.security (en Flask) permiten aplicar hashing con funciones como generate_password_hash, que incluyen salting automáticamente.

### 🗃️ Ventajas de usar SQLite en este proyecto.
- Simplicidad: No necesita configuración de servidor ni credenciales.
- Portabilidad: La base de datos es un archivo .db, fácil de mover o versionar.
- Ideal para prototipos o proyectos pequeños: Como es tu caso.
- Ligereza: Consume pocos recursos.
- SQLite es perfecto para proyectos educativos o de prueba, aunque no es lo ideal para sistemas de gran escala o con alta concurrencia.
