import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

# Función de Conexión a SQL Server
def obtener_conexion():
    try:
        # Configuración adaptada al servidor
        conexion = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=.\SQLEXPRESS;'  # Usa la instancia local detectada en SSMS
            'DATABASE=TiendaTecnologia;'
            'Trusted_Connection=yes;'
        )
        return conexion
    except Exception as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a la Base de Datos:\n{e}")
        return None

class AppTienda:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión de Ventas - Tienda de Tecnología")
        self.root.geometry("850x650")

        # Crear Cuaderno de Pestañas (Notebook)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Módulos exigidos por el proyecto
        self.tab_clientes = ttk.Frame(self.notebook)
        self.tab_ventas = ttk.Frame(self.notebook)
        self.tab_consultas = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_clientes, text="Módulo Clientes")
        self.notebook.add(self.tab_ventas, text="Módulo Ventas (Transaccional)")
        self.notebook.add(self.tab_consultas, text="Módulo Consultas (5.1 - 5.7)")

        self.construir_tab_clientes()
        self.construir_tab_ventas()
        self.construir_tab_consultas()

    # ----------------------------------------------------
    # MÓDULO A: CLIENTES
    # ----------------------------------------------------
    def construir_tab_clientes(self):
        frame = ttk.LabelFrame(self.tab_clientes, text="Registro / Actualización de Clientes", padding=15)
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text="ID Cliente (Solo para actualizar):").grid(row=0, column=0, sticky="w", pady=5)
        self.txt_cli_id = ttk.Entry(frame)
        self.txt_cli_id.grid(row=0, column=1, pady=5, sticky="w")

        ttk.Label(frame, text="Nombre Completo:").grid(row=1, column=0, sticky="w", pady=5)
        self.txt_cli_nombre = ttk.Entry(frame, width=40)
        self.txt_cli_nombre.grid(row=1, column=1, pady=5, sticky="w")

        ttk.Label(frame, text="Correo Electrónico:").grid(row=2, column=0, sticky="w", pady=5)
        self.txt_cli_correo = ttk.Entry(frame, width=40)
        self.txt_cli_correo.grid(row=2, column=1, pady=5, sticky="w")

        ttk.Label(frame, text="Teléfono:").grid(row=3, column=0, sticky="w", pady=5)
        self.txt_cli_telefono = ttk.Entry(frame, width=40)
        self.txt_cli_telefono.grid(row=3, column=1, pady=5, sticky="w")

        btn_guardar = ttk.Button(frame, text="Guardar Cliente", command=self.guardar_cliente)
        btn_guardar.grid(row=4, column=0, columnspan=2, pady=15)

    def guardar_cliente(self):
        cid = self.txt_cli_id.get().strip()
        nombre = self.txt_cli_nombre.get().strip()
        correo = self.txt_cli_correo.get().strip()
        telefono = self.txt_cli_telefono.get().strip()

        if not nombre:
            messagebox.showwarning("Atención", "El nombre del cliente es obligatorio.")
            return

        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()

        try:
            if cid: # Actualizar
                cursor.execute(
                    "UPDATE Cliente SET nombre=?, correo=?, telefono=? WHERE id_cliente=?",
                    (nombre, correo if correo else None, telefono if telefono else None, cid)
                )
                messagebox.showinfo("Éxito", "Cliente actualizado correctamente.")
            else: # Insertar
                cursor.execute(
                    "INSERT INTO Cliente (nombre, correo, telefono) VALUES (?, ?, ?)",
                    (nombre, correo if correo else None, telefono if telefono else None)
                )
                messagebox.showinfo("Éxito", "Cliente registrado correctamente.")
            conn.commit()
            self.limpiar_form_clientes()
            self.cargar_combos_ventas()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error SQL", f"No se pudo guardar el cliente: {e}")
        finally:
            conn.close()

    def limpiar_form_clientes(self):
        self.txt_cli_id.delete(0, tk.END)
        self.txt_cli_nombre.delete(0, tk.END)
        self.txt_cli_correo.delete(0, tk.END)
        self.txt_cli_telefono.delete(0, tk.END)

    # ----------------------------------------------------
    # MÓDULO B: VENTAS (TRANSACCIONAL)
    # ----------------------------------------------------
    def construir_tab_ventas(self):
        frame = ttk.LabelFrame(self.tab_ventas, text="Registrar Nueva Venta", padding=15)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Cliente:").grid(row=0, column=0, sticky="w", pady=5)
        self.cb_cliente = ttk.Combobox(frame, state="readonly", width=40)
        self.cb_cliente.grid(row=0, column=1, pady=5, sticky="w")

        ttk.Label(frame, text="Empleado:").grid(row=1, column=0, sticky="w", pady=5)
        self.cb_empleado = ttk.Combobox(frame, state="readonly", width=40)
        self.cb_empleado.grid(row=1, column=1, pady=5, sticky="w")

        ttk.Label(frame, text="Producto:").grid(row=2, column=0, sticky="w", pady=5)
        self.cb_producto = ttk.Combobox(frame, state="readonly", width=40)
        self.cb_producto.grid(row=2, column=1, pady=5, sticky="w")

        ttk.Label(frame, text="Cantidad:").grid(row=3, column=0, sticky="w", pady=5)
        self.sp_cantidad = ttk.Spinbox(frame, from_=1, to=100, width=10)
        self.sp_cantidad.grid(row=3, column=1, sticky="w", pady=5)
        self.sp_cantidad.set(1)

        btn_agregar = ttk.Button(frame, text="Agregar a la Venta", command=self.agregar_detalle_local)
        btn_agregar.grid(row=4, column=0, columnspan=2, pady=10)

        # Tabla temporal de ítems agregados (Sintaxis grid corregida)
        self.tree_cart = ttk.Treeview(frame, columns=("ID", "Producto", "Cantidad", "Precio", "Subtotal"), show="headings", height=5)
        self.tree_cart.heading("ID", text="ID Prod")
        self.tree_cart.heading("Producto", text="Producto")
        self.tree_cart.heading("Cantidad", text="Cantidad")
        self.tree_cart.heading("Precio", text="Precio Unit.")
        self.tree_cart.heading("Subtotal", text="Subtotal")
        self.tree_cart.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)

        btn_procesar = ttk.Button(frame, text="PROCESAR VENTA (TRANSACCIÓN EN BD)", command=self.procesar_venta_transaccional)
        btn_procesar.grid(row=6, column=0, columnspan=2, pady=15)

        self.cart_items = []
        self.cargar_combos_ventas()

    def cargar_combos_ventas(self):
        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT id_cliente, nombre FROM Cliente")
            self.dict_clientes = {f"{r[0]} - {r[1]}": r[0] for r in cursor.fetchall()}
            self.cb_cliente['values'] = list(self.dict_clientes.keys())

            cursor.execute("SELECT id_empleado, nombre FROM Empleado")
            self.dict_empleados = {f"{r[0]} - {r[1]}": r[0] for r in cursor.fetchall()}
            self.cb_empleado['values'] = list(self.dict_empleados.keys())

            cursor.execute("SELECT id_producto, nombre, precio_actual FROM Producto")
            self.dict_productos = {f"{r[0]} - {r[1]} (Q{r[2]})": (r[0], r[1], float(r[2])) for r in cursor.fetchall()}
            self.cb_producto['values'] = list(self.dict_productos.keys())
        except Exception as e:
            print("Error cargando desplegables:", e)
        finally:
            conn.close()

    def agregar_detalle_local(self):
        prod_sel = self.cb_producto.get()
        if not prod_sel: return

        pid, pnombre, precio = self.dict_productos[prod_sel]
        cant = int(self.sp_cantidad.get())
        subtotal = cant * precio

        self.cart_items.append((pid, cant, precio))
        self.tree_cart.insert("", tk.END, values=(pid, pnombre, cant, f"Q{precio:.2f}", f"Q{subtotal:.2f}"))

    def procesar_venta_transaccional(self):
        cli_sel = self.cb_cliente.get()
        emp_sel = self.cb_empleado.get()

        if not cli_sel or not emp_sel or not self.cart_items:
            messagebox.showwarning("Atención", "Debe seleccionar Cliente, Empleado y al menos un Producto.")
            return

        id_cliente = self.dict_clientes[cli_sel]
        id_empleado = self.dict_empleados[emp_sel]

        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()

        try:
            # INICIO DE TRANSACCIÓN MANUAL
            conn.autocommit = False

            # 1. Insertar Cabecera de Venta
            cursor.execute(
                "INSERT INTO Venta (id_cliente, id_empleado) OUTPUT INSERTED.id_venta VALUES (?, ?)",
                (id_cliente, id_empleado)
            )
            id_venta = cursor.fetchone()[0]

            # 2. Insertar Detalles de Venta
            for pid, cant, precio in self.cart_items:
                cursor.execute(
                    "INSERT INTO DetalleVenta (id_venta, id_producto, cantidad, precio_unitario) VALUES (?, ?, ?, ?)",
                    (id_venta, pid, cant, precio)
                )

            # CONFIRMAR TRANSACCIÓN SI TODO SALIÓ BIEN
            conn.commit()
            messagebox.showinfo("Éxito Transaccional", f"¡Venta #{id_venta} registrada correctamente con COMMIT!")
            self.cart_items.clear()
            for i in self.tree_cart.get_children(): self.tree_cart.delete(i)

        except Exception as e:
            # REVERTIR CAMBIOS SI OCURRIÓ ALGÚN ERROR
            conn.rollback()
            messagebox.showerror("Rollback Activado", f"Ocurrió un error. Se ejecutó ROLLBACK para evitar ventas incompletas:\n{e}")

        finally:
            conn.close()

    # ----------------------------------------------------
    # MÓDULO C: CONSULTAS (5.1 - 5.7)
    # ----------------------------------------------------
    def construir_tab_consultas(self):
        frame = ttk.Frame(self.tab_consultas, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Seleccione Consulta SQL:").pack(anchor="w")
        
        self.cb_consulta = ttk.Combobox(frame, state="readonly", width=65, values=[
            "5.1 Historial de ventas",
            "5.2 Compras realizadas por cliente",
            "5.3 Resumen de ventas por empleado (> Q 10,000)",
            "5.4 Productos más vendidos (> 10 unidades)",
            "5.5 Ingresos por categoría (> Q 5,000)",
            "5.6 Reporte por cliente y categoría (> Q 2,000)",
            "5.7 Clientes con compras superiores al promedio"
        ])
        self.cb_consulta.pack(fill="x", pady=5)
        self.cb_consulta.current(0)

        btn_ejecutar = ttk.Button(frame, text="Ejecutar Consulta", command=self.ejecutar_consulta_sql)
        btn_ejecutar.pack(pady=5)

        # Tabla para visualizar resultados
        self.tree_res = ttk.Treeview(frame, show="headings")
        self.tree_res.pack(fill="both", expand=True, pady=10)

    def ejecutar_consulta_sql(self):
        idx = self.cb_consulta.current() + 1
        
        queries = {
            1: """SELECT v.id_venta, v.fecha, c.nombre AS cliente, e.nombre AS empleado, SUM(d.cantidad * d.precio_unitario) AS importe_total
                  FROM Venta v INNER JOIN Cliente c ON v.id_cliente = c.id_cliente
                  INNER JOIN Empleado e ON v.id_empleado = e.id_empleado
                  INNER JOIN DetalleVenta d ON v.id_venta = d.id_venta
                  GROUP BY v.id_venta, v.fecha, c.nombre, e.nombre ORDER BY importe_total DESC;""",
            
            2: """SELECT c.nombre AS cliente, COUNT(DISTINCT v.id_venta) AS cantidad_ventas, SUM(d.cantidad * d.precio_unitario) AS importe_total
                  FROM Cliente c INNER JOIN Venta v ON c.id_cliente = v.id_cliente
                  INNER JOIN DetalleVenta d ON v.id_venta = d.id_venta
                  GROUP BY c.id_cliente, c.nombre ORDER BY importe_total DESC;""",
            
            3: """SELECT e.nombre AS empleado, COUNT(DISTINCT v.id_venta) AS ventas_registradas, SUM(d.cantidad * d.precio_unitario) AS importe_total
                  FROM Empleado e INNER JOIN Venta v ON e.id_empleado = v.id_empleado
                  INNER JOIN DetalleVenta d ON v.id_venta = d.id_venta
                  GROUP BY e.id_empleado, e.nombre HAVING SUM(d.cantidad * d.precio_unitario) > 10000 ORDER BY importe_total DESC;""",
            
            4: """SELECT p.nombre AS producto, cat.nombre AS categoria, SUM(d.cantidad) AS total_unidades, SUM(d.cantidad * d.precio_unitario) AS importe_total
                  FROM Producto p INNER JOIN Categoria cat ON p.id_categoria = cat.id_categoria
                  INNER JOIN DetalleVenta d ON p.id_producto = d.id_producto
                  GROUP BY p.id_producto, p.nombre, cat.nombre HAVING SUM(d.cantidad) > 10 ORDER BY total_unidades DESC;""",
            
            5: """SELECT cat.nombre AS categoria, COUNT(DISTINCT p.id_producto) AS productos_diferentes, SUM(d.cantidad) AS total_unidades, SUM(d.cantidad * d.precio_unitario) AS importe_total
                  FROM Categoria cat INNER JOIN Producto p ON cat.id_categoria = p.id_categoria
                  INNER JOIN DetalleVenta d ON p.id_producto = d.id_producto
                  GROUP BY cat.id_categoria, cat.nombre HAVING SUM(d.cantidad * d.precio_unitario) > 5000 ORDER BY importe_total DESC;""",
            
            6: """SELECT c.nombre AS cliente, cat.nombre AS categoria, COUNT(DISTINCT v.id_venta) AS cantidad_ventas, SUM(d.cantidad) AS unidades_adquiridas, SUM(d.cantidad * d.precio_unitario) AS importe_total
                  FROM Cliente c INNER JOIN Venta v ON c.id_cliente = v.id_cliente
                  INNER JOIN DetalleVenta d ON v.id_venta = d.id_venta
                  INNER JOIN Producto p ON d.id_producto = p.id_producto
                  INNER JOIN Categoria cat ON p.id_categoria = cat.id_categoria
                  GROUP BY c.id_cliente, c.nombre, cat.id_categoria, cat.nombre HAVING SUM(d.cantidad * d.precio_unitario) > 2000 ORDER BY importe_total DESC;""",
            
            7: """SELECT c.nombre AS cliente, COUNT(DISTINCT v.id_venta) AS cantidad_ventas, SUM(d.cantidad * d.precio_unitario) AS importe_total_acumulado
                  FROM Cliente c INNER JOIN Venta v ON c.id_cliente = v.id_cliente
                  INNER JOIN DetalleVenta d ON v.id_venta = d.id_venta
                  GROUP BY c.id_cliente, c.nombre
                  HAVING SUM(d.cantidad * d.precio_unitario) > (
                      SELECT AVG(total_venta) FROM (
                          SELECT SUM(cantidad * precio_unitario) AS total_venta FROM DetalleVenta GROUP BY id_venta
                      ) AS resumen
                  ) ORDER BY importe_total_acumulado DESC;"""
        }

        sql = queries[idx]
        conn = obtener_conexion()
        if not conn: return
        cursor = conn.cursor()

        try:
            cursor.execute(sql)
            col_names = [column[0] for column in cursor.description]
            rows = cursor.fetchall()

            # Limpiar tabla visual
            self.tree_res.delete(*self.tree_res.get_children())
            self.tree_res["columns"] = col_names

            for col in col_names:
                self.tree_res.heading(col, text=col)
                self.tree_res.column(col, width=120)

            for row in rows:
                self.tree_res.insert("", tk.END, values=[str(item) for item in row])

        except Exception as e:
            messagebox.showerror("Error de Ejecución SQL", f"No se pudo ejecutar la consulta:\n{e}")
        finally:
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = AppTienda(root)
    root.mainloop()