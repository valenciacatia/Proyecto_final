import io
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from PIL import Image


st.set_page_config(
    page_title="EDA Bank Marketing",
    layout="wide"
)

sns.set_theme(style="whitegrid")


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


VARIABLE_OBJETIVO = "y"


DICCIONARIO_VARIABLES = {
    "age": "Edad del cliente",
    "job": "Tipo de trabajo del cliente",
    "marital": "Estado civil",
    "education": "Nivel educativo",
    "default": "Tiene crédito en mora",
    "housing": "Tiene crédito hipotecario",
    "loan": "Tiene crédito personal",
    "contact": "Canal de comunicación usado",
    "month": "Último mes de contacto",
    "day_of_week": "Día del último contacto",
    "duration": "Duración del contacto en segundos",
    "campaign": "Número de contactos en la campaña actual",
    "pdays": "Días desde la última gestión",
    "previous": "Contactos previos antes de la actual campaña",
    "poutcome": "Resultado de la campaña anterior",
    "emp.var.rate": "Tasa de variación del empleo",
    "cons.price.idx": "Índice de precios al consumidor",
    "cons.conf.idx": "Índice de confianza del consumidor",
    "euribor3m": "Euribor a 3 meses",
    "nr.employed": "Número de empleados",
    "y": "Resultado final: yes si aceptó la campaña, no si no la aceptó"
}


TRADUCCION_CATEGORIAS = {
    "yes": "Sí aceptó",
    "no": "No aceptó",
    "success": "Aceptó anteriormente",
    "failure": "No aceptó anteriormente",
    "nonexistent": "Sin campaña previa",
    "cellular": "Celular",
    "telephone": "Teléfono"
}


def footer():
    st.markdown("---")
    st.caption("Elaborado por: Catia Maria Valencia Vilca")


@st.cache_data
def leer_csv(archivo):
    try:
        return pd.read_csv(archivo, sep=";")
    except Exception:
        try:
            return pd.read_csv(archivo, sep=None, engine="python")
        except Exception:
            return None


def traducir_valor(valor):
    return TRADUCCION_CATEGORIAS.get(str(valor), valor)


def porcentaje_yes(serie):
    return (serie.astype(str).str.lower() == "yes").mean()


def formato_pct(valor):
    return f"{valor * 100:.2f}%"


def clasificar_variable(df, columna):
    tipo = df[columna].dtype
    unicos = df[columna].nunique(dropna=True)

    if columna == VARIABLE_OBJETIVO:
        return "Variable objetivo"
    elif pd.api.types.is_numeric_dtype(tipo) and unicos > 15:
        return "Numérica continua"
    elif pd.api.types.is_numeric_dtype(tipo) and unicos <= 15:
        return "Numérica discreta"
    else:
        return "Categórica"


def obtener_variables_por_tipo(df):
    numericas = []
    categoricas = []

    for col in df.columns:
        clasificacion = clasificar_variable(df, col)

        if "Numérica" in clasificacion:
            numericas.append(col)
        elif clasificacion == "Categórica":
            categoricas.append(col)

    return numericas, categoricas


def limpiar_ejes(ax, titulo=None, xlabel=None, ylabel=None, rotacion=0):
    if titulo:
        ax.set_title(titulo, fontsize=12, weight="bold")
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=rotacion)


