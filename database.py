import sqlite3
from datetime import datetime


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
