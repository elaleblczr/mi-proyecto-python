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
    "Victoria": 48,
    "Corona": 48,
    "Pall Mall Azul": 7,
    "Marlboro Rojo": 7
}

ticket_actual = {}
total = 0

# =====================================
# FUNCIONES
# =====================================

def agregar_producto(nombre, precio):
    global total

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

def quitar_producto(nombre):

    global total

    if nombre not in ticket_actual:
        return

    precio = ticket_actual[nombre]["precio"]

    ticket_actual[nombre]["cantidad"] -= 1

    total -= precio

    if ticket_actual[nombre]["cantidad"] <= 0:
        del ticket_actual[nombre]

    if total < 0:
        total = 0

    actualizar_ticket()
    calcular_cambio()

def actualizar_ticket():

    ticket.delete("1.0", "end")

    ticket.insert("end", "========================\n")
    ticket.insert("end", "         TICKET\n")
    ticket.insert("end", "========================\n\n")

    for producto, datos in ticket_actual.items():

        cantidad = datos["cantidad"]
        precio = datos["precio"]
        subtotal = cantidad * precio

        ticket.insert(
            "end",
            f"{producto:<20} x{cantidad:<3} ${subtotal}\n"
        )

    ticket.insert("end", "\n------------------------\n")
    ticket.insert("end", f"TOTAL: ${total}")

    total_label.configure(
        text=f"TOTAL: ${total}"
    )


def calcular_cambio(event=None):

    try:

        recibido = float(recibido_entry.get())

        if recibido >= total:

            cambio = recibido - total

            cambio_label.configure(
                text=f"CAMBIO: ${cambio:.2f}"
            )

        else:

            cambio_label.configure(
                text="CAMBIO: $0.00"
            )

    except:

        cambio_label.configure(
            text="CAMBIO: $0.00"
        )


def poner_efectivo(cantidad):

    recibido_entry.delete(0, "end")
    recibido_entry.insert(0, str(cantidad))

    calcular_cambio()

def cancelar_venta():

    global total

    ticket_actual.clear()

    total = 0

    ticket.delete("1.0", "end")

    recibido_entry.delete(0, "end")

    total_label.configure(
        text="TOTAL: $0"
    )

    cambio_label.configure(
        text="CAMBIO: $0.00"
    )


def cobrar():

    global total

    if total == 0:

        messagebox.showwarning(
            "Aviso",
            "No hay productos en la venta."
        )
        return

    try:

        recibido = float(recibido_entry.get())

    except:

        messagebox.showerror(
            "Error",
            "Ingresa una cantidad válida."
        )
        return

    if recibido < total:

        messagebox.showerror(
            "Error",
            "La cantidad recibida es insuficiente."
        )
        return

    cambio = recibido - total

    guardar_venta(
        ticket_actual,
        total
    )

    messagebox.showinfo(
        "Venta completada",
        f"Total: ${total:.2f}\n"
        f"Recibido: ${recibido:.2f}\n"
        f"Cambio: ${cambio:.2f}"
    )

    cancelar_venta()

    folio_label.configure(
        text=f"FOLIO: {obtener_siguiente_folio():06d}"
    )

def mostrar_reportes():

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

    productos = obtener_corte_diario()

    texto.insert("end", "PRODUCTOS VENDIDOS\n\n")

    for producto, cantidad, total_producto in productos:

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

app.title("Caja Registradora")
app.geometry("1100x650")

# =====================================
# TITULO
# =====================================

titulo = ctk.CTkLabel(
    app,
    text="CAJA REGISTRADORA",
    font=("Arial", 32, "bold")
)

titulo.pack(pady=20)

folio_label = ctk.CTkLabel(
    app,
    text=f"FOLIO: {obtener_siguiente_folio():06d}",
    font=("Arial", 18, "bold")
)

folio_label.pack()

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
# PRODUCTOS
# =====================================

frame_productos = ctk.CTkFrame(frame_principal)
frame_productos.pack(
    side="left",
    fill="y",
    padx=10,
    pady=10
)

ctk.CTkLabel(
    frame_productos,
    text="PRODUCTOS",
    font=("Arial", 22, "bold")
).pack(pady=10)

for nombre, precio in productos.items():

    boton = ctk.CTkButton(
        frame_productos,
        text=f"{nombre} - ${precio}",
        width=180,
        height=45,
        command=lambda n=nombre, p=precio: agregar_producto(n, p)
    )

    boton.pack(
        pady=10,
        padx=15
    )

# =====================================
# TICKET
# =====================================

frame_ticket = ctk.CTkFrame(frame_principal)
frame_ticket.pack(
    side="right",
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

ctk.CTkLabel(
    frame_ticket,
    text="TICKET ACTUAL",
    font=("Arial", 24, "bold")
).pack(pady=10)

ticket = ctk.CTkTextbox(
    frame_ticket,
    width=600,
    height=250
)

ticket.pack(
    padx=20,
    pady=10
)

# =====================================
# TOTAL
# =====================================

total_label = ctk.CTkLabel(
    frame_ticket,
    text="TOTAL: $0",
    font=("Arial", 28, "bold")
)

total_label.pack(pady=10)

# =====================================
# RECIBIDO
# =====================================

ctk.CTkLabel(
    frame_ticket,
    text="RECIBIDO",
    font=("Arial", 18, "bold")
).pack(pady=(10, 5))

recibido_entry = ctk.CTkEntry(
    frame_ticket,
    width=250,
    height=40,
    font=("Arial", 18)
)

recibido_entry.pack()

recibido_entry.bind(
    "<KeyRelease>",
    calcular_cambio
)

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
# BOTONES RAPIDOS
# =====================================

frame_efectivo = ctk.CTkFrame(frame_ticket)
frame_efectivo.pack(pady=10)

for monto in [100, 200, 500, 1000]:

    ctk.CTkButton(
        frame_efectivo,
        text=f"${monto}",
        width=80,
        command=lambda m=monto: poner_efectivo(m)
    ).pack(
        side="left",
        padx=5
    )

# =====================================
# BOTONES PRINCIPALES
# =====================================

frame_botones = ctk.CTkFrame(frame_ticket)
frame_botones.pack(pady=20)

cobrar_btn = ctk.CTkButton(
    frame_botones,
    text="COBRAR",
    fg_color="green",
    width=150,
    height=45,
    command=cobrar
)

cobrar_btn.pack(
    side="left",
    padx=10
)

cancelar_btn = ctk.CTkButton(
    frame_botones,
    text="CANCELAR",
    fg_color="red",
    width=150,
    height=45,
    command=cancelar_venta
)

cancelar_btn.pack(
    side="left",
    padx=10
)

reportes_btn = ctk.CTkButton(
    frame_botones,
    text="REPORTES",
    fg_color="orange",
    command=mostrar_reportes
)

reportes_btn.pack(
    side="left",
    padx=10
)

# =====================================
# INICIAR APP
# =====================================

app.mainloop()