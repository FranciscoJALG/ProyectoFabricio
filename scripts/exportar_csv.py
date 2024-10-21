# exportar_csv.py meramente para historicos
import pandas as pd
import os
from conexion_sql import obtener_conexion

def exportar_datos_ventas_a_csv(sucursal_id):
    conexion = obtener_conexion()
    query = """
    WITH DetallesAgrupados AS (
        SELECT
            dt.FolDoc_Codigo,
            dt.FolTda_Codigo,
            dt.FolEst_Codigo,
            dt.FolConsecutivo,
            dt.Art_Codigo,
            SUM(dt.DT_Cantidad) AS CantidadVendida,
            CONVERT(DATE, t.T_Fecha) AS FechaVenta
        FROM DetallesTicket dt
        LEFT JOIN VentasNegadas vn ON dt.Art_Codigo = vn.Art_Codigo
            AND dt.FolTda_Codigo = vn.Tda_Codigo
            AND dt.FolEst_Codigo = vn.Est_Codigo
        JOIN Tickets t ON dt.FolDoc_Codigo = t.FolDoc_Codigo
            AND dt.FolTda_Codigo = t.FolTda_Codigo
            AND dt.FolEst_Codigo = t.FolEst_Codigo
            AND dt.FolConsecutivo = t.FolConsecutivo
        LEFT JOIN Compueje ce ON dt.Art_Codigo = ce.Art_Codigo
            AND dt.FolTda_Codigo = ce.FolTda_Codigo
            AND dt.FolEst_Codigo = ce.FolEst_Codigo
            AND dt.FolConsecutivo = ce.FolConsecutivo
        WHERE vn.Art_Codigo IS NULL  -- Excluir ventas negadas
        AND t.FolTda_Codigo = ?  -- Nodo 22 (Sucursal)
        AND TRY_CONVERT(DATE, t.T_Fecha) BETWEEN '2022-01-01' AND '2023-12-31'  -- Filtrar por años 2022 y 2023
        AND ce.TMA_Codigo IS NOT NULL  -- Asegurarse que hay movimientos
        GROUP BY dt.FolDoc_Codigo, dt.FolTda_Codigo, dt.FolEst_Codigo, dt.FolConsecutivo, dt.Art_Codigo, t.T_Fecha
    )
    SELECT  
        da.Art_Codigo AS CodigoArticulo,
        a.Art_Descripcion AS DescripcionArticulo,
        SUM(da.CantidadVendida) AS TotalVendido,
        da.FechaVenta,
        t.FolTda_Codigo AS Sucursal,
        SUM(ce.CE_Cantidad) AS InventarioMovimiento  -- Movimientos desde Compueje
    FROM DetallesAgrupados da
    JOIN Articulos a ON da.Art_Codigo = a.Art_Codigo
    JOIN Tickets t ON da.FolDoc_Codigo = t.FolDoc_Codigo
        AND da.FolTda_Codigo = t.FolTda_Codigo
        AND da.FolEst_Codigo = t.FolEst_Codigo
        AND da.FolConsecutivo = t.FolConsecutivo
    LEFT JOIN Compueje ce ON da.Art_Codigo = ce.Art_Codigo
        AND da.FolTda_Codigo = ce.FolTda_Codigo
        AND da.FolEst_Codigo = ce.FolEst_Codigo
        AND da.FolConsecutivo = ce.FolConsecutivo
        AND ce.TMA_Codigo IS NOT NULL  -- Incluir solo movimientos con TMA_Codigo válido
    GROUP BY da.Art_Codigo, a.Art_Descripcion, da.FechaVenta, t.FolTda_Codigo
    ORDER BY da.FechaVenta;
    """
    
    # Ejecutar la consulta y exportar los datos a un DataFrame
    datos = pd.read_sql(query, conexion, params=[sucursal_id])
    conexion.close()

    # Verificar si el folder existe, si no, crearlo
    folder = './csv_sucursales'
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Crear el nombre del archivo CSV y guardar los datos
    nombre_archivo = f'{folder}/sucursal_{sucursal_id}.csv'
    datos.to_csv(nombre_archivo, index=False)
    print(f'Datos de la sucursal {sucursal_id} exportados a {nombre_archivo}')

if __name__ == "__main__":
    for sucursal_id in range(1, 40):  # Rango de sucursales
        exportar_datos_ventas_a_csv(sucursal_id)
