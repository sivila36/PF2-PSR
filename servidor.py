from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # En producción, usar una clave segura

# Crear la base de datos y tablas
def init_db():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            contraseña TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crear tabla de tareas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            completada BOOLEAN DEFAULT 0,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Inicializar la base de datos
init_db()

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'GET':
        """Muestra un formulario HTML simple para registro"""
        html_form = '''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Registro de Usuario</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    width: 100%;
                    max-width: 400px;
                }
                h1 {
                    text-align: center;
                    color: #333;
                    margin-bottom: 30px;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                label {
                    display: block;
                    margin-bottom: 5px;
                    color: #555;
                    font-weight: 500;
                }
                input[type="text"], input[type="password"] {
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    font-size: 16px;
                    box-sizing: border-box;
                    transition: border-color 0.3s ease;
                }
                input[type="text"]:focus, input[type="password"]:focus {
                    outline: none;
                    border-color: #4facfe;
                }
                button {
                    width: 100%;
                    padding: 12px;
                    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    cursor: pointer;
                    transition: transform 0.3s ease;
                }
                button:hover {
                    transform: translateY(-2px);
                }
                .links {
                    text-align: center;
                    margin-top: 20px;
                }
                .links a {
                    color: #4facfe;
                    text-decoration: none;
                    margin: 0 10px;
                }
                .links a:hover {
                    text-decoration: underline;
                }
                #resultado {
                    margin-top: 20px;
                    padding: 10px;
                    border-radius: 5px;
                    display: none;
                }
                .success {
                    background: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }
                .error {
                    background: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>👤 Registro de Usuario</h1>
                <form id="registroForm">
                    <div class="form-group">
                        <label for="usuario">Usuario:</label>
                        <input type="text" id="usuario" name="usuario" required>
                    </div>
                    <div class="form-group">
                        <label for="contraseña">Contraseña:</label>
                        <input type="password" id="contraseña" name="contraseña" required>
                    </div>
                    <button type="submit">📝 Registrar Usuario</button>
                </form>
                
                <div id="resultado"></div>
                
                <div class="links">
                    <a href="/login">🔐 Iniciar Sesión</a>
                </div>
            </div>

            <script>
                document.getElementById('registroForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const usuario = document.getElementById('usuario').value;
                    const contraseña = document.getElementById('contraseña').value;
                    const resultado = document.getElementById('resultado');
                    
                    try {
                        const response = await fetch('/registro', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                usuario: usuario,
                                contraseña: contraseña
                            })
                        });
                        
                        const data = await response.json();
                        
                        resultado.style.display = 'block';
                        if (response.ok) {
                            resultado.className = 'success';
                            resultado.textContent = data.mensaje;
                            document.getElementById('registroForm').reset();
                        } else {
                            resultado.className = 'error';
                            resultado.textContent = data.error;
                        }
                    } catch (error) {
                        resultado.style.display = 'block';
                        resultado.className = 'error';
                        resultado.textContent = 'Error de conexión: ' + error.message;
                    }
                });
            </script>
        </body>
        </html>
        '''
        return html_form
    
    # Método POST - Lógica original
    try:
        data = request.get_json()
        
        if not data or 'usuario' not in data or 'contraseña' not in data:
            return jsonify({'error': 'Datos incompletos. Se requiere usuario y contraseña'}), 400
        
        usuario = data['usuario']
        contraseña = data['contraseña']
        
        # Validar que los campos no estén vacíos
        if not usuario.strip() or not contraseña.strip():
            return jsonify({'error': 'Usuario y contraseña no pueden estar vacíos'}), 400
        
        # Hash de la contraseña
        contraseña_hash = generate_password_hash(contraseña)
        
        # Guardar en la base de datos
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO usuarios (usuario, contraseña) VALUES (?, ?)', 
                         (usuario, contraseña_hash))
            conn.commit()
            conn.close()
            
            return jsonify({'mensaje': 'Usuario registrado exitosamente'}), 201
            
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'error': 'El usuario ya existe'}), 409
            
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        """Muestra un formulario HTML simple para login"""
        html_form = '''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Iniciar Sesión</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    width: 100%;
                    max-width: 400px;
                }
                h1 {
                    text-align: center;
                    color: #333;
                    margin-bottom: 30px;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                label {
                    display: block;
                    margin-bottom: 5px;
                    color: #555;
                    font-weight: 500;
                }
                input[type="text"], input[type="password"] {
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    font-size: 16px;
                    box-sizing: border-box;
                    transition: border-color 0.3s ease;
                }
                input[type="text"]:focus, input[type="password"]:focus {
                    outline: none;
                    border-color: #4facfe;
                }
                button {
                    width: 100%;
                    padding: 12px;
                    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    cursor: pointer;
                    transition: transform 0.3s ease;
                }
                button:hover {
                    transform: translateY(-2px);
                }
                .links {
                    text-align: center;
                    margin-top: 20px;
                }
                .links a {
                    color: #4facfe;
                    text-decoration: none;
                    margin: 0 10px;
                }
                .links a:hover {
                    text-decoration: underline;
                }
                #resultado {
                    margin-top: 20px;
                    padding: 10px;
                    border-radius: 5px;
                    display: none;
                }
                .success {
                    background: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }
                .error {
                    background: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔐 Iniciar Sesión</h1>
                <form id="loginForm">
                    <div class="form-group">
                        <label for="usuario">Usuario:</label>
                        <input type="text" id="usuario" name="usuario" required>
                    </div>
                    <div class="form-group">
                        <label for="contraseña">Contraseña:</label>
                        <input type="password" id="contraseña" name="contraseña" required>
                    </div>
                    <button type="submit">🚀 Iniciar Sesión</button>
                </form>
                
                <div id="resultado"></div>
                
                <div class="links">
                    <a href="/registro">👤 Registrarse</a>
                </div>
            </div>

            <script>
                document.getElementById('loginForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const usuario = document.getElementById('usuario').value;
                    const contraseña = document.getElementById('contraseña').value;
                    const resultado = document.getElementById('resultado');
                    
                    try {
                        const response = await fetch('/login', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                usuario: usuario,
                                contraseña: contraseña
                            })
                        });
                        
                        const data = await response.json();
                        
                        resultado.style.display = 'block';
                        if (response.ok) {
                            resultado.className = 'success';
                            resultado.textContent = data.mensaje + ' - Redirigiendo a tareas...';
                            setTimeout(() => {
                                window.location.href = '/tareas';
                            }, 2000);
                        } else {
                            resultado.className = 'error';
                            resultado.textContent = data.error;
                        }
                    } catch (error) {
                        resultado.style.display = 'block';
                        resultado.className = 'error';
                        resultado.textContent = 'Error de conexión: ' + error.message;
                    }
                });
            </script>
        </body>
        </html>
        '''
        return html_form
    
    # Método POST - Lógica original
    try:
        data = request.get_json()
        
        if not data or 'usuario' not in data or 'contraseña' not in data:
            return jsonify({'error': 'Datos incompletos. Se requiere usuario y contraseña'}), 400
        
        usuario = data['usuario']
        contraseña = data['contraseña']
        
        # Verificar credenciales
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, usuario, contraseña FROM usuarios WHERE usuario = ?', (usuario,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data[2], contraseña):
            # Crear sesión
            session['usuario_id'] = user_data[0]
            session['usuario'] = user_data[1]
            
            return jsonify({'mensaje': 'Inicio de sesión exitoso', 'usuario': usuario}), 200
        else:
            return jsonify({'error': 'Credenciales incorrectas'}), 401
            
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'mensaje': 'Sesión cerrada exitosamente'}), 200

