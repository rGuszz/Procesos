import streamlit as st
import pandas as pd
import yfinance as yf
import procesos as pr
from streamlit_dynamic_filters import DynamicFilters

titulo = st.container()
datos = st.container()
opciones = st.container()

with titulo:
    st.title("Bienvenido a la interfaz para calcular el precio de opciones y ver otros datos")
    df = pd.read_csv(r'nasdaq_screener_1715204451275.csv', usecols=["Symbol", "Name"])
    st.write(df)

    st.sidebar.header("Filtro")
    e = st.sidebar.multiselect("Elije una opción", options=df["Name"], max_selections=1, default="Apple Inc. Common Stock", key="str")
    empresa = str(e)
    st.write(empresa)
    activo = df.loc[empresa,"Symbol"]
    st.write(activo)
    
with datos:
    st.header("Precios del activo y gráfica")
    st.text("Los últimos 182 precios del activo se muestran en la siguiente tabla y se muestra un gráfico")
    df = pr.precio(activo)
    df = pr.precio(activo).iloc[::-1]
    st.write(df)
    st.line_chart(df)

with opciones:
    st.header("Volatilidad")
    st.text("Cálculo de la volatilidad")
    vol = pr.volatilidad(activo)
    st.write(f"La volatilidad del activo {activo} es de {round(vol*100,2)}%")
    
    st.header(f"Precio de la opción europea vainilla tipo put del activo {activo}")
    K = st.slider("Precio Strike", min_value=0.00, max_value=1000.00, step=0.01, value=200.00)
    
    st.subheader("Cálculo con simulación")
    precio_put = pr.opcion_put(activo, K)
    st.write(f"El precio de la opción tipo put al dia de hoy (Simulación) es de ${round(precio_put,2)}")
    
    st.subheader("Cálculo con la fórmula de Black-Scholes")
    precio_put_bs = pr.opcion_put_bs(activo, K)
    st.write(f"El precio de la opción tipo put (Black-Scholes) al dia de hoy es de ${round(precio_put_bs,2)}")    
    
    st.header(f"Simularemos una trayectoria del activo {activo}")
    n = st.slider("Escoje el numero de subintervalos en los que estará divido el tiempo", min_value=2, max_value=1000, value=50)
    sim = pr.trayectoria(activo, n)
    st.line_chart(sim)
    
    st.header(f"Simularemos j trayectorias del activo {activo}")
    j = st.slider("Elije el número de trayectorias a simular", min_value=1, max_value=10000, value=100)
    pr.trayectorias(activo, j, n)
    
    st.header(f"Precio de la opción asiatica europea vainilla tipo put del activo {activo}")
    num = st.slider("Escoje el numero de subintervalos en los que estará divido el tiempo ", min_value=1, max_value=1000, value=50)
    jp = st.slider("Elije el número de trayectorias a simular para hacer el cálculo", min_value=1, max_value=10000, value=100)
    
    st.subheader("Cálculo con el promedio aritmético")
    precio_asiatica_put = pr.precio_asiatica(activo,num,jp)
    st.write(f"\nEl precio de la opción asiática de {activo} calculado con el promedio aritmético al dia de hoy es de ${round(precio_asiatica_put,2)}")
    
    st.subheader("Cálculo con el promedio geométrico")
    K_1 = st.slider("Precio Strike para la opción asiática", min_value=0.00, max_value=10000.00, step=0.01, value=200.00)
    precio_asiatica_put_geo = pr.precio_asiatica_geo(activo,num,jp,K_1)
    st.write(f"\nEL precio de la opción asiática de {activo} calculado con el promedio geometrico al dia de hoy es de ${round(precio_asiatica_put_geo,2)}")
    
