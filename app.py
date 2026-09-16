import flet as ft
from database import (
    crear_bd, guardar_venta, obtener_siguiente_folio,
    obtener_ventas, obtener_detalles_venta, obtener_venta_por_id,
    eliminar_venta, actualizar_producto_venta, recalcular_total_venta,
    eliminar_producto_venta, buscar_ventas_por_fecha, obtener_corte_diario,
    obtener_total_vendido
)
from datetime import datetime

# =====================================
# CONFIGURACION
# =====================================

productos = {
    "1": {"nombre": "Victoria", "precio": 48},
    "2": {"nombre": "Corona", "precio": 48},
    "3": {"nombre": "Pall Mall Azul", "precio": 7},
    "4": {"nombre": "Marlboro Rojo", "precio": 7}
}

ticket_actual = {}
total = 0
recibido_temporal = ""
venta_en_edicion = None

# =====================================
# FUNCIONES DEL TICKET
# =====================================

def agregar_producto(tecla):
    """Agrega un producto por tecla numérica"""
    global total
    
    if tecla not in productos:
        return
    
    datos_producto = productos[tecla]
    nombre = datos_producto["nombre"]
    precio = datos_producto["precio"]

    if nombre in ticket_actual:
        ticket_actual[nombre]["cantidad"] += 1
    else:
        ticket_actual[nombre] = {
            "precio": precio,
            "cantidad": 1
        }

    total += precio
    actualizar_ticket()
    calcular_cambio()

def quitar_ultimo_producto():
    """Quita el último producto agregado"""
    global total
    
    if not ticket_actual:
        return
    
    ultimo_producto = list(ticket_actual.keys())[-1]
    precio = ticket_actual[ultimo_producto]["precio"]
    ticket_actual[ultimo_producto]["cantidad"] -= 1
    total -= precio
    
    if ticket_actual[ultimo_producto]["cantidad"] <= 0:
        del ticket_actual[ultimo_producto]
    
    if total < 0:
        total = 0
    
    actualizar_ticket()
    calcular_cambio()

def actualizar_ticket():
    """Actualiza la visualización del ticket"""
    ticket_text.value = "╔════════════════════════════╗\n"
    ticket_text.value += "║         TICKET             ║\n"
    ticket_text.value += "╚════════════════════════════╝\n\n"

    for producto, datos in ticket_actual.items():
        cantidad = datos["cantidad"]
        precio = datos["precio"]
        subtotal = cantidad * precio
        ticket_text.value += f"{producto:<18} x{cantidad:<2} ${subtotal}\n"

    ticket_text.value += "\n" + "─" * 30 + "\n"
    ticket_text.value += f"TOTAL: ${total}\n"
    ticket_text.value += "─" * 30

    total_label.value = f"TOTAL: ${total}"
    page.update()

def calcular_cambio():
    """Calcula el cambio según lo ingresado"""
    global recibido_temporal
    
    try:
        recibido = float(recibido_temporal) if recibido_temporal else 0

        if recibido >= total:
            cambio = recibido - total
            cambio_label.value = f"CAMBIO: ${cambio:.2f}"
            cambio_label.color = "lightgreen"
        else:
            cambio_label.value = f"Falta: ${total - recibido:.2f}"
            cambio_label.color = "orange"

    except:
        cambio_label.value = "CAMBIO: $0.00"
        cambio_label.color = "lightgreen"
    
    page.update()

def cancelar_venta():
    """Cancela la venta actual"""
    global total, recibido_temporal

    ticket_actual.clear()
    total = 0
    recibido_temporal = ""

    ticket_text.value = "El ticket aparecerá aquí"
    recibido_label.value = "RECIBIDO: $0"
    total_label.value = "TOTAL: $0"
    cambio_label.value = "CAMBIO: $0.00"
    cambio_label.color = "lightgreen"
    
    page.update()
    mostrar_snackbar("Venta cancelada")

