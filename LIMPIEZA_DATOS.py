# PREPARACIÓN DE DATOS EN PYTHON:
# Importar librerías para el proyecto:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# PROCESO DE CARGA DEL DATASET AL PROGRAMA:
# Inicializo variable 'df'(DataFrame) que abrirá y leerá archivos .CSV de la ruta definida por medio de 'pd.read_csv'.
# Coloco 'r' para no interpretar '\' como comandos especiales.
# encoding="latin-1" para leer la codificación en la que el archivo está. Python los lee correctamente en vez de fallar.
df = pd.read_csv(r"Global_Superstore2.csv", encoding="latin-1")

"""
# Visualizo las primeras filas del dataset.
print(df.head())

# Información general.
print(df.info())

# Visualizo el total de registros en el dataset SIN los datos preparados.
print(f"El dataset completo tiene un total de {len(df)} registros.")
"""

# PROCESO DE DETECCIÓN DE VALORES NULOS:
# Valido si existen registros con valores nulos.
print("COLUMNAS CON VALORES NULOS:")
print(df.isnull().sum())

# Existen valores nulos en "Código Postal". 
# Rellenaré los nulos con "Desconocido" y transformaré dicha columna a string, pues no se trabajará cálculos matemáticos con ella.
df['Postal Code'] = df['Postal Code'].fillna('Desconocido')
df['Postal Code'] = df['Postal Code'].astype(str)

print()

# PROCESO DE DETECCIÓN DE DUPLICADOS:
# Valido si existen registros duplicados.
print("VALORES DUPLICADOS:", df.duplicated().sum())

print()

# Guardo los datos duplicados en la variable.
# Muestro las filas y algunas columnas.
filas_duplicadas = df[df.duplicated()]
print("VERIFICACIÓN DUPLICADOS:")
print(filas_duplicadas[['Row ID', 'Sales', 'Postal Code']].head(10))

# No existen duplicados. No se realiza más.

print()

# TRANSFORMACIÓN DE VARIABLES
# Conversión de fechas. Especifico que el día va primero tal y como en el .CSV.
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)

# CREACIÓN DE VARIABLES TEMPORALES
# De gran utilidad para realizar el análisis de ventas que realizaremos.
# Extraigo partes de la fecha: año y mes. Adicional, a partir del número del mes extraigo el nombre del mes.
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month
df['Month_Name'] = df['Order Date'].dt.month_name()

# Con los datos ya limpios procedo a guardarlos en un fichero nuevo.
df.to_csv("dataset_limpio.csv",index=False)

print("DATASET LIMPIO GUARDADO")
