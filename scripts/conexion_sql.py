# conexion_sql.py
import pyodbc

def obtener_conexion():
    conexion = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'  # Servidor
        'DATABASE=NOVACAJA5;'  # Nombre BD
        'Trusted_Connection=yes;'  # Autenticación de Windows
    )
    return conexion

# Probar la conexión
if __name__ == "__main__":
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT 1")
        print("Conexión exitosa")
        conexion.close()
    except Exception as e:
        print(f"Error en la conexión: {e}")
