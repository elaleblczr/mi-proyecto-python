import customtkinter as ctk
from tkinter import messagebox

from database import crear_bd
from database import guardar_venta

from database import obtener_corte_diario
from database import obtener_total_vendido

from database import obtener_siguiente_folio

from datetime import datetime

from database import obtener_total_hoy
from database import obtener_corte_semanal
from database import obtener_total_semanal

# =====================================
# CONFIGURACION
# =====================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

productos = {
    "1": {"nombre": "Victoria", "precio": 48},
    "2": {"nombre": "Corona", "precio": 48},
    "3": {"nombre": "Pall Mall Azul", "precio": 7},
    "4": {"nombre": "Marlboro Rojo", "precio": 7}
}

ticket_actual = {}
total = 0
recibido_temporal = ""

# =====================================
# FUNCIONES
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
    
    # Feedback visual
    parpadear_producto(tecla)

def quitar_ultimo_producto():
    """Quita el último producto agregado"""
    global total
    
    if not ticket_actual:
        return
    
    # Obtener el último producto agregado
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
    ticket.configure(state="normal")
    ticket.delete("1.0", "end")

    ticket.insert("end", "╔════════════════════════════╗\n")
    ticket.insert("end", "║         TICKET             ║\n")
    ticket.insert("end", "╚════════════════════════════╝\n\n")

    for producto, datos in ticket_actual.items():
        cantidad = datos["cantidad"]
        precio = datos["precio"]
        subtotal = cantidad * precio

        ticket.insert(
            "end",
            f"{producto:<18} x{cantidad:<2} ${subtotal}\n"
        )

    ticket.insert("end", "\n" + "─" * 30 + "\n")
    ticket.insert("end", f"TOTAL: ${total}\n")
    ticket.insert("end", "─" * 30 + "\n")

    total_label.configure(
        text=f"TOTAL: ${total}"
    )
    
    ticket.configure(state="disabled")

def calcular_cambio(event=None):
    """Calcula el cambio según lo ingresado"""
    global recibido_temporal
    
    try:
        recibido = float(recibido_temporal) if recibido_temporal else 0

        if recibido >= total:
            cambio = recibido - total
            cambio_label.configure(
                text=f"CAMBIO: ${cambio:.2f}",
                text_color="lightgreen"
            )
        else:
            cambio_label.configure(
                text=f"Falta: ${total - recibido:.2f}",
                text_color="orange"
            )

    except:
        cambio_label.configure(
            text="CAMBIO: $0.00",
            text_color="lightgreen"
        )

def handle_numpad_input(event):
    """Maneja entrada de números del teclado numérico y regular"""
    global recibido_temporal
    
    key = event.keysym
    char = event.char
    
    # Teclas de productos (1-4)
    if key in productos:
        agregar_producto(key)
        return
    
    # Tecla ENTER para cobrar
    if key == "Return":
        cobrar()
        return
    
    # Tecla C para cancelar
    if key.lower() == "c":
        cancelar_venta()
        return
    
    # Tecla R para reportes
    if key.lower() == "r":
        mostrar_reportes()
        return
    
    # Tecla BackSpace para quitar producto
    if key == "BackSpace":
        quitar_ultimo_producto()
        return
    
    # Números para ingresar dinero recibido
    if char.isdigit():
        recibido_temporal += char
        recibido_label.configure(
            text=f"RECIBIDO: ${recibido_temporal if recibido_temporal else '0'}"
        )
        calcular_cambio()
        return
    
    # Punto decimal
    if char == "." and "." not in recibido_temporal:
        recibido_temporal += char
        recibido_label.configure(
            text=f"RECIBIDO: ${recibido_temporal if recibido_temporal else '0'}"
        )
        return
    
    # Borrar último dígito con Delete
    if key == "Delete":
        if recibido_temporal:
            recibido_temporal = recibido_temporal[:-1]
            recibido_label.configure(
                text=f"RECIBIDO: ${recibido_temporal if recibido_temporal else '0'}"
            )
            calcular_cambio()

