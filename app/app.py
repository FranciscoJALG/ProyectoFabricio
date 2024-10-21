import sys
import os
import pandas as pd
import pickle
import numpy as np
from flask import Flask, request, render_template, redirect, url_for
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta

# Añadimos la ruta del directorio scripts para las importaciones
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))
from inventario import obtener_inventario_actual  # Importamos la función desde inventario.py

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MODEL_FOLDER'] = 'models'

# Función para calcular MAPE (función de utilidad)
def calcular_mape(y_real, y_pred):
    y_real, y_pred = np.array(y_real), np.array(y_pred)
    # Asegurarnos de que las longitudes coincidan y de que no haya valores nulos
    if len(y_real) == 0 or len(y_real) != len(y_pred):
        return None  # No calcular si no hay suficientes datos comparables
    return np.mean(np.abs((y_real - y_pred) / y_real)) * 100

# Función para predecir con ARIMA si hay suficientes datos
def predecir_ventas_arima(producto_codigo, ventas_recientes):
    try:
        model_path = f'./models/sucursal_22/producto_{producto_codigo}_arima_model.pkl'
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                modelo_arima = pickle.load(f)
            print(f"Modelo ARIMA cargado para el producto {producto_codigo}")

            # Predicción a 45 días
            predicciones_futuras = modelo_arima.predict(n_periods=45)
            return predicciones_futuras
        else:
            print(f"Modelo no encontrado para el producto {producto_codigo}")
            return None
    except Exception as e:
        print(f"Error al aplicar ARIMA: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predecir', methods=['POST'])
def predecir():
    # Recibir la sucursal desde el formulario
    sucursal_id = request.form['sucursal_id']
    
    # Leer el archivo CSV subido por el usuario
    archivo_csv = request.files['archivo_csv']
    datos = pd.read_csv(archivo_csv)

    # Procesar la fecha seleccionada por el usuario
    fecha_prediccion = request.form.get('fecha_prediccion')
    if fecha_prediccion:
        fecha_prediccion = datetime.strptime(fecha_prediccion, '%Y-%m-%d')
    else:
        fecha_prediccion = datetime.now()

    fecha_final = fecha_prediccion + timedelta(days=45)

    resultados = []

    # Obtener los productos únicos dentro del archivo
    productos_unicos = datos['CodigoArticulo'].unique()

    # Realizar predicciones para cada producto
    for producto_codigo in productos_unicos:
        datos_producto = datos[datos['CodigoArticulo'] == producto_codigo]
        ventas_recientes = datos_producto['TotalVendido'].values[-24:]  # Últimos 24 días de ventas (2 ciclos de 12 meses)

        if len(ventas_recientes) < 2:  # Si no hay suficientes datos para hacer una predicción significativa
            print(f"No hay suficientes datos para el producto {producto_codigo}")
            continue  # Saltar este producto si no hay datos suficientes

        # Nombre del producto
        nombre_producto = datos_producto['DescripcionArticulo'].iloc[0]  # Nombre del producto

        # Obtener el inventario actual desde la base de datos para la sucursal
        inventario_actual = obtener_inventario_actual(producto_codigo)

        # Predecir las ventas para los próximos 45 días
        predicciones_futuras = predecir_ventas_arima(producto_codigo, ventas_recientes)

        if predicciones_futuras is None:
            continue

        # Obtener las ventas reales de los últimos 24 días (si hay suficientes datos)
        ventas_reales = datos_producto['TotalVendido'].values[-24:]

        # Calcular el MAPE si hay suficientes datos
        if len(ventas_reales) == len(predicciones_futuras):
            try:
                mape = calcular_mape(ventas_reales, predicciones_futuras[:len(ventas_reales)])
            except Exception as e:
                print(f"Error al calcular el MAPE para el producto {producto_codigo}: {e}")
                mape = None
        else:
            mape = None

        # Calcular la cantidad a reabastecer (predicción - inventario actual)
        cantidad_reabastecer = max(0, np.sum(predicciones_futuras) - float(inventario_actual))

        # Agregar los resultados a la lista
        resultados.append({
            'producto_codigo': producto_codigo,
            'nombre_producto': nombre_producto,
            'inventario_actual': inventario_actual,  # Inventario actual desde la base de datos
            'total_prediccion': np.sum(predicciones_futuras),  # Total de las predicciones
            'cantidad_reabastecer': cantidad_reabastecer,  # Cantidad a reabastecer
            'mape': mape,
            'modelo_utilizado': 'ARIMA',
            'fecha_inicio': fecha_prediccion.strftime('%Y-%m-%d'),
            'fecha_fin': fecha_final.strftime('%Y-%m-%d'),
        })

    # Renderizar la plantilla de resultados
    return render_template('resultado.html', resultados=resultados, sucursal_id=sucursal_id)

if __name__ == '__main__':
    app.run(debug=True)