@app.route('/tareas')
def tareas():
    # Verificar si el usuario está autenticado
    if 'usuario_id' not in session:
        return jsonify({'error': 'Debe iniciar sesión para acceder a las tareas'}), 401
    
    # HTML de bienvenida
    html_template = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sistema de Tareas</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 {
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }
            .welcome-message {
                padding: 30px;
                text-align: center;
                font-size: 1.2em;
                line-height: 1.6;
            }
            .user-info {
                background: #f8f9fa;
                padding: 20px;
                margin: 20px;
                border-radius: 10px;
                border-left: 5px solid #4facfe;
            }
            .features {
                padding: 30px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            }
            .feature-card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                transition: transform 0.3s ease;
            }
            .feature-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .feature-card h3 {
                color: #4facfe;
                margin-bottom: 10px;
            }
            .logout-btn {
                display: inline-block;
                background: #dc3545;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
                transition: background 0.3s ease;
            }
            .logout-btn:hover {
                background: #c82333;
            }
            .api-info {
                background: #e9ecef;
                padding: 20px;
                margin: 20px;
                border-radius: 10px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 Sistema de Tareas</h1>
            </div>
            
            <div class="welcome-message">
                <h2>¡Hola, {{ usuario }}!</h2>
                <p>Has iniciado sesión exitosamente en el sistema de gestión de tareas.</p>
            </div>
            
            <div class="user-info">
                <h3>📋 Información de Usuario</h3>
                <p><strong>ID de Usuario:</strong> {{ usuario_id }}</p>
                <p><strong>Nombre de Usuario:</strong> {{ usuario }}</p>
                <p><strong>Fecha de Acceso:</strong> {{ fecha_actual }}</p>
            </div>
            
            <div class="features">
                <div class="feature-card">
                    <h3>👤 Gestión de Usuarios</h3>
                    <p>Registro e inicio de sesión seguro con contraseñas hasheadas</p>
                </div>
                <div class="feature-card">
                    <h3>🔐 Autenticación</h3>
                    <p>Sistema de sesiones para mantener la seguridad</p>
                </div>
                <div class="feature-card">
                    <h3>💾 Base de Datos</h3>
                    <p>Persistencia de datos en SQLite</p>
                </div>
                <div class="feature-card">
                    <h3>🛡️ Seguridad</h3>
                    <p>Contraseñas protegidas con hash bcrypt</p>
                </div>
            </div>
            
            <div class="api-info">
                <h3>🔗 Endpoints Disponibles:</h3>
                <ul>
                    <li><strong>GET/POST /registro</strong> - Registrar nuevo usuario</li>
                    <li><strong>GET/POST /login</strong> - Iniciar sesión</li>
                    <li><strong>GET /tareas</strong> - Ver página de bienvenida (requiere autenticación)</li>
                    <li><strong>GET /logout</strong> - Cerrar sesión</li>
                </ul>
            </div>
            
            <div style="text-align: center; padding: 20px;">
                <a href="/logout" class="logout-btn">🚪 Cerrar Sesión</a>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html_template, 
                                usuario=session['usuario'],
                                usuario_id=session['usuario_id'],
                                fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

@app.route('/')
def index():
    return jsonify({
        'mensaje': 'API REST de Gestión de Tareas',
        'endpoints': {
            'registro': 'GET/POST /registro - Registrar nuevo usuario',
            'login': 'GET/POST /login - Iniciar sesión',
            'tareas': 'GET /tareas - Ver página de bienvenida (requiere autenticación)',
            'logout': 'GET /logout - Cerrar sesión'
        }
    })

if __name__ == '__main__':
    print("🚀 Iniciando servidor API REST...")
    print("📋 Endpoints disponibles:")
    print("   GET/POST /registro - Registrar usuario")
    print("   GET/POST /login - Iniciar sesión")
    print("   GET /tareas - Página de bienvenida")
    print("   GET /logout - Cerrar sesión")
    print("   GET / - Información de la API")
    print("\n🌐 Servidor ejecutándose en: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