class DataAnalyzer:

    def __init__(self, df):
        self.df = df.copy()
        self.numericas, self.categoricas = obtener_variables_por_tipo(self.df)

    def resumen_general(self):
        data = []

        for col in self.df.columns:
            data.append({
                "Variable": col,
                "Descripción": DICCIONARIO_VARIABLES.get(col, col),
                "Tipo de dato": str(self.df[col].dtype),
                "Valores nulos": self.df[col].isna().sum(),
                "% nulos": round(self.df[col].isna().mean() * 100, 2),
                "Valores únicos": self.df[col].nunique(dropna=True),
                "Clasificación": clasificar_variable(self.df, col)
            })

        return pd.DataFrame(data)

    def estadisticas_numericas(self):
        if len(self.numericas) == 0:
            return pd.DataFrame()

        tabla = self.df[self.numericas].describe().T.reset_index()
        tabla = tabla.rename(columns={
            "index": "Variable",
            "count": "Cantidad de datos",
            "mean": "Media",
            "std": "Desviación estándar",
            "min": "Mínimo",
            "25%": "Percentil 25",
            "50%": "Mediana",
            "75%": "Percentil 75",
            "max": "Máximo"
        })

        tabla.insert(
            1,
            "Descripción",
            tabla["Variable"].map(lambda x: DICCIONARIO_VARIABLES.get(x, x))
        )

        return tabla

    def estadisticas_categoricas(self):
        resumen = []

        for col in self.categoricas:
            conteo = self.df[col].value_counts(dropna=False)

            categoria_frecuente = conteo.index[0]
            cantidad = conteo.iloc[0]
            participacion = cantidad / len(self.df)

            resumen.append({
                "Variable": col,
                "Descripción": DICCIONARIO_VARIABLES.get(col, col),
                "Categorías": self.df[col].nunique(dropna=True),
                "Categoría más frecuente": traducir_valor(categoria_frecuente),
                "Cantidad": cantidad,
                "Participación": formato_pct(participacion)
            })

        return pd.DataFrame(resumen)

    def tasa_aceptacion(self):
        if VARIABLE_OBJETIVO not in self.df.columns:
            return np.nan
        return porcentaje_yes(self.df[VARIABLE_OBJETIVO])

    def tasa_por_categoria(self, variable):
        tabla = (
            self.df.groupby(variable)[VARIABLE_OBJETIVO]
            .apply(porcentaje_yes)
            .reset_index(name="Tasa de aceptación")
            .sort_values("Tasa de aceptación", ascending=False)
        )

        tabla["Categoría"] = tabla[variable].map(traducir_valor)
        tabla["Tasa de aceptación %"] = tabla["Tasa de aceptación"].map(formato_pct)

        return tabla

    def comparacion_numerica_objetivo(self, variable):
        tabla = (
            self.df.groupby(VARIABLE_OBJETIVO)[variable]
            .agg(
                Cantidad="count",
                Media="mean",
                Mediana="median",
                Desviacion_estandar="std",
                Minimo="min",
                Maximo="max"
            )
            .reset_index()
        )

        tabla = tabla.rename(columns={
            VARIABLE_OBJETIVO: "Resultado de campaña",
            "Desviacion_estandar": "Desviación estándar",
            "Minimo": "Mínimo",
            "Maximo": "Máximo"
        })

        tabla["Resultado de campaña"] = tabla["Resultado de campaña"].map(traducir_valor)

        return tabla



logo_path = Path("DMC.png")

if logo_path.exists():
    logo = Image.open(logo_path)
    st.sidebar.image(logo, use_container_width=True)

st.sidebar.title("Bank Marketing")
st.sidebar.caption("Análisis Exploratorio de Datos")

archivo = st.sidebar.file_uploader(
    "Carga el archivo BankMarketing.csv",
    type=["csv"]
)

menu = st.sidebar.radio(
    "Navegación",
    ["Home", "Carga del Dataset", "EDA", "Conclusiones"]
)


df = None

if archivo is not None:
    df = leer_csv(archivo)


if menu != "Home" and df is None:
    st.warning("No se ha cargado el dataset. Carga el archivo BankMarketing.csv desde el panel lateral para continuar.")
    footer()
    st.stop()



