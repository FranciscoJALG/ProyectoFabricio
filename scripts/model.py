import numpy as np
import pandas as pd
from pmdarima import auto_arima  # ARIMA
import os
import pickle

# Función para preparar y entrenar modelos con ARIMA
def entrenar_modelo_arima(datos_csv, sucursal_id):
    # Leer los datos del CSV
    datos = pd.read_csv(datos_csv)

    # Filtrar productos con ventas nulas y fechas vacías
    datos = datos[(datos['TotalVendido'] > 0) & (pd.notnull(datos['FechaVenta']))]
    
    # Ordenar por fecha
    datos = datos.sort_values('FechaVenta')

    # Obtener los productos únicos dentro de la sucursal
    productos_unicos = datos['CodigoArticulo'].unique()

    # Entrenar un modelo por cada producto en la sucursal
    for producto_codigo in productos_unicos:
        # Filtrar las ventas para este producto
        datos_producto = datos[datos['CodigoArticulo'] == producto_codigo]

        print(f"Producto {producto_codigo} tiene {len(datos_producto)} datos.")

        if len(datos_producto) < 2:
            print(f"No hay suficientes datos para entrenar el modelo para el producto {producto_codigo} en la sucursal {sucursal_id}")
            continue

        # Preparar los datos de ventas
        ventas = datos_producto['TotalVendido'].values

        # Entrenar el modelo ARIMA automáticamente
        try:
            print(f"Entrenando ARIMA para el producto {producto_codigo}")
            modelo_arima = auto_arima(ventas, seasonal=False, stepwise=True)
        except Exception as e:
            print(f"Error al entrenar ARIMA para el producto {producto_codigo}: {e}")
            continue  # Saltar este producto si hay un error

        # Guardar el modelo entrenado para este producto en esta sucursal
        model_folder = os.path.join('./models', f'sucursal_{sucursal_id}')
        if not os.path.exists(model_folder):
            os.makedirs(model_folder)
        
        model_path = os.path.join(model_folder, f'producto_{producto_codigo}_arima_model.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(modelo_arima, f)

        print(f"Modelo ARIMA guardado para el producto {producto_codigo} en la sucursal {sucursal_id}, archivo: {model_path}")

# Ejecución del entrenamiento para una sucursal específica
if __name__ == "__main__":

    # Archivo CSV de la sucursal y su ID
    csv_path = './csv_sucursales/sucursal_22.csv'  # Ruta al CSV de la sucursal
    sucursal_id = '22'  # ID de la sucursal

    # Entrenar los modelos para la sucursal 22
    entrenar_modelo_arima(csv_path, sucursal_id)
