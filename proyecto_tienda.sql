-- ============================================================
-- Proyecto: Sistema de Gestión de Ventas de una Tienda de Tecnología
-- Cristian Josué Cruz López 7690-24-7788
-- Base de datos I
-- ============================================================

-- Si la base de datos ya fue creada en el intento anterior, nos aseguramos de usarla o recrearla
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'TiendaTecnologia')
BEGIN
    CREATE DATABASE TiendaTecnologia;
END
GO

USE TiendaTecnologia;
GO

-- Eliminar tablas previas en orden correcto por si existen parcialmente
IF OBJECT_ID('dbo.DetalleVenta', 'U') IS NOT NULL DROP TABLE dbo.DetalleVenta;
IF OBJECT_ID('dbo.Venta', 'U') IS NOT NULL DROP TABLE dbo.Venta;
IF OBJECT_ID('dbo.Producto', 'U') IS NOT NULL DROP TABLE dbo.Producto;
IF OBJECT_ID('dbo.Categoria', 'U') IS NOT NULL DROP TABLE dbo.Categoria;
IF OBJECT_ID('dbo.Empleado', 'U') IS NOT NULL DROP TABLE dbo.Empleado;
IF OBJECT_ID('dbo.Cliente', 'U') IS NOT NULL DROP TABLE dbo.Cliente;
GO

-- 1. CREACIÓN DE TABLAS E INTEGRIDAD DE DATOS

CREATE TABLE Categoria (
    id_categoria INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Producto (
    id_producto INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    precio_actual DECIMAL(10,2) NOT NULL CHECK (precio_actual >= 0),
    id_categoria INT NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES Categoria(id_categoria) ON DELETE NO ACTION
);

CREATE TABLE Cliente (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    correo VARCHAR(150) UNIQUE NULL,
    telefono VARCHAR(20) NULL
);

CREATE TABLE Empleado (
    id_empleado INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    puesto VARCHAR(100) NOT NULL
);

CREATE TABLE Venta (
    id_venta INT IDENTITY(1,1) PRIMARY KEY,
    fecha DATETIME NOT NULL DEFAULT GETDATE(),
    id_cliente INT NOT NULL,
    id_empleado INT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente) ON DELETE NO ACTION,
    FOREIGN KEY (id_empleado) REFERENCES Empleado(id_empleado) ON DELETE NO ACTION
);

CREATE TABLE DetalleVenta (
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL CHECK (precio_unitario >= 0),
    PRIMARY KEY (id_venta, id_producto),
    FOREIGN KEY (id_venta) REFERENCES Venta(id_venta) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES Producto(id_producto) ON DELETE NO ACTION
);
GO

-- CREACIÓN DE ÍNDICES ADICIONALES
CREATE INDEX IX_Venta_Fecha ON Venta(fecha);
CREATE INDEX IX_Venta_Cliente ON Venta(id_cliente);
GO

-- 2. INSERCIÓN DE DATOS DE PRUEBA

-- Empleados (Min 4)
INSERT INTO Empleado (nombre, puesto) VALUES 
('Luis Gómez', 'Vendedor'),
('Marta López', 'Vendedora'),
('Carlos Ruiz', 'Cajero'),
('Ana Morales', 'Gerente de Ventas');

-- Categorías (Min 5)
INSERT INTO Categoria (nombre) VALUES 
('Periféricos'), 
('Pantallas'), 
('Almacenamiento'), 
('Laptops'), 
('Componentes');

-- Productos (Min 15)
INSERT INTO Producto (nombre, precio_actual, id_categoria) VALUES 
('Teclado Mecánico RGB', 150.00, 1),
('Mouse Inalámbrico', 75.00, 1),
('Audífonos Gamer', 300.00, 1),
('Monitor 27 IPS 144Hz', 1200.00, 2),
('Monitor 24 60Hz', 650.00, 2),
('Disco Duro Externo 2TB', 350.00, 3),
('SSD NVMe 1TB', 450.00, 3),
('Memoria USB 64GB', 40.00, 3),
('Laptop Gamer I7 16GB', 6500.00, 4),
('Laptop Oficina I5 8GB', 3800.00, 4),
('MacBook Air M2', 7200.00, 4),
('Tarjeta de Video RTX 4060', 2800.00, 5),
('Procesador Intel i7 13th', 2200.00, 5),
('Memoria RAM DDR4 16GB', 280.00, 5),
('Fuente de Poder 750W 80+', 450.00, 5);

-- Clientes
INSERT INTO Cliente (nombre, correo, telefono) VALUES 
('Ana Pérez', 'ana.perez@email.com', '555-0101'),
('Carlos Díaz', 'carlos.diaz@email.com', '555-0102'),
('María Rodríguez', 'maria.rodriguez@email.com', '555-0103'),
('Jorge Hernández', 'jorge.h@email.com', '555-0104');

-- Ventas y Detalle de Ventas
INSERT INTO Venta (fecha, id_cliente, id_empleado) VALUES 
('2026-09-10', 1, 1),
('2026-09-11', 2, 2),
('2026-09-12', 1, 2),
('2026-09-13', 3, 1),
('2026-09-14', 1, 1);

