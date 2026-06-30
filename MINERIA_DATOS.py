# Importar librerías.
import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


# Configuración global de visualización de Pandas.
# Fuerza a que todos los tipos 'float' muestren el formato de moneda sin alterar el tipo de dato numérico.
pd.set_option('display.float_format', lambda x: f"${x:,.2f}")

# Carga del conjunto de datos usando rutas relativas.
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_completa = os.path.join(directorio_actual, "dataset_limpio.csv")
df = pd.read_csv(ruta_completa)

# Conviertimos las columnas que tienen fechas a tipo DATETIME.
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Ship Date'] = pd.to_datetime(df['Ship Date'])

# --------------------------------------------------
# [ OPCIÓN A: Análisis Descriptivo ]
# --------------------------------------------------

print("\n" + "~" * 75)
print(" >>> TECNICA - ANÁLISIS DESCRIPTIVO")
print("~" * 75)

# PRODUCTOS MÁS VENDIDOS
top_productos = (
    df.groupby('Product Name')['Sales']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\nTOP 10 PRODUCTOS MÁS VENDIDOS:\n")
# Limpieza estética: se remueve el nombre del índice para evitar duplicidad de etiquetas al imprimir.
top_productos.index.name = None 

# Muestra el encabezado alineado manualmente junto con los datos de la Serie en texto limpio.
print(f"{'Product Name':<20} {'Sales':>48}") 
print(top_productos.to_string(header=False))
print("\n" + "█" * 75)

# VENTAS POR REGIÓN
ventas_region = (
    df.groupby('Region')['Sales']
    .sum()
    .sort_values(ascending=False)
)

print("\nVENTAS POR REGIÓN:\n")
# Limpieza de etiqueta de índice.
ventas_region.index.name = None 

# Encabezado manual alineado para la distribución geográfica de ventas.
print(f"{'Región':<20} {'Sales':>9}") 
print(ventas_region.to_string(header=False))
print("\n" + "█" * 75)

# EVOLUCIÓN TEMPORAL
evolucion_temporal = (
    df.groupby(['Year', 'Month'])['Sales']
    .sum()
    .reset_index()
)

print("\nEVOLUCIÓN TEMPORAL DE VENTAS - ÚLTIMOS 12 PERIODOS:\n")
# El truncamiento con .tail(12) extrae el último año del histórico para el reporte dinámico.
print(
    evolucion_temporal
    .tail(12)
    .to_string(index=False)
)
print("\n" + "█" * 75)

# --------------------------------------------------
# [ OPCIÓN B: Segmentación con K-Means ]
# --------------------------------------------------

print("\n" + "~" * 75)
print(" >>> TECNICA - SEGMENTACIÓN CON K-MEANS")
print("~" * 75)

# Agrupación a nivel de cliente para resumir el comportamiento de compra.
clientes = (
    df.groupby('Customer ID')
    .agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Quantity': 'sum'
    })
    .reset_index()
)

# Escalado de características (StandardScaler).
# Es indispensable centrar y normalizar las variables para evitar que las unidades de 'Sales' dominen sobre 'Quantity'.
scaler = StandardScaler()
X_clientes = scaler.fit_transform(clientes[['Sales', 'Profit', 'Quantity']])

# Inicialización del algoritmo de agrupamiento K-Means con un modelo de 3 clústeres.
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
clientes['Cluster'] = kmeans.fit_predict(X_clientes)

print("\nSEGMENTACIÓN DE CLIENTES:\n")

# Construcción de la tabla de perfiles de los segmentos creados.
resumen_clientes = (
    clientes.groupby('Cluster')
    .agg({
        'Sales': ['count', 'mean', 'sum'],
        'Profit': 'mean',
        'Quantity': 'mean'
    })
)

# ─── CONFIGURACIÓN ESTÉTICA DE LA TABLA ───
resumen_print = resumen_clientes.copy()
# Se aplana el índice multinivel generado por la agregación (ej. ('Sales', 'mean') pasa a 'Sales_mean').
resumen_print.columns = [f"{col[0]}_{col[1]}" for col in resumen_print.columns]
resumen_print = resumen_print.reset_index()

# Impresión con formateador selectivo.
# Se inyecta una función lambda local en 'Quantity_mean' para sobrescribir la regla monetaria global,
# ya que el conteo físico de productos vendidos no lleva signo de dólar.
print(
    resumen_print.to_string(
        index=False, 
        col_space=5, 
        justify='right',
        formatters={'Quantity_mean': lambda x: f"{x:.1f}"} 
    )
)
print("\n" + "█" * 75)

# --------------------------------------------------
# [ OPCIÓN D: Predicción ]
# --------------------------------------------------

print("~" * 75)
print(" >>> TECNICA - PREDICCIÓN CON REGRESIÓN LINEAL")
print("~" * 75)

# Segmentación de variables del conjunto de datos.
X = df[['Quantity', 'Discount']] # Atributos predictores independientes.
y = df['Sales']                  # Variable continua dependiente (objetivo).

# División de datos para la evaluación del modelo.
# Se destina un 20% reservado para pruebas ciegas del rendimiento de la regresión.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

# Ajuste y entrenamiento del modelo con los datos del subconjunto de entrenamiento.
modelo = LinearRegression()
modelo.fit(X_train, y_train)

# Generación de proyecciones basadas en los datos de testeo.
predicciones = modelo.predict(X_test)

# Cálculo de la métrica R² para conocer el porcentaje de la variabilidad explicado por el modelo.
r2 = r2_score(y_test, predicciones)
print(f"\nCoeficiente de Determinación (R²): {r2:.4f}")

# Creación de DataFrame comparativo para auditar la desviación de las predicciones del modelo.
comparacion = pd.DataFrame({
    'Ventas Reales': y_test.values[:10],
    'Ventas Predichas': predicciones[:10]
})

print("\nPRIMERAS 10 PREDICCIONES:\n")
print(comparacion.to_string(index=False))

print("\n" + "═" * 74)
print(" --FIN DE LA MINERÍA DE DATOS--")
print("═" * 74)
