import yfinance as yf
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import streamlit as st
import plotly.graph_objs as go

T = 182/360

def precio(a):
    df = yf.download(a)["Close"][-182:]
    return df

def volatilidad(activo):
  sumandos = (precio(activo).apply(lambda x: math.log(x)).diff().dropna()).apply(lambda x: x**2)
  vol = np.sqrt((1/T)*(sumandos.sum()))
  return vol

def max(a,b):
    if a<b:
     return b
    else:
     return a
 
def opcion_put(activo, K):
    n = 1000000 
    simu = np.array(np.random.normal(0,1,n))
    sim = pd.DataFrame({"Numeros simulados":list(simu)})
    S_0 = precio(activo)[-1]
    vol = volatilidad(activo)
    precios_sim = sim["Numeros simulados"].apply(lambda x: S_0*math.exp((0.0797-(1/2)*(vol**2))*(T)+(vol)*(x)*(np.sqrt(T))))
    payoff = precios_sim.apply(lambda x: max(K-x,0))
    P_0 = (math.exp(-0.0797*(T)))*(payoff.sum())*(1/n)
    return P_0
     
def opcion_put_bs(activo, K):
    S_0 = precio(activo)[-1]
    vol = volatilidad(activo)
    d_1 = (np.log(S_0/K)+(0.0797+(1/2)*(vol**2))*T)/(vol*np.sqrt(T))
    d_2 = d_1-vol*np.sqrt(T)
    P_cero = K*(np.exp(-0.0797*T))*stats.norm.cdf(-d_2)-S_0*stats.norm.cdf(-d_1)
    return P_cero

def trayectoria(activo, n):
  trayectoria = np.zeros((n+1,1))
  trayectoria[0] = precio(activo)[-1]
  vola = volatilidad(activo)
  dt = T/n
  ter_1 = (0.0797-0.5*(vola**2))*dt
  ter_2 = (vola)*(np.sqrt(dt))

  for i in range(n):
    trayectoria[i+1] = trayectoria[i]*(np.exp(ter_1 + ter_2*(np.random.normal(0,1))))

  return trayectoria

def trayectorias(activo, j, n):
  trayecs = np.zeros((n+1,j))
  trayecs[0,:] = precio(activo)[-1]
  volati = volatilidad(activo)
  dt = T/n
  e_1 = (0.0797-0.5*(volati**2))*dt
  e_2 = (volati)*(np.sqrt(dt))
  plt.figure(figsize=(20,6))

  for i in range(n):
    for k in range(j):
      trayecs[i+1,k] = trayecs[i,k]*(np.exp(e_1+e_2*(np.random.normal())))
  dataframes = [pd.DataFrame({"Valores":trayecs.transpose()[i]}) for i in range(j)]    
  graficas = [go.Line(x=dataframes[i].index, y=dataframes[i]["Valores"], mode="lines", name=f"Trayectoria {i+1}") for i in range(j)]
  # dic = {"x":0.9, "y":0.9, "xref":"container", "yref":"container", "bgcolor":"#E6F2FC"}
  estilo = go.Layout(title=f"Gráfica de {j} trayectorias simuladas del activo {activo}", legend=None)
  fig = go.Figure(data=graficas, layout=estilo)
  return st.plotly_chart(fig)

def precio_asiatica(activo,n,j):
    trayecs = np.zeros((n+1,j))
    trayecs[0,:] = precio(activo)[-1]
    volati = volatilidad(activo)
    dt = T/n
    e_1 = (0.0797-0.5*(volati**2))*dt
    e_2 = (volati)*(np.sqrt(dt))
    promedios = np.zeros((1,j))
    payoff = [[]for i in range(j)]

    for i in range(n):
        for k in range(j):
         trayecs[i+1,k] = trayecs[i,k]*(np.exp(e_1+e_2*(np.random.normal())))

    for k in range(j):
     payoff[k] = max(trayecs.transpose()[k,:].mean()-trayecs.transpose()[k,-1],0)
    precioo = np.exp(-0.0797*(T))*(1/j)*(sum(payoff))
    return precioo

def precio_asiatica_geo(activo,n,j,K):
  trayecs = np.zeros((n+1,j))
  trayecs[0,:] = precio(activo)[-1]
  volati = volatilidad(activo)
  dt = T/n
  e_1 = (0.0797-0.5*(volati**2))*dt
  e_2 = (volati)*(np.sqrt(dt))
  payoff = [[]for i in range(j)]

  for i in range(n):
      for k in range(j):
          trayecs[i+1,k] = trayecs[i,k]*(np.exp(e_1+e_2*(np.random.normal())))

  for k in range(j):
    payoff[k] = max(K-np.exp((1/len(trayecs.transpose()[k,:]))*sum(map(np.log,trayecs.transpose()[k,:]))),0)
  precio_geo = np.exp(-0.0797*(T))*(1/j)*(sum(payoff))
  return precio_geo

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
def remote_css(url):
        st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)    
