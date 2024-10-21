import pyodbc
import pandas as pd

# Función para obtener la conexión a SQL Server
def obtener_conexion():
    conexion = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'  # Servidor
        'DATABASE=NOVACAJA5;'  # Nombre BD
        'Trusted_Connection=yes;'  # Autenticación de Windows
    )
    return conexion

# Función para generar el CSV con los datos de enero 2024
def generar_csv_ventas_enero():
    # Establecer la conexión
    conn = obtener_conexion()

    # Define el query para obtener los datos de enero 2024
    query = '''
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
        AND t.FolTda_Codigo = 22  -- Nodo 22 (Sucursal)
        AND TRY_CONVERT(DATE, t.T_Fecha) BETWEEN '2024-01-01' AND '2024-01-31'  -- Filtrar por enero de 2024
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
    '''

    # Ejecutar el query y cargar los resultados en un DataFrame de pandas
    df = pd.read_sql(query, conn)

    # Cerrar la conexión
    conn.close()

    # Guardar el DataFrame en un archivo CSV
    csv_file_path = './ventas_enero_2024.csv'  # ruta
    df.to_csv(csv_file_path, index=False)

    print(f'Datos exportados a {csv_file_path}')

# Ejecutar la función para generar el CSV
if __name__ == '__main__':
    generar_csv_ventas_enero()
