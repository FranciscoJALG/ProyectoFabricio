# inventario.py
from conexion_sql import obtener_conexion

# Función para obtener el inventario actual de un producto en la sucursal 8
def obtener_inventario_actual(producto_codigo):
    conexion = obtener_conexion()

    query = """
    SELECT 
        d.AA_ExistenciaActualU AS InventarioActual
    FROM 
        ArticulosAlmacen d
    WHERE 
        d.Tda_Codigo = 22  -- Solo para la sucursal 8
    AND 
        d.Art_Codigo = ?;
    """

    
    cursor = conexion.cursor()
    cursor.execute(query, producto_codigo)
    
    resultado = cursor.fetchone()
    conexion.close()

    if resultado:
        return resultado[0]  # Retornar el inventario actual
    else:
        return 0  # Si no se encuentra el producto, retornar 0