def cobrar():
    """Realiza el cobro"""
    global total, recibido_temporal

    if total == 0:
        mostrar_snackbar("No hay productos en la venta", "error")
        return

    try:
        recibido = float(recibido_temporal) if recibido_temporal else 0
    except:
        mostrar_snackbar("Ingresa una cantidad válida", "error")
        return

    if recibido < total:
        mostrar_snackbar(f"Falta: ${total - recibido:.2f}", "error")
        return

    cambio = recibido - total

    guardar_venta(ticket_actual, total)

    mostrar_snackbar(
        f"✓ Venta: ${total:.2f} | Cambio: ${cambio:.2f}",
        "success"
    )

    cancelar_venta()
    folio_label.value = f"FOLIO: {obtener_siguiente_folio():06d}"

# =====================================
# FUNCIONES DE REGISTROS
# =====================================

def mostrar_registros():
    """Muestra la pantalla de registros"""
    cargar_lista_ventas()
    page.views.append(
        ft.View("/registros", [
            ft.AppBar(
                title=ft.Text("📊 Registros de Ventas"),
                bgcolor="blue",
                leading=ft.IconButton(
                    ft.icons.ARROW_BACK,
                    on_click=lambda _: volver_a_principal()
                )
            ),
            ft.Column([
                ft.Row([
                    ft.TextField(
                        label="Buscar por fecha (DD/MM/YYYY)",
                        width=250,
                        on_change=lambda e: buscar_venta_por_fecha(e.control.value)
                    ),
                    ft.IconButton(
                        ft.icons.REFRESH,
                        on_click=lambda _: cargar_lista_ventas()
                    )
                ], wrap=True),
                lista_ventas,
                ft.Divider(),
                detalles_venta_column
            ], expand=True, scroll="auto")
        ])
    )
    page.update()

def cargar_lista_ventas():
    """Carga todas las ventas en la lista"""
    lista_ventas.controls.clear()
    ventas = obtener_ventas()
    
    for venta in ventas:
        venta_id, fecha, total_venta = venta
        lista_ventas.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([
                                ft.Text(f"Venta #{venta_id:06d}", weight="bold", size=16),
                                ft.Text(f"Fecha: {fecha}", size=12, color="gray"),
                                ft.Text(f"Total: ${total_venta:.2f}", size=14, weight="bold", color="green")
                            ], expand=True),
                            ft.IconButton(
                                ft.icons.EDIT,
                                on_click=lambda _, vid=venta_id: editar_venta(vid)
                            ),
                            ft.IconButton(
                                ft.icons.DELETE,
                                icon_color="red",
                                on_click=lambda _, vid=venta_id: confirmar_eliminar(vid)
                            )
                        ], spacing=5)
                    ]),
                    padding=10
                )
            )
        )
    
    page.update()

def editar_venta(venta_id):
    """Abre la pantalla de edición de venta"""
    global venta_en_edicion
    venta_en_edicion = venta_id
    
    venta = obtener_venta_por_id(venta_id)
    detalles = obtener_detalles_venta(venta_id)
    
    editar_column.controls.clear()
    
    editar_column.controls.append(
        ft.Text(f"Editando Venta #{venta_id:06d}", weight="bold", size=18)
    )
    editar_column.controls.append(
        ft.Text(f"Fecha: {venta[1]}", size=12, color="gray")
    )
    
    for detalle in detalles:
        detalle_id, vid, producto, cantidad, precio, subtotal = detalle
        
        cantidad_field = ft.TextField(
            label="Cantidad",
            value=str(cantidad),
            width=100,
            keyboard_type="number"
        )
        
        precio_field = ft.TextField(
            label="Precio",
            value=str(precio),
            width=100,
            keyboard_type="number"
        )
        
        editar_column.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(f"Producto: {producto}", weight="bold"),
                        ft.Row([
                            cantidad_field,
                            precio_field,
                            ft.IconButton(
                                ft.icons.DELETE,
                                icon_color="red",
                                on_click=lambda _, did=detalle_id, cid=cantidad_field, pid=precio_field: 
                                    eliminar_detalle(did)
                            ),
                            ft.IconButton(
                                ft.icons.SAVE,
                                icon_color="green",
                                on_click=lambda _, did=detalle_id, cid=cantidad_field, pid=precio_field: 
                                    guardar_cambio_detalle(did, cid, pid)
                            )
                        ])
                    ]),
                    padding=10
                )
            )
        )
    
    editar_column.controls.append(
        ft.Row([
            ft.ElevatedButton(
                "Guardar y Cerrar",
                on_click=lambda _: cerrar_edicion()
            ),
            ft.ElevatedButton(
                "Cancelar",
                on_click=lambda _: cerrar_edicion()
            )
        ])
    )
    
    detalles_venta_column.controls = [editar_column]
    page.update()

