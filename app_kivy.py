"""Interfaz móvil de CajaRegistradora.

La base de datos se copia al almacenamiento privado de la aplicación en Android
la primera vez que se inicia. En escritorio se puede ejecutar directamente con
``python app_kivy.py`` y conserva ``ventas.db`` en el directorio del proyecto.
"""

import os
import shutil
from pathlib import Path

from kivy.app import App
from kivy.metrics import dp
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

import database


PRODUCTOS = {
    "Victoria": 48,
    "Corona": 48,
    "Pall Mall Azul": 7,
    "Marlboro Rojo": 7,
}


class CajaRegistradoraApp(App):
    title = "Caja Registradora"

    def build(self):
        self._preparar_base_de_datos()
        database.crear_bd()
        self.ticket_actual = {}
        self.total = 0.0

        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        root.add_widget(Label(text="CAJA REGISTRADORA", font_size="24sp", size_hint_y=None, height=dp(42)))
        self.folio_label = Label(size_hint_y=None, height=dp(30))
        root.add_widget(self.folio_label)

        contenido = BoxLayout(spacing=dp(8))
        productos = BoxLayout(orientation="vertical", spacing=dp(6), size_hint_x=0.42)
        productos.add_widget(Label(text="PRODUCTOS", size_hint_y=None, height=dp(32)))
        for nombre, precio in PRODUCTOS.items():
            boton = Button(text=f"{nombre}\n${precio}", font_size="16sp")
            boton.bind(on_release=lambda _, n=nombre, p=precio: self.agregar_producto(n, p))
            productos.add_widget(boton)
        contenido.add_widget(productos)

        panel = BoxLayout(orientation="vertical", spacing=dp(6))
        panel.add_widget(Label(text="TICKET ACTUAL", size_hint_y=None, height=dp(32)))
        self.ticket_label = Label(text="", halign="left", valign="top", size_hint_y=None)
        self.ticket_label.bind(texture_size=self.ticket_label.setter("size"))
        ticket_scroll = ScrollView()
        ticket_scroll.add_widget(self.ticket_label)
        panel.add_widget(ticket_scroll)
        self.total_label = Label(size_hint_y=None, height=dp(34), font_size="20sp")
        panel.add_widget(self.total_label)

        self.recibido_input = TextInput(
            hint_text="Recibido", input_filter="float", multiline=False,
            input_type="number", size_hint_y=None, height=dp(42),
        )
        self.recibido_input.bind(text=lambda *_: self.actualizar_cambio())
        panel.add_widget(self.recibido_input)
        self.cambio_label = Label(size_hint_y=None, height=dp(30))
        panel.add_widget(self.cambio_label)

        efectivo = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(4))
        for monto in (100, 200, 500, 1000):
            boton = Button(text=f"${monto}")
            boton.bind(on_release=lambda _, m=monto: self.poner_efectivo(m))
            efectivo.add_widget(boton)
        panel.add_widget(efectivo)

        acciones = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(5))
        cobrar = Button(text="COBRAR", background_color=(0.1, 0.65, 0.2, 1))
        cobrar.bind(on_release=lambda *_: self.cobrar())
        cancelar = Button(text="CANCELAR", background_color=(0.75, 0.15, 0.15, 1))
        cancelar.bind(on_release=lambda *_: self.cancelar_venta())
        reportes = Button(text="REPORTES", background_color=(0.9, 0.55, 0.1, 1))
        reportes.bind(on_release=lambda *_: self.mostrar_reportes())
        for boton in (cobrar, cancelar, reportes):
            acciones.add_widget(boton)
        panel.add_widget(acciones)
        contenido.add_widget(panel)
        root.add_widget(contenido)

        self.actualizar_vista()
        return root

    def _preparar_base_de_datos(self):
        if platform == "android":
            destino = Path(self.user_data_dir) / "ventas.db"
            origen = Path(__file__).with_name("ventas.db")
            if not destino.exists() and origen.exists():
                shutil.copy2(origen, destino)
            os.environ["CAJA_DB_PATH"] = str(destino)
            database.DB_PATH = str(destino)
        else:
            database.DB_PATH = str(Path(__file__).with_name("ventas.db"))

    def agregar_producto(self, nombre, precio):
        datos = self.ticket_actual.setdefault(nombre, {"precio": precio, "cantidad": 0})
        datos["cantidad"] += 1
        self.total += precio
        self.actualizar_vista()

    def quitar_producto(self, nombre):
        if nombre not in self.ticket_actual:
            return
        datos = self.ticket_actual[nombre]
        datos["cantidad"] -= 1
        self.total -= datos["precio"]
        if datos["cantidad"] <= 0:
            del self.ticket_actual[nombre]
        self.total = max(0.0, self.total)
        self.actualizar_vista()

    def actualizar_vista(self):
        lineas = ["========================", "         TICKET", "========================", ""]
        for nombre, datos in self.ticket_actual.items():
            lineas.append(f"{nombre} x{datos['cantidad']}  ${datos['cantidad'] * datos['precio']:.2f}")
        lineas.extend(["", "------------------------", f"TOTAL: ${self.total:.2f}"])
        self.ticket_label.text = "\n".join(lineas)
        self.total_label.text = f"TOTAL: ${self.total:.2f}"
        self.folio_label.text = f"FOLIO: {database.obtener_siguiente_folio():06d}"
        self.actualizar_cambio()

    def actualizar_cambio(self):
        try:
            recibido = float(self.recibido_input.text or 0)
        except ValueError:
            recibido = 0
        cambio = recibido - self.total if recibido >= self.total else 0
        self.cambio_label.text = f"CAMBIO: ${cambio:.2f}"

    def poner_efectivo(self, cantidad):
        self.recibido_input.text = str(cantidad)
        self.actualizar_cambio()

    def cancelar_venta(self):
        self.ticket_actual.clear()
        self.total = 0.0
        self.recibido_input.text = ""
        self.actualizar_vista()

    def cobrar(self):
        if self.total <= 0:
            self.mostrar_aviso("Aviso", "No hay productos en la venta.")
            return
        try:
            recibido = float(self.recibido_input.text)
        except ValueError:
            self.mostrar_aviso("Error", "Ingresa una cantidad válida.")
            return
        if recibido < self.total:
            self.mostrar_aviso("Error", "La cantidad recibida es insuficiente.")
            return
        cambio = recibido - self.total
        database.guardar_venta(self.ticket_actual, self.total)
        self.mostrar_aviso("Venta completada", f"Total: ${self.total:.2f}\nRecibido: ${recibido:.2f}\nCambio: ${cambio:.2f}")
        self.cancelar_venta()

    def mostrar_reportes(self):
        productos = database.obtener_corte_diario()
        lineas = ["CORTE DE CAJA", "", "PRODUCTOS VENDIDOS", ""]
        for producto, cantidad, total_producto in productos:
            lineas.append(f"{producto}\nCantidad: {cantidad}\nTotal: ${total_producto:.2f}\n")
        lineas.append(f"TOTAL VENDIDO: ${database.obtener_total_vendido():.2f}")
        self.mostrar_aviso("Reporte de ventas", "\n".join(lineas))

    def mostrar_aviso(self, titulo, mensaje):
        Popup(title=titulo, content=Label(text=mensaje), size_hint=(0.9, 0.7)).open()


if __name__ == "__main__":
    CajaRegistradoraApp().run()
