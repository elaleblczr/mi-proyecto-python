# 🛍️ Caja Registradora - Aplicación Android

Una aplicación de punto de venta (POS) moderna y fácil de usar, diseñada para funcionar en Android sin necesidad de conexión a internet.

## ✨ Características

- ✅ **Control por teclado** - Selecciona productos con teclas 1-4
- ✅ **Interfaz simple** - Diseñado para ser rápido de usar
- ✅ **Base de datos offline** - SQLite integrado, sin conexión necesaria
- ✅ **Gestión de registros** - Ver, editar y borrar ventas
- ✅ **Reportes diarios** - Consulta de ventas del día
- ✅ **Multiplataforma** - Funciona en Android, iOS y Web (Flet)

## 🎮 Controles

| Tecla | Acción |
|-------|--------|
| **1-4** | Seleccionar producto |
| **Números** | Ingresar dinero recibido |
| **ENTER** | Cobrar venta |
| **C** | Cancelar venta |
| **BACKSPACE** | Quitar último producto |
| **DELETE** | Borrar dígito del dinero |
| **R** | Ver reportes |

## 📋 Requisitos Previos

Para compilar a APK necesitas:

1. **Python 3.9 o superior** - [Descargar](https://www.python.org/downloads/)
2. **Java Development Kit (JDK)** - [Descargar](https://www.oracle.com/java/technologies/downloads/)
3. **Android SDK** - [Descargar](https://developer.android.com/studio)
4. **Git** (opcional pero recomendado)

## 🚀 Instalación y Compilación

### Opción 1: En Linux/macOS

```bash
# 1. Clonar el repositorio
git clone https://github.com/elaleblczr/mi-proyecto-python.git
cd mi-proyecto-python

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install --upgrade pip
pip install buildozer cython
pip install flet

# 4. Compilar a APK
buildozer android debug

# El APK se generará en: bin/cajaregistradora-1.0.0-debug.apk
```

### Opción 2: En Windows

```bash
# 1. Clonar el repositorio
git clone https://github.com/elaleblczr/mi-proyecto-python.git
cd mi-proyecto-python

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install --upgrade pip
pip install buildozer cython
pip install flet

# 4. Compilar a APK
buildozer android debug
```

### Opción 3: Usar Docker (Recomendado - Sin instalaciones complicadas)

```bash
# Construcción automática con Docker
docker run --rm -v $(pwd):/app -w /app buildozer/buildozer:latest \
  buildozer android debug
```

## 📲 Instalar en tu Dispositivo Android

### Método 1: Directamente (APK generado)

```bash
# Conecta tu teléfono por USB
adb install bin/cajaregistradora-1.0.0-debug.apk
```

### Método 2: Transferencia manual

1. Copia el archivo `bin/cajaregistradora-1.0.0-debug.apk` a tu teléfono
2. Abre el archivo en el explorador
3. Permite la instalación de fuentes desconocidas
4. ¡Listo! La app está instalada

## 🔧 Configuración

### Cambiar Productos

Edita el archivo `app.py` en la sección `productos`:

```python
productos = {
    "1": {"nombre": "Victoria", "precio": 48},
    "2": {"nombre": "Corona", "precio": 48},
    "3": {"nombre": "Pall Mall Azul", "precio": 7},
    "4": {"nombre": "Marlboro Rojo", "precio": 7}
}
```

### Cambiar información de la App

En `buildozer.spec`:

```ini
[app]
title = Tu Nombre de App
package.name = tunombreaplicacion
package.domain = org.ejemplo
version = 1.0.0
```

## 📊 Estructura de Archivos

```
mi-proyecto-python/
├── app.py                 # Aplicación principal (Flet)
├── database.py            # Gestión de base de datos (SQLite)
├── buildozer.spec         # Configuración de compilación
├── ventas.db              # Base de datos (se crea automáticamente)
├── ver_ventas.py          # Script auxiliar
└── README.md              # Este archivo
```

## 🛠️ Solución de Problemas

### Error: "buildozer: command not found"

```bash
pip install --upgrade buildozer
```

### Error: "No Java compiler found"

Asegúrate de tener JDK instalado:
```bash
java -version  # Verifica si está instalado
```

### Error: "Android SDK not found"

1. Descarga Android Studio
2. Abre Android Studio y completa el asistente de instalación
3. Configura las variables de entorno:

**En Linux/macOS:**
```bash
export ANDROID_SDK_ROOT=$HOME/Android/Sdk
export ANDROID_NDK_ROOT=$HOME/Android/Sdk/ndk/25.1.8937393
```

**En Windows:**
```bash
set ANDROID_SDK_ROOT=C:\Users\TuUsuario\AppData\Local\Android\Sdk
set ANDROID_NDK_ROOT=C:\Users\TuUsuario\AppData\Local\Android\Sdk\ndk\25.1.8937393
```

### La app tarda mucho en compilar

Es normal la primera vez (20-40 minutos). Las compilaciones posteriores son más rápidas.

## 📱 Uso en la Aplicación

1. **Agregar productos**: Presiona 1-4 según el producto
2. **Ingresar dinero**: Teclea los números
3. **Cobrar**: Presiona ENTER
4. **Ver registros**: Presiona el botón de registros en la app
5. **Editar venta**: Selecciona una venta y presiona editar

## 🗄️ Transferencia a otra laptop por USB

1. Conecta un USB a tu laptop actual
2. Copia esta carpeta completa al USB:
   ```bash
   cp -r mi-proyecto-python/ /media/usb/
   ```
3. Conecta el USB a otra laptop
4. Copia los archivos
5. Instala las dependencias (ver sección Instalación)
6. ¡La app está lista para usar!

## 📝 Notas Importantes

- **Base de datos**: El archivo `ventas.db` se guarda en el dispositivo automáticamente
- **Backup**: Considera hacer backup de `ventas.db` periódicamente
- **Permisos**: La app solicita permisos de almacenamiento para guardar datos
- **Versión de Android**: Soporta Android 5.0+ (API 21+)

## 🚀 Próximas Mejoras

- [ ] Sincronización en la nube (opcional)
- [ ] Exportar reportes a PDF
- [ ] Análisis gráficos de ventas
- [ ] Contraseña de acceso
- [ ] Múltiples usuarios

## 📧 Soporte y Contribuciones

Si encuentras problemas o tienes sugerencias, crea un issue en GitHub.

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

**Última actualización**: Septiembre 2026
**Versión**: 1.0.0
