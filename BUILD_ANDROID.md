# Construir APK para Android

La aplicación móvil está en `app_kivy.py` y usa la misma base SQLite (`ventas.db`).
En Android la base se copia una sola vez al almacenamiento privado de la app, por
lo que las ventas nuevas no dependen de permisos externos.

## GitHub Actions (sin instalar Linux localmente)

El workflow `.github/workflows/build-android.yml` compila automáticamente en
Ubuntu cuando se hace push a `main`. También se puede iniciar manualmente:

1. Abre la pestaña **Actions** del repositorio en GitHub.
2. Selecciona **Build Android APK**.
3. Pulsa **Run workflow**, elige la rama y confirma con **Run workflow**.
4. Espera a que termine el job **build** (la primera ejecución descarga SDK/NDK
   y puede tardar varios minutos).
5. En la ejecución terminada, baja a **Artifacts**, selecciona
   `cajaregistradora-debug-apk` y descarga el ZIP que contiene el APK.

Un push a `main` inicia el mismo workflow automáticamente. El artifact se
conserva durante 14 días.

## Construcción local opcional

Buildozer requiere Linux. En Windows se puede usar WSL2 con Ubuntu:

```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip buildozer cython
buildozer -v android debug
```

El APK de prueba queda en `bin/`. Para una compilación limpia usar
`buildozer android clean` antes de repetir el comando. La primera compilación
descarga Android SDK/NDK y puede tardar varios minutos.
