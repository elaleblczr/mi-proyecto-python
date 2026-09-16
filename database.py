import sqlite3
from datetime import datetime
import shutil
import os


# =====================================
# CREAR BASE DE DATOS
# =====================================

def crear_bd():

    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        total REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detalle_venta(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER,
        producto TEXT,
        cantidad INTEGER,
        precio REAL,
        subtotal REAL
    )
    """)

    conexion.commit()
    conexion.close()


# =====================================
# GUARDAR VENTA
# =====================================

def guardar_venta(ticket_actual, total):

    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cursor.execute("""
    INSERT INTO ventas(fecha,total)
    VALUES(?,?)
    """, (fecha, total))

    venta_id = cursor.lastrowid

    for producto, datos in ticket_actual.items():

        cantidad = datos["cantidad"]
        precio = datos["precio"]
        subtotal = cantidad * precio

        cursor.execute("""
        INSERT INTO detalle_venta
        (
            venta_id,
            producto,
            cantidad,
            precio,
            subtotal
        )
        VALUES(?,?,?,?,?)
        """,
        (
            venta_id,
            producto,
            cantidad,
            precio,
            subtotal
        ))

    conexion.commit()
    conexion.close()


# =====================================
# OBTENER TODAS LAS VENTAS
# =====================================

def obtener_ventas():

    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT *
    FROM ventas
    ORDER BY id DESC
    """)

    ventas = cursor.fetchall()

    conexion.close()

    return ventas


# =====================================
# OBTENER DETALLES DE UNA VENTA
# =====================================

def obtener_detalles_venta(venta_id):

    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT *
    FROM detalle_venta
    WHERE venta_id = ?
    ORDER BY id
    """, (venta_id,))

    detalles = cursor.fetchall()

    conexion.close()

    return detalles


# =====================================
# OBTENER VENTA POR ID
# =====================================

def obtener_venta_por_id(venta_id):

    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT *
    FROM ventas
    WHERE id = ?
    """, (venta_id,))

    venta = cursor.fetchone()

    conexion.close()

    return venta


# =====================================
# FOLIO SIGUIENTE
# =====================================

def obtener_siguiente_folio():

    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT MAX(id)
    FROM ventas
    """)

    resultado = cursor.fetchone()[0]

    conexion.close()

    if resultado is None:
        return 1

    return resultado + 1


# =====================================
# CORTE DEL DIA
# =====================================

def obtener_corte_diario():

    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT
        producto,
        SUM(cantidad),
        SUM(subtotal)
    FROM detalle_venta
    WHERE venta_id IN (
        SELECT id
        FROM ventas
        WHERE DATE(
            substr(fecha,7,4) || '-' ||
            substr(fecha,4,2) || '-' ||
            substr(fecha,1,2)
        ) = DATE('now')
    )
    GROUP BY producto
    """)

    datos = cursor.fetchall()

    conexion.close()

    return datos


# =====================================
# OBTENER TOTAL VENDIDO
# =====================================

def obtener_total_vendido():

    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT SUM(total)
    FROM ventas
    WHERE DATE(
        substr(fecha,7,4) || '-' ||
        substr(fecha,4,2) || '-' ||
        substr(fecha,1,2)
    ) = DATE('now')
    """)

    resultado = cursor.fetchone()[0]

    conexion.close()

    return resultado if resultado else 0


# =====================================
# OBTENER TOTAL HOY
# =====================================

def obtener_total_hoy():

    return obtener_total_vendido()


# =====================================
# OBTENER CORTE SEMANAL
# =====================================

def obtener_corte_semanal():

    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT
        producto,
        SUM(cantidad),
        SUM(subtotal)
    FROM detalle_venta
    WHERE venta_id IN (
        SELECT id
        FROM ventas
        WHERE strftime('%Y-%W', 
            substr(fecha,7,4) || '-' ||
            substr(fecha,4,2) || '-' ||
            substr(fecha,1,2)
        ) = strftime('%Y-%W', 'now')
    )
    GROUP BY producto
    """)

    datos = cursor.fetchall()

    conexion.close()

    return datos


# =====================================
# OBTENER TOTAL SEMANAL
# =====================================