def eliminar_detalle(detalle_id):
    """Elimina un producto de la venta"""
    if eliminar_producto_venta(detalle_id):
        if venta_en_edicion:
            recalcular_total_venta(venta_en_edicion)
            editar_venta(venta_en_edicion)
        mostrar_snackbar("Producto eliminado", "success")

def guardar_cambio_detalle(detalle_id, cantidad_field, precio_field):
    """Guarda cambios en un producto"""
    try:
        cantidad = int(cantidad_field.value)
        precio = float(precio_field.value)
        
        if cantidad <= 0 or precio < 0:
            mostrar_snackbar("Valores inválidos", "error")
            return
        
        if actualizar_producto_venta(detalle_id, cantidad, precio):
            if venta_en_edicion:
                recalcular_total_venta(venta_en_edicion)
                editar_venta(venta_en_edicion)
            mostrar_snackbar("Cambio guardado", "success")
    except:
        mostrar_snackbar("Error al guardar", "error")

def cerrar_edicion():
    """Cierra la edición y recarga la lista"""
    detalles_venta_column.controls.clear()
    cargar_lista_ventas()
    page.update()

def confirmar_eliminar(venta_id):
    """Muestra diálogo de confirmación para eliminar"""
    def eliminar_confirmed(_):
        if eliminar_venta(venta_id):
            mostrar_snackbar("Venta eliminada", "success")
            cargar_lista_ventas()
        else:
            mostrar_snackbar("Error al eliminar", "error")
        dlg_modal.open = False
        page.update()
    
    dlg_modal = ft.AlertDialog(
        title=ft.Text("¿Eliminar venta?"),
        content=ft.Text("Esta acción no se puede deshacer"),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda _: (setattr(dlg_modal, 'open', False), page.update())),
            ft.TextButton("Eliminar", on_click=eliminar_confirmed)
        ]
    )
    
    page.dialog = dlg_modal
    dlg_modal.open = True
    page.update()

def buscar_venta_por_fecha(fecha):
    """Busca ventas por fecha"""
    if not fecha:
        cargar_lista_ventas()
        return
    
    lista_ventas.controls.clear()
    ventas = buscar_ventas_por_fecha(fecha)
    
    for venta in ventas:
        venta_id, fecha_venta, total_venta = venta
        lista_ventas.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([
                                ft.Text(f"Venta #{venta_id:06d}", weight="bold", size=16),
                                ft.Text(f"Fecha: {fecha_venta}", size=12, color="gray"),
                                ft.Text(f"Total: ${total_venta:.2f}", size=14, weight="bold", color="green")
                            ], expand=True),
                            ft.IconButton(
                                ft.icons.EDIT,
                                on_click=lambda _, vid=venta_id: editar_venta(vid)
                            ),
                            ft.IconButton(
                                ft.icons.DELETE,
                                icon_color="red",
                                on_click=lambda _, vid=venta_id: confirmar_eliminar(vid)
                            )
                        ], spacing=5)
                    ]),
                    padding=10
                )
            )
        )
    
    page.update()

def volver_a_principal():
    """Vuelve a la pantalla principal"""
    page.views.pop()
    page.update()

# =====================================
# FUNCIONES UI
# =====================================

def mostrar_snackbar(mensaje, tipo="info"):
    """Muestra un mensaje temporal"""
    color = "green" if tipo == "success" else "red" if tipo == "error" else "blue"
    snackbar = ft.SnackBar(
        ft.Text(mensaje),
        bgcolor=color
    )
    page.overlay.append(snackbar)
    snackbar.open = True
    page.update()

