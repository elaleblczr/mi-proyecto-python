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


# ==========