def obtener_total_semanal():

    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT SUM(total)
    FROM ventas
    WHERE strftime('%Y-%W', 
        substr(fecha,7,4) || '-' ||
        substr(fecha,4,2) || '-' ||
        substr(fecha,1,2)
    ) = strftime('%Y-%W', 'now')
    """)

    resultado = cursor.fetchone()[0]

    conexion.close()

    return resultado if resultado else 0


# =====================================
# ELIMINAR VENTA
# =====================================

def eliminar_venta(venta_id):
    """Elimina una venta y sus detalles"""
    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    try:
        # Primero eliminar detalles de la venta
        cursor.execute("""
        DELETE FROM detalle_venta
        WHERE venta_id = ?
        """, (venta_id,))

        # Luego eliminar la venta
        cursor.execute("""
        DELETE FROM ventas
        WHERE id = ?
        """, (venta_id,))

        conexion.commit()
        conexion.close()
        return True

    except Exception as e:
        conexion.close()
        return False


# =====================================
# ACTUALIZAR PRODUCTO EN VENTA
# =====================================

def actualizar_producto_venta(detalle_id, cantidad, precio):
    """Actualiza cantidad y precio de un producto en una venta"""
    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    try:
        subtotal = cantidad * precio

        cursor.execute("""
        UPDATE detalle_venta
        SET cantidad = ?, precio = ?, subtotal = ?
        WHERE id = ?
        """, (cantidad, precio, subtotal, detalle_id))

        conexion.commit()
        conexion.close()
        return True

    except Exception as e:
        conexion.close()
        return False


# =====================================
# RECALCULAR TOTAL VENTA
# =====================================

def recalcular_total_venta(venta_id):
    """Recalcula el total de una venta basado en sus detalles"""
    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    try:
        # Calcular nuevo total
        cursor.execute("""
        SELECT SUM(subtotal)
        FROM detalle_venta
        WHERE venta_id = ?
        """, (venta_id,))

        nuevo_total = cursor.fetchone()[0]

        if nuevo_total is None:
            nuevo_total = 0

        # Actualizar total en ventas
        cursor.execute("""
        UPDATE ventas
        SET total = ?
        WHERE id = ?
        """, (nuevo_total, venta_id))

        conexion.commit()
        conexion.close()
        return True

    except Exception as e:
        conexion.close()
        return False


# =====================================
# ELIMINAR PRODUCTO DE VENTA
# =====================================

def eliminar_producto_venta(detalle_id):
    """Elimina un producto de una venta"""
    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    try:
        cursor.execute("""
        DELETE FROM detalle_venta
        WHERE id = ?
        """, (detalle_id,))

        conexion.commit()
        conexion.close()
        return True

    except Exception as e:
        conexion.close()
        return False


# =====================================
# BUSCAR VENTAS POR FECHA
# =====================================

def buscar_ventas_por_fecha(fecha):
    """Busca ventas por fecha específica (formato: DD/MM/YYYY)"""
    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT *
    FROM ventas
    WHERE fecha LIKE ?
    ORDER BY id DESC
    """, (f"{fecha}%",))

    ventas = cursor.fetchall()

    conexion.close()

    return ventas


# =====================================
# CREAR BACKUP
# =====================================