if menu == "Home":

    st.title("Bank Marketing")

    st.markdown("""
    ## Objetivo y resumen

    Se tiene la información de una institución financiera que busca entender los factores que influyen en la aceptación de sus campañas de marketing.
    En los últimos 6 meses, la efectividad disminuyó de 12% a 8%, afectando los bonos de los ejecutivos comerciales.
    El objetivo del análisis es identificar relaciones y comportamientos relevantes que expliquen la aceptación de las campañas.
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Proyecto")
        st.markdown("## EDA")

    with col2:
        st.markdown("### Herramienta")
        st.markdown("## Streamlit")

    with col3:
        st.markdown("### Enfoque")
        st.markdown("## Toma de decisiones")

    st.subheader("Datos del proyecto")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Alumna:** Catia Maria Valencia Vilca")
        st.write("**Curso:** Especialización Python for Analytics")
        st.write("**Año:** 2026")

    with col2:
        st.write("**Tecnologías:** Python, Pandas, NumPy, Matplotlib, Seaborn y Streamlit")
        st.write("**Dataset:** BankMarketing.csv")
        st.write("**Variable objetivo:** Resultado final: `yes` si aceptó la campaña, `no` si no la aceptó.")

    st.subheader("Contexto")
    st.info(
        "La efectividad comercial disminuyó de 12% a 8%. "
        "Por ello, se analiza la última campaña para encontrar relaciones útiles "
        "entre el perfil del cliente, el contacto comercial y la aceptación final."
    )

    footer()



elif menu == "Carga del Dataset":

    st.title("Carga y validación del dataset")

    analyzer = DataAnalyzer(df)

    st.success("Dataset cargado correctamente.")

    col1, col2, col3 = st.columns(3)

    col1.metric("Filas", f"{df.shape[0]:,}")
    col2.metric("Columnas", df.shape[1])
    col3.metric("Tasa de aceptación", formato_pct(analyzer.tasa_aceptacion()))

    st.subheader("Vista previa")
    st.dataframe(df.head(10), use_container_width=True)

    st.subheader("Diccionario de variables")

    diccionario = pd.DataFrame({
        "Variable": list(DICCIONARIO_VARIABLES.keys()),
        "Descripción": list(DICCIONARIO_VARIABLES.values())
    })

    st.dataframe(diccionario, use_container_width=True)

    st.info(
        """
        La variable **Success** significa que el cliente ya aceptó una campaña anterior.

        **Failure** significa que el cliente no aceptó una campaña anterior.

        **Nonexistent** significa que el cliente no tuvo campaña previa.
        """
    )

    footer()


elif menu == "EDA":

    st.title("Análisis Exploratorio de Datos")

    analyzer = DataAnalyzer(df)

    numericas = analyzer.numericas
    categoricas = analyzer.categoricas

    tabs = st.tabs([
        "1. Información general",
        "2. Variables",
        "3. Estadística descriptiva",
        "4. Valores faltantes",
        "5. Numéricas",
        "6. Categóricas",
        "7. Numérico vs objetivo",
        "8. Categórico vs objetivo",
        "9. Análisis dinámico",
        "10. Hallazgos"
    ])

    with tabs[0]:

        st.subheader("Información general del dataset")

        col1, col2, col3 = st.columns(3)

        col1.metric("Filas", f"{df.shape[0]:,}")
        col2.metric("Columnas", df.shape[1])
        col3.metric("Aceptación global", formato_pct(analyzer.tasa_aceptacion()))

        st.dataframe(analyzer.resumen_general(), use_container_width=True)

        st.info(
            "La tabla resume los tipos de datos, valores nulos, valores únicos y clasificación de cada variable."
        )

    with tabs[1]:

        st.subheader("Clasificación de variables")

        tabla_variables = analyzer.resumen_general()[[
            "Variable",
            "Descripción",
            "Tipo de dato",
            "Valores únicos",
            "Clasificación"
        ]]

        st.dataframe(tabla_variables, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Variables numéricas")
            st.write(numericas)
            st.metric("Cantidad", len(numericas))

        with col2:
            st.markdown("### Variables categóricas")
            st.write(categoricas)
            st.metric("Cantidad", len(categoricas))

    with tabs[2]:

        st.subheader("Estadística descriptiva")

        st.markdown("### Variables numéricas")
        st.dataframe(analyzer.estadisticas_numericas(), use_container_width=True)

        st.markdown("### Variables categóricas")
        st.dataframe(analyzer.estadisticas_categoricas(), use_container_width=True)

        st.info(
            "La participación indica qué porcentaje representa la categoría más frecuente de cada variable. "
            "No significa porcentaje de datos disponibles."
        )

    with tabs[3]:

        st.subheader("Análisis de valores faltantes")

        nulls = df.isnull().sum().sort_values(ascending=False)
        nulls_pct = (df.isnull().mean() * 100).sort_values(ascending=False)

        tabla_nulls = pd.DataFrame({
            "Variable": nulls.index,
            "Valores faltantes": nulls.values,
            "% faltantes": nulls_pct.values
        })

        st.dataframe(tabla_nulls, use_container_width=True)

        fig, ax = plt.subplots(figsize=(12, 5))

        sns.barplot(
            data=tabla_nulls,
            x="Variable",
            y="Valores faltantes",
            ax=ax
        )

        limpiar_ejes(
            ax,
            "Valores faltantes por variable",
            "",
            "Cantidad",
            75
        )

        st.pyplot(fig)

        if nulls.sum() == 0:
            st.success("No se identifican valores faltantes explícitos en el dataset.")

    with tabs[4]:

        st.subheader("Distribución de variables numéricas")

        for i in range(0, len(numericas), 2):

            col1, col2 = st.columns(2)
            fila = numericas[i:i+2]

            for col_streamlit, variable in zip([col1, col2], fila):

                with col_streamlit:

                    descripcion = DICCIONARIO_VARIABLES.get(variable, variable)

                    fig, ax = plt.subplots(figsize=(6, 4))

                    sns.histplot(
                        df[variable],
                        kde=True,
                        ax=ax
                    )

                    limpiar_ejes(
                        ax,
                        f"Distribución de {descripcion}",
                        descripcion,
                        "Frecuencia"
                    )

                    st.pyplot(fig)

        st.info(
            "Los histogramas permiten revisar la forma de distribución de las variables numéricas, "
            "identificando concentración, dispersión y posibles valores extremos."
        )

    with tabs[5]:

        st.subheader("Análisis de variables categóricas")

        categorias_analisis = [
            col for col in categoricas if col != VARIABLE_OBJETIVO
        ]

        for variable in categorias_analisis:

            descripcion = DICCIONARIO_VARIABLES.get(variable, variable)

            st.markdown(f"### {descripcion}")

            conteo = (
                df[variable]
                .value_counts(dropna=False)
                .reset_index()
            )

            conteo.columns = [descripcion, "Cantidad"]
            conteo["Participación"] = conteo["Cantidad"] / conteo["Cantidad"].sum()
            conteo["Participación"] = conteo["Participación"].map(formato_pct)
            conteo[descripcion] = conteo[descripcion].map(traducir_valor)

            col1, col2 = st.columns([1, 2])

            with col1:
                st.dataframe(conteo, use_container_width=True)

            with col2:
                fig, ax = plt.subplots(figsize=(8, 4))

                orden = df[variable].value_counts().index

                sns.countplot(
                    data=df,
                    y=variable,
                    order=orden,
                    ax=ax
                )

                labels = [traducir_valor(t.get_text()) for t in ax.get_yticklabels()]
                ax.set_yticklabels(labels)

                limpiar_ejes(
                    ax,
                    f"Frecuencia de {descripcion}",
                    "Cantidad",
                    ""
                )

                st.pyplot(fig)

    with tabs[6]:

        st.subheader("Análisis bivariado: variables numéricas vs aceptación")

        variables_clave = [
            col for col in ["age", "duration", "campaign", "previous", "euribor3m"]
            if col in numericas
        ]

        if len(variables_clave) == 0:
            variables_clave = numericas[:5]

        for variable in variables_clave:

            descripcion = DICCIONARIO_VARIABLES.get(variable, variable)

            st.markdown(f"### {descripcion}")

            tabla = analyzer.comparacion_numerica_objetivo(variable)

            col1, col2 = st.columns([1, 2])

            with col1:
                st.dataframe(tabla, use_container_width=True)

            with col2:
                fig, ax = plt.subplots(figsize=(7, 4))

                sns.boxplot(
                    data=df,
                    x=VARIABLE_OBJETIVO,
                    y=variable,
                    ax=ax
                )

                ax.set_xticklabels([
                    traducir_valor(t.get_text()) for t in ax.get_xticklabels()
                ])

                limpiar_ejes(
                    ax,
                    f"{descripcion} según aceptación",
                    "Aceptación de la campaña",
                    descripcion
                )

                st.pyplot(fig)

            tabla_mediana = (
                df.groupby(VARIABLE_OBJETIVO)[variable]
                .median()
                .reset_index()
            )

            tabla_mediana[VARIABLE_OBJETIVO] = tabla_mediana[VARIABLE_OBJETIVO].map(traducir_valor)

            mejor_fila = tabla_mediana.sort_values(variable, ascending=False).iloc[0]

            st.caption(
                f"La mayor mediana de {descripcion.lower()} se observa en el grupo "
                f"'{mejor_fila[VARIABLE_OBJETIVO]}', con un valor de {mejor_fila[variable]:,.2f}."
            )

    with tabs[7]:

        st.subheader("Análisis bivariado: variables categóricas vs aceptación")

        variables_clave_cat = [
            col for col in ["job", "education", "contact", "month", "poutcome"]
            if col in categoricas
        ]

        if len(variables_clave_cat) == 0:
            variables_clave_cat = categoricas[:5]

        for variable in variables_clave_cat:

            descripcion = DICCIONARIO_VARIABLES.get(variable, variable)

            st.markdown(f"### {descripcion}")

            tabla = analyzer.tasa_por_categoria(variable)

            tabla_mostrar = tabla[["Categoría", "Tasa de aceptación %"]].copy()
            tabla_mostrar.columns = [descripcion, "Tasa de aceptación"]

            col1, col2 = st.columns([1, 2])

            with col1:
                st.dataframe(tabla_mostrar, use_container_width=True)

            with col2:
                fig, ax = plt.subplots(figsize=(8, 4))

                sns.barplot(
                    data=tabla,
                    y="Categoría",
                    x="Tasa de aceptación",
                    ax=ax
                )

                ax.set_xlim(
                    0,
                    max(tabla["Tasa de aceptación"].max() * 1.15, 0.10)
                )

                limpiar_ejes(
                    ax,
                    f"Tasa de aceptación por {descripcion}",
                    "Tasa de aceptación",
                    ""
                )

                st.pyplot(fig)

            mejor = tabla.iloc[0]

            categoria = mejor["Categoría"]
            tasa = formato_pct(mejor["Tasa de aceptación"])

            st.caption( 
            f"La categoría con mayor tasa de aceptación en {descripcion.lower()} "
            f"es '{categoria}', con una tasa de {tasa}."
            )
            
            st.markdown("""
                **Interpretación de `poutcome`:**

                - **Success**: el cliente aceptó una campaña anterior.
                - **Failure**: el cliente no aceptó una campaña anterior.
                - **Nonexistent**: el cliente no tuvo campaña previa.
                    """)

    with tabs[8]:

        st.subheader("Análisis dinámico complementario")

        variables_para_agrupar = [
            col for col in ["job", "education", "contact", "month", "poutcome"]
            if col in categoricas
        ]

        col1, col2 = st.columns(2)

        with col1:

            variable_grupo = st.selectbox(
                "Variable para agrupar",
                variables_para_agrupar
            )

            categorias = st.multiselect(
                "Filtrar categorías",
                sorted(df[variable_grupo].dropna().unique().tolist()),
                default=sorted(df[variable_grupo].dropna().unique().tolist())[:5]
            )

        with col2:

            if "age" in df.columns:
                edad_min = int(df["age"].min())
                edad_max = int(df["age"].max())

                rango_edad = st.slider(
                    "Rango de edad",
                    edad_min,
                    edad_max,
                    (edad_min, edad_max)
                )
            else:
                rango_edad = None

            ver_base = st.checkbox("Mostrar base filtrada")

        df_filtrado = df.copy()

        if rango_edad is not None:
            df_filtrado = df_filtrado[
                df_filtrado["age"].between(rango_edad[0], rango_edad[1])
            ]

        df_filtrado = df_filtrado[
            df_filtrado[variable_grupo].isin(categorias)
        ]

        st.metric("Registros filtrados", f"{len(df_filtrado):,}")

        if len(df_filtrado) > 0:

            tabla = (
                df_filtrado.groupby(variable_grupo)[VARIABLE_OBJETIVO]
                .apply(porcentaje_yes)
                .reset_index(name="Tasa de aceptación")
                .sort_values("Tasa de aceptación", ascending=False)
            )

            tabla["Categoría"] = tabla[variable_grupo].map(traducir_valor)
            tabla["Tasa de aceptación %"] = tabla["Tasa de aceptación"].map(formato_pct)

            st.dataframe(
                tabla[["Categoría", "Tasa de aceptación %"]],
                use_container_width=True
            )

            fig, ax = plt.subplots(figsize=(8, 4))

            sns.barplot(
                data=tabla,
                y="Categoría",
                x="Tasa de aceptación",
                ax=ax
            )

            limpiar_ejes(
                ax,
                "Tasa de aceptación filtrada",
                "Tasa de aceptación",
                ""
            )

            st.pyplot(fig)

            if ver_base:
                st.dataframe(df_filtrado.head(100), use_container_width=True)

        else:
            st.warning("No hay registros con los filtros seleccionados.")

    with tabs[9]:

        st.subheader("Hallazgos clave del EDA")

        tasa = analyzer.tasa_aceptacion()

        mediana_duracion = df.groupby(VARIABLE_OBJETIVO)["duration"].median()

        tasa_contacto = analyzer.tasa_por_categoria("contact") if "contact" in df.columns else None
        tasa_poutcome = analyzer.tasa_por_categoria("poutcome") if "poutcome" in df.columns else None
        tasa_job = analyzer.tasa_por_categoria("job") if "job" in df.columns else None

        col1, col2, col3 = st.columns(3)

        col1.metric("Aceptación global", formato_pct(tasa))
        col2.metric("Mediana duración - No aceptó", f"{mediana_duracion.get('no', np.nan):.0f} seg.")
        col3.metric("Mediana duración - Sí aceptó", f"{mediana_duracion.get('yes', np.nan):.0f} seg.")

        st.markdown("### Interpretación del dataset")

        st.markdown(f"""
        1. La tasa global de aceptación de la campaña es de **{formato_pct(tasa)}**,
        lo que evidencia que aun la campaña de marketing no se ve reflejada por parte de los clientes.

        2. Los clientes que aceptaron la campaña presentan una mayor duración mediana
        de contacto frente a quienes no aceptaron. Esto sugiere que las interacciones con mas duración 
         podrían estar asociadas a una mayor probabilidad de aceptación.

        3. El canal de contacto con mejor desempeño fue
        **{tasa_contacto.iloc[0]['Categoría']}**,
        alcanzando una tasa de aceptación de
        **{formato_pct(tasa_contacto.iloc[0]['Tasa de aceptación'])}**.

        4. Los clientes con antecedentes positivos en campañas anteriores presentan
        una mayor probabilidad de aceptación en la campaña actual.
        En este dataset, la categoría **success** significa que el cliente aceptó
        una campaña previa.

        5. El grupo ocupacional con mayor tasa de aceptación corresponde a
        **{tasa_job.iloc[0]['Categoría']}**, con una tasa de aceptación de
        **{formato_pct(tasa_job.iloc[0]['Tasa de aceptación'])}**.
        """)

    footer()


elif menu == "Conclusiones":

    st.title("Conclusiones finales")

    analyzer = DataAnalyzer(df)

    tasa = formato_pct(analyzer.tasa_aceptacion())

    mediana_duracion = df.groupby(VARIABLE_OBJETIVO)["duration"].median()

    tasa_contacto = analyzer.tasa_por_categoria("contact")
    tasa_poutcome = analyzer.tasa_por_categoria("poutcome")
    tasa_job = analyzer.tasa_por_categoria("job")

    st.markdown(f"""
    1. La campaña presenta una tasa de aceptación de **{tasa}**, por lo que existe oportunidades para mejorar la segmentación comercial.

    2. La duración del contacto diferencia claramente a los clientes que aceptan de los que no aceptan.
    La mediana de duración en clientes que aceptaron es **{mediana_duracion.get('yes', np.nan):.0f} segundos**,
    frente a **{mediana_duracion.get('no', np.nan):.0f} segundos** en clientes que no aceptaron.

    3. El canal con mejor desempeño relativo es **{tasa_contacto.iloc[0]['Categoría']}**, por lo que podría priorizarse en campañas similares.

    4. El antecedente de campañas anteriores es relevante. Cuando el resultado previo fue **{tasa_poutcome.iloc[0]['Categoría']}**,
    la tasa de aceptación fue mayor. En este dataset, `success` significa que el cliente aceptó una campaña anterior.

    5. El grupo laboral con mayor tasa de aceptación es **{tasa_job.iloc[0]['Categoría']}**, lo que permite orientar mejor la segmentación comercial.
    """)

    st.info(
        "Recomendación: usar estos hallazgos para mejorar la selección de clientes, "
        "priorizar canales efectivos y reducir contactos de baja probabilidad de conversión."
    )

    footer()