def parpadear_producto(tecla):
    """Efecto visual cuando se selecciona un producto"""
    botones_productos[tecla].configure(fg_color="white")
    app.after(100, lambda: botones_productos[tecla].configure(fg_color="green"))

def cancelar_venta():
    """Cancela la venta actual"""
    global total, recibido_temporal

    ticket_actual.clear()
    total = 0
    recibido_temporal = ""

    ticket.configure(state="normal")
    ticket.delete("1.0", "end")
    ticket.configure(state="disabled")

    recibido_label.configure(
        text="RECIBIDO: $0"
    )

    total_label.configure(
        text="TOTAL: $0"
    )

    cambio_label.configure(
        text="CAMBIO: $0.00",
        text_color="lightgreen"
    )
    
    messagebox.showinfo("Venta Cancelada", "La venta ha sido cancelada.")

def cobrar():
    """Realiza el cobro"""
    global total, recibido_temporal

    if total == 0:
        messagebox.showwarning(
            "Aviso",
            "No hay productos en la venta."
        )
        return

    try:
        recibido = float(recibido_temporal) if recibido_temporal else 0
    except:
        messagebox.showerror(
            "Error",
            "Ingresa una cantidad válida."
        )
        return

    if recibido < total:
        messagebox.showerror(
            "Error",
            f"La cantidad recibida es insuficiente.\n"
            f"Falta: ${total - recibido:.2f}"
        )
        return

    cambio = recibido - total

    guardar_venta(
        ticket_actual,
        total
    )

    messagebox.showinfo(
        "✓ Venta Completada",
        f"Total: ${total:.2f}\n"
        f"Recibido: ${recibido:.2f}\n"
        f"Cambio: ${cambio:.2f}"
    )

    cancelar_venta()

    folio_label.configure(
        text=f"FOLIO: {obtener_siguiente_folio():06d}"
    )

def mostrar_reportes():
    """Muestra ventana de reportes"""
    ventana = ctk.CTkToplevel(app)

    ventana.title("Reporte de Ventas")
    ventana.geometry("600x500")

    titulo = ctk.CTkLabel(
        ventana,
        text="CORTE DE CAJA",
        font=("Arial", 24, "bold")
    )

    titulo.pack(pady=20)

    texto = ctk.CTkTextbox(
        ventana,
        width=500,
        height=300
    )

    texto.pack(pady=10)

    productos_reporte = obtener_corte_diario()

    texto.insert("end", "PRODUCTOS VENDIDOS\n\n")

    for producto, cantidad, total_producto in productos_reporte:
        texto.insert(
            "end",
            f"{producto}\n"
            f"Cantidad: {cantidad}\n"
            f"Total: ${total_producto:.2f}\n\n"
        )

    total_general = obtener_total_vendido()

    texto.insert(
        "end",
        f"\nTOTAL VENDIDO: ${total_general:.2f}"
    )

    texto.configure(state="disabled")

# =====================================
# VENTANA
# =====================================

crear_bd()

app = ctk.CTk()

app.title("Caja Registradora - Control por Teclado")
app.geometry("1000x700")

# =====================================
# TITULO Y FOLIO
# =====================================

frame_header = ctk.CTkFrame(app)
frame_header.pack(fill="x", padx=20, pady=15)

titulo = ctk.CTkLabel(
    frame_header,
    text="🛍️ CAJA REGISTRADORA",
    font=("Arial", 32, "bold")
)
titulo.pack(side="left", padx=10)

folio_label = ctk.CTkLabel(
    frame_header,
    text=f"FOLIO: {obtener_siguiente_folio():06d}",
    font=("Arial", 16, "bold"),
    text_color="orange"
)
folio_label.pack(side="right", padx=10)

# =====================================
# INSTRUCCIONES
# =====================================

frame_instrucciones = ctk.CTkFrame(app, fg_color="gray25")
frame_instrucciones.pack(fill="x", padx=20, pady=10)

