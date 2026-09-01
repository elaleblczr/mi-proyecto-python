from database import obtener_ventas

ventas = obtener_ventas()

print("\n===== VENTAS REGISTRADAS =====\n")

for venta in ventas:

    print(f"Folio: {venta[0]}")
    print(f"Fecha: {venta[1]}")
    print(f"Total: ${venta.2f}")
    print("-" * 30)