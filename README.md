# Proyecto Final - Bank Marketing

## Objetivo

El objetivo del proyecto es realizar un Análisis Exploratorio de Datos (EDA) del caso BankMarketing, que evalúa la aceptación de campañas de marketing.  
El análisis busca identificar los principales factores relacionados con la aceptación de dichas campañas por parte de los clientes.

## Tecnologías utilizadas

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Streamlit

## Dataset

El proyecto utiliza el archivo:

- `BankMarketing.csv`

## Funcionalidades

La aplicación permite:

- Cargar dinámicamente el dataset.
- Clasificar automáticamente las variables.
- Revisar estadísticas descriptivas.
- Analizar valores faltantes.
- Evaluar variables numéricas y categóricas.
- Realizar análisis bivariado frente a la variable objetivo.
- Visualizar resultados mediante gráficos.
- Revisar hallazgos e interpretación del dataset.
- Presentar conclusiones finales.

## Instrucciones de ejecución

Para ejecutar el proyecto, primero se deben instalar las librerías necesarias desde el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

Luego, desde la carpeta del proyecto, ejecutar:

```bash
streamlit run app_campañas.py
```
## Link para ingresar a la aplicación

[Aplicación Bank-Marketing](https://proyecto-final-bank-marketing.streamlit.app/)


## Visualización de la aplicación

### Home

La sección Home presenta el contexto del problema, el objetivo del proyecto y la información general del estudiante.


![Home](Home.jpg)

### Carga del Dataset

La sección Carga del Dataset permite cargar el archivo `BankMarketing.csv`, validar la estructura de la base y revisar el diccionario de variables.


![Carga Dataset](Carga%20Dataset.jpg)

### Análisis Exploratorio de Datos

La sección EDA permite identificar las principales características de los clientes que aceptan o no aceptan la campaña.  
Incluye análisis general, clasificación de variables, estadística descriptiva, valores faltantes, análisis numérico, análisis categórico y análisis bivariado.


![EDA 1](EDA1.jpg)

![EDA 2](EDA2.jpg)

![EDA 3](EDA3.jpg)

### Conclusiones

La sección Conclusiones resume los principales hallazgos encontrados en el análisis y plantea recomendaciones generales para mejorar la segmentación de campañas.

![Conclusiones](Conclusiones.jpg)

## Conclusión general

El análisis permite identificar las principales caracteristicas asociadas a la aceptación de campañas de marketing, como el canal de contacto, la duración de la interacción, el historial de campañas anteriores y ciertas características del perfil del cliente.  
Estos resultados pueden servir como base para mejorar la segmentación comercial y orientar mejor futuras campañas.