def crear_backup():
    """Crea una copia de seguridad de la base de datos"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = "backups"
        
        # Crear carpeta de backups si no existe
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        backup_path = f"{backup_dir}/ventas_backup_{timestamp}.db"
        shutil.copy2("ventas.db", backup_path)
        
        return True, f"Backup guardado: {backup_path}"
    
    except Exception as e:
        return False, f"Error en backup: {str(e)}"


# =====================================
# RESTAURAR BACKUP
# =====================================

def restaurar_backup(backup_path):
    """Restaura la base de datos desde un backup"""
    try:
        shutil.copy2(backup_path, "ventas.db")
        return True, "Backup restaurado exitosamente"
    
    except Exception as e:
        return False, f"Error al restaurar: {str(e)}"


# =====================================
# OBTENER ESTADISTICAS
# =====================================

def obtener_estadisticas():
    """Obtiene estadísticas de ventas"""
    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    try:
        # Total de ventas
        cursor.execute("SELECT COUNT(*) FROM ventas")
        total_ventas = cursor.fetchone()[0]

        # Total vendido
        cursor.execute("SELECT SUM(total) FROM ventas")
        total_vendido = cursor.fetchone()[0] or 0

        # Promedio por venta
        promedio_venta = total_vendido / total_ventas if total_ventas > 0 else 0

        # Venta máxima
        cursor.execute("SELECT MAX(total) FROM ventas")
        venta_maxima = cursor.fetchone()[0] or 0

        # Venta mínima
        cursor.execute("SELECT MIN(total) FROM ventas WHERE total > 0")
        venta_minima = cursor.fetchone()[0] or 0

        # Productos más vendidos
        cursor.execute("""
        SELECT producto, SUM(cantidad) as total_cantidad
        FROM detalle_venta
        GROUP BY producto
        ORDER BY total_cantidad DESC
        LIMIT 5
        """)

        productos_top = cursor.fetchall()
        productos_texto = "\n".join([f"{p[0]}: {int(p[1])} unidades" for p in productos_top])

        conexion.close()

        return {
            "total_ventas": total_ventas,
            "total_vendido": total_vendido,
            "promedio_venta": promedio_venta,
            "venta_maxima": venta_maxima,
            "venta_minima": venta_minima,
            "productos_top": productos_texto
        }

    except Exception as e:
        conexion.close()
        return {
            "total_ventas": 0,
            "total_vendido": 0,
            "promedio_venta": 0,
            "venta_maxima": 0,
            "venta_minima": 0,
            "productos_top": "Sin datos"
        }


# =====================================
# OBTENER LISTA DE BACKUPS
# =====================================

def obtener_backups():
    """Obtiene lista de archivos de backup disponibles"""
    try:
        if not os.path.exists("backups"):
            return []
        
        backups = [f for f in os.listdir("backups") if f.startswith("ventas_backup_")]
        return sorted(backups, reverse=True)
    
    except:
        return []


# =====================================
# EXPORTAR A CSV
# =====================================

def exportar_ventas_csv():
    """Exporta todas las ventas a formato CSV"""
    try:
        import csv
        
        conexion = sqlite3.connect("ventas.db")
        cursor = conexion.cursor()
        
        cursor.execute("""
        SELECT v.id, v.fecha, v.total, dv.producto, dv.cantidad, dv.precio
        FROM ventas v
        LEFT JOIN detalle_venta dv ON v.id = dv.venta_id
        ORDER BY v.id DESC
        """)
        
        datos = cursor.fetchall()
        conexion.close()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo = f"ventas_export_{timestamp}.csv"
        
        with open(archivo, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID Venta", "Fecha", "Total Venta", "Producto", "Cantidad", "Precio"])
            writer.writerows(datos)
        
        return True, f"Exportado a: {archivo}"
    
    except Exception as e:
        return False, f"Error al exportar: {str(e)}"


# =====================================
# OBTENER REPORTE MENSUAL
# =====================================

def obtener_reporte_mensual(mes, año):
    """Obtiene reporte de ventas de un mes específico"""
    conexion = sqlite3.connect("ventas.db")
    cursor = conexion.cursor()

    try:
        # Formato: MM y YYYY
        mes_str = f"{mes:02d}"
        
        cursor.execute("""
        SELECT
            COUNT(*) as total_ventas,
            SUM(total) as total_vendido,
            AVG(total) as promedio,
            MAX(total) as venta_maxima,
            MIN(total) as venta_minima
        FROM ventas
        WHERE substr(fecha,4,2) = ? AND substr(fecha,7,4) = ?
        """, (mes_str, str(año)))

        resultado = cursor.fetchone()
        conexion.close()

        if resultado[0] is None:
            return None

        return {
            "total_ventas": resultado[0],
            "total_vendido": resultado[1] or 0,
            "promedio": resultado[2] or 0,
            "venta_maxima": resultado[3] or 0,
            "venta_minima": resultado[4] or 0
        }

    except Exception as e:
        conexion.close()
        return None
