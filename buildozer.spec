[app]

# Información de la aplicación
title = Caja Registradora
package.name = cajaregistradora
package.domain = org.ejemplo

# Archivo principal
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db

# Versión
version = 1.0.0

# Requerimientos
requirements = python3,kivy,flet,sqlite3

# Orientación (portrait para móvil)
orientation = portrait

# Fullscreen
fullscreen = 1

# Permisos de Android
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# Versión mínima de Android
android.minapi = 21
android.targetapi = 31
android.api = 31

# Arquitectura
android.archs = arm64-v8a,armeabi-v7a

# Nombre del paquete Java
android.java_classes = org.kivy.android.PythonActivity

# Icono de la aplicación (opcional)
# android.icon = data/icon.png

# Imagen de splash (opcional)
# android.presplash = data/presplash.png

# Versión de NDK y SDK
android.ndk = 25b
android.sdk = 31

# Gradle
android.gradle_dependencies = androidx.appcompat:appcompat:1.3.1

# Configuración de compilación
p4a.bootstrap = sdl2

# Logs
log_level = 2

[buildozer]

# Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# Display warning when buildozer is run as root (<= 0 to accept)
warn_on_root = 1

# Path to build artifact storage, absolute or relative to spec file
build_dir = .buildozer

# Path to build output (i.e. .apk, .aab, .ipa) storage
bin_dir = ./bin