INSERT INTO DetalleVenta (id_venta, id_producto, cantidad, precio_unitario) VALUES 
(1, 1, 2, 150.00),
(1, 2, 1, 75.00),
(2, 9, 2, 6500.00),
(3, 4, 1, 1200.00),
(4, 11, 2, 7200.00),
(5, 1, 12, 150.00),
(5, 4, 5, 1200.00);
GO

-- 3. CONSULTAS SQL SOLICITADAS 

-- 5.1 Historial de ventas
SELECT v.id_venta, v.fecha, c.nombre AS cliente, e.nombre AS empleado, 
       SUM(d.cantidad * d.precio_unitario) AS importe_total
FROM Venta v
INNER JOIN Cliente c ON v.id_cliente = c.id_cliente
INNER JOIN Empleado e ON v.id_empleado = e.id_empleado
INNER JOIN DetalleVenta d ON v.id_venta = d.id_venta
GROUP BY v.id_venta, v.fecha, c.nombre, e.nombre
ORDER BY importe_total DESC;

-- 5.2 Compras realizadas por cliente
SELECT c.nombre AS cliente, COUNT(DISTINCT v.id_venta) AS cantidad_ventas, 
       SUM(d.cantidad * d.precio_unitario) AS importe_total
FROM Cliente c
INNER JOIN Venta v ON c.id_cliente = v.id_cliente
INNER JOIN DetalleVenta d ON v.id_venta = d.id_venta
GROUP BY c.id_cliente, c.nombre
ORDER BY importe_total DESC;

-- 5.3 Resumen de ventas por empleado (> Q 10,000)
SELECT e.nombre AS empleado, COUNT(DISTINCT v.id_venta) AS ventas_registradas, 
       SUM(d.cantidad * d.precio_unitario) AS importe_total
FROM Empleado e
INNER JOIN Venta v ON e.id_empleado = v.id_empleado
INNER JOIN DetalleVenta d ON v.id_venta = d.id_venta
GROUP BY e.id_empleado, e.nombre
HAVING SUM(d.cantidad * d.precio_unitario) > 10000
ORDER BY importe_total DESC;

-- 5.4 Productos más vendidos (> 10 unidades)
SELECT p.nombre AS producto, cat.nombre AS categoria, 
       SUM(d.cantidad) AS total_unidades, 
       SUM(d.cantidad * d.precio_unitario) AS importe_total
FROM Producto p
INNER JOIN Categoria cat ON p.id_categoria = cat.id_categoria
INNER JOIN DetalleVenta d ON p.id_producto = d.id_producto
GROUP BY p.id_producto, p.nombre, cat.nombre
HAVING SUM(d.cantidad) > 10
ORDER BY total_unidades DESC;

-- 5.5 Ingresos por categoría (> Q 5,000)
SELECT cat.nombre AS categoria, 
       COUNT(DISTINCT p.id_producto) AS productos_diferentes,
       SUM(d.cantidad) AS total_unidades, 
       SUM(d.cantidad * d.precio_unitario) AS importe_total
FROM Categoria cat
INNER JOIN Producto p ON cat.id_categoria = p.id_categoria
INNER JOIN DetalleVenta d ON p.id_producto = d.id_producto
GROUP BY cat.id_categoria, cat.nombre
HAVING SUM(d.cantidad * d.precio_unitario) > 5000
ORDER BY importe_total DESC;

-- 5.6 Reporte por cliente y categoría (> Q 2,000)
SELECT c.nombre AS cliente, cat.nombre AS categoria, 
       COUNT(DISTINCT v.id_venta) AS cantidad_ventas,
       SUM(d.cantidad) AS unidades_adquiridas, 
       SUM(d.cantidad * d.precio_unitario) AS importe_total
FROM Cliente c
INNER JOIN Venta v ON c.id_cliente = v.id_cliente
INNER JOIN DetalleVenta d ON v.id_venta = d.id_venta
INNER JOIN Producto p ON d.id_producto = p.id_producto
INNER JOIN Categoria cat ON p.id_categoria = cat.id_categoria
GROUP BY c.id_cliente, c.nombre, cat.id_categoria, cat.nombre
HAVING SUM(d.cantidad * d.precio_unitario) > 2000
ORDER BY importe_total DESC;

-- 5.7 Clientes con compras superiores al promedio
SELECT c.nombre AS cliente, COUNT(DISTINCT v.id_venta) AS cantidad_ventas, 
       SUM(d.cantidad * d.precio_unitario) AS importe_total_acumulado
FROM Cliente c
INNER JOIN Venta v ON c.id_cliente = v.id_cliente
INNER JOIN DetalleVenta d ON v.id_venta = d.id_venta
GROUP BY c.id_cliente, c.nombre
HAVING SUM(d.cantidad * d.precio_unitario) > (
    SELECT AVG(total_venta) 
    FROM (
        SELECT SUM(cantidad * precio_unitario) AS total_venta 
        FROM DetalleVenta 
        GROUP BY id_venta
    ) AS resumen_ventas
)
ORDER BY importe_total_acumulado DESC;
GO