def handle_keyboard(e):
    """Maneja entrada de teclado"""
    global recibido_temporal
    
    key = e.key
    
    # Productos (1-4)
    if key in productos:
        agregar_producto(key)
        return
    
    # ENTER para cobrar
    if key == "Enter":
        cobrar()
        return
    
    # C para cancelar
    if key.lower() == "c":
        cancelar_venta()
        return
    
    # R para reportes
    if key.lower() == "r":
        mostrar_reportes()
        return
    
    # BackSpace para quitar producto
    if key == "Backspace":
        quitar_ultimo_producto()
        return
    
    # Números para dinero
    if key.isdigit():
        recibido_temporal += key
        recibido_label.value = f"RECIBIDO: ${recibido_temporal if recibido_temporal else '0'}"
        calcular_cambio()
        return
    
    # Delete para borrar dígito
    if key == "Delete":
        if recibido_temporal:
            recibido_temporal = recibido_temporal[:-1]
            recibido_label.value = f"RECIBIDO: ${recibido_temporal if recibido_temporal else '0'}"
            calcular_cambio()

def mostrar_reportes():
    """Muestra reportes diarios"""
    productos_reporte = obtener_corte_diario()
    total_general = obtener_total_vendido()
    
    reporte_text = "CORTE DE CAJA DIARIO\n\n"
    reporte_text += "PRODUCTOS VENDIDOS:\n"
    reporte_text += "─" * 40 + "\n"
    
    for producto, cantidad, total_producto in productos_reporte:
        reporte_text += f"{producto}\n"
        reporte_text += f"  Cantidad: {cantidad}\n"
        reporte_text += f"  Total: ${total_producto:.2f}\n\n"
    
    reporte_text += "─" * 40 + "\n"
    reporte_text += f"TOTAL VENDIDO: ${total_general:.2f}"
    
    dlg = ft.AlertDialog(
        title=ft.Text("📊 Reportes"),
        content=ft.Text(reporte_text),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda _: (setattr(dlg, 'open', False), page.update()))
        ]
    )
    
    page.dialog = dlg
    dlg.open = True
    page.update()

# =====================================
# CONFIGURAR UI GLOBAL
# =====================================

ticket_text = ft.Text("El ticket aparecerá aquí", size=12)
total_label = ft.Text("TOTAL: $0", size=28, weight="bold", color="lightgreen")
recibido_label = ft.Text("RECIBIDO: $0", size=20, weight="bold", color="lightblue")
cambio_label = ft.Text("CAMBIO: $0.00", size=20, weight="bold", color="lightgreen")
folio_label = ft.Text(f"FOLIO: {obtener_siguiente_folio():06d}", size=16, weight="bold", color="orange")

lista_ventas = ft.Column(expand=True, scroll="auto")
detalles_venta_column = ft.Column(expand=True, scroll="auto")
editar_column = ft.Column()

# =====================================
# VISTA PRINCIPAL
# =====================================

def main(page: ft.Page):
    global page as page_global
    
    page.title = "Caja Registradora Android"
    page.scroll = "auto"
    
    crear_bd()
    
    # Bind de teclado
    page.on_keyboard_event = handle_keyboard
    
    # Vista principal
    page_principal = ft.View("/", [
        ft.AppBar(
            title=ft.Text("🛍️ CAJA REGISTRADORA"),
            bgcolor="blue",
            actions=[
                ft.IconButton(
                    ft.icons.RECEIPT_LONG,
                    on_click=lambda _: mostrar_registros(),
                    tooltip="Registros"
                )
            ]
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("⌨️ [1-4] Productos | [Números] Dinero | [ENTER] Cobrar | [C] Cancelar", 
                       size=10, color="lightblue"),
                folio_label,
                ft.Divider(),
                
                # Ticket
                ft.Card(
                    content=ft.Container(
                        content=ticket_text,
                        padding=10
                    )
                ),
                
                # Totales
                total_label,
                recibido_label,
                cambio_label,
                
                ft.Divider(),
                
                # Botones principales
                ft.Row([
                    ft.ElevatedButton(
                        "COBRAR [ENTER]",
                        bgcolor="green",
                        color="white",
                        on_click=lambda _: cobrar()
                    ),
                    ft.ElevatedButton(
                        "CANCELAR [C]",
                        bgcolor="red",
                        color="white",
                        on_click=lambda _: cancelar_venta()
                    )
                ], wrap=True),
                
                ft.ElevatedButton(
                    "REPORTES [R]",
                    bgcolor="orange",
                    color="white",
                    on_click=lambda _: mostrar_reportes(),
                    expand=True
                )
            ], spacing=10, expand=True),
            padding=15
        )
    ])
    
    page.add(page_principal)

if __name__ == "__main__":
    ft.app(target=main)