instrucciones_text = ctk.CTkLabel(
    frame_instrucciones,
    text="⌨️  CONTROLES: [1-4] Productos  |  [Números] Dinero  |  [ENTER] Cobrar  |  [C] Cancelar  |  [BKSP] Quitar  |  [R] Reportes",
    font=("Arial", 12),
    text_color="lightblue"
)
instrucciones_text.pack(pady=8)

# =====================================
# PANEL PRINCIPAL
# =====================================

frame_principal = ctk.CTkFrame(app)
frame_principal.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=20
)

# =====================================
# PRODUCTOS (LADO IZQUIERDO)
# =====================================

frame_productos = ctk.CTkFrame(frame_principal)
frame_productos.pack(
    side="left",
    fill="y",
    padx=15,
    pady=10
)

ctk.CTkLabel(
    frame_productos,
    text="📦 PRODUCTOS",
    font=("Arial", 20, "bold")
).pack(pady=15)

botones_productos = {}
colores = ["#4CAF50", "#2196F3", "#FF9800", "#E91E63"]

for tecla, color in zip(sorted(productos.keys()), colores):
    datos = productos[tecla]
    nombre = datos["nombre"]
    precio = datos["precio"]
    
    boton = ctk.CTkButton(
        frame_productos,
        text=f"[{tecla}] {nombre}\n${precio}",
        width=180,
        height=60,
        font=("Arial", 14, "bold"),
        fg_color=color,
        command=lambda t=tecla: agregar_producto(t)
    )
    
    boton.pack(pady=15, padx=10)
    botones_productos[tecla] = boton

# =====================================
# TICKET (LADO DERECHO)
# =====================================

frame_ticket = ctk.CTkFrame(frame_principal)
frame_ticket.pack(
    side="right",
    fill="both",
    expand=True,
    padx=15,
    pady=10
)

ctk.CTkLabel(
    frame_ticket,
    text="🧾 TICKET ACTUAL",
    font=("Arial", 20, "bold")
).pack(pady=10)

ticket = ctk.CTkTextbox(
    frame_ticket,
    width=600,
    height=250,
    font=("Courier", 12)
)

ticket.pack(
    padx=15,
    pady=10,
    fill="both",
    expand=True
)

ticket.insert("end", "El ticket aparecerá aquí\n")
ticket.configure(state="disabled")

# =====================================
# TOTAL
# =====================================

total_label = ctk.CTkLabel(
    frame_ticket,
    text="TOTAL: $0",
    font=("Arial", 32, "bold"),
    text_color="lightgreen"
)

total_label.pack(pady=15)

# =====================================
# DINERO RECIBIDO
# =====================================

recibido_label = ctk.CTkLabel(
    frame_ticket,
    text="RECIBIDO: $0",
    font=("Arial", 24, "bold"),
    text_color="lightblue"
)

recibido_label.pack(pady=10)

# =====================================
# CAMBIO
# =====================================

cambio_label = ctk.CTkLabel(
    frame_ticket,
    text="CAMBIO: $0.00",
    font=("Arial", 24, "bold"),
    text_color="lightgreen"
)

cambio_label.pack(pady=15)

# =====================================
# BOTONES RÁPIDOS (VISUAL)
# =====================================

frame_rapidos = ctk.CTkFrame(frame_ticket)
frame_rapidos.pack(pady=15)

ctk.CTkButton(
    frame_rapidos,
    text="[ENTER] COBRAR",
    fg_color="green",
    width=140,
    height=40,
    command=cobrar
).pack(side="left", padx=8)

ctk.CTkButton(
    frame_rapidos,
    text="[C] CANCELAR",
    fg_color="red",
    width=140,
    height=40,
    command=cancelar_venta
).pack(side="left", padx=8)

ctk.CTkButton(
    frame_rapidos,
    text="[R] REPORTES",
    fg_color="orange",
    width=140,
    height=40,
    command=mostrar_reportes
).pack(side="left", padx=8)

# =====================================
# BINDINGS DE TECLADO
# =====================================

app.bind("<Key>", handle_numpad_input)

# =====================================
# INICIAR APP
# =====================================

app.mainloop()
