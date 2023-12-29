### Librerías

import streamlit as st
import pandas as pd
import folium
from folium import plugins
from folium.plugins import HeatMapWithTime
from streamlit_folium import folium_static
from dateutil.relativedelta import *
import seaborn as sns; sns.set_theme()
import numpy as np
from PIL import Image
import requests
import pickle
from IPython.display import HTML

# Configuración warnings
# ==============================================================================
import warnings
warnings.filterwarnings('ignore')

path_favicon = './img/favicon.ico'
im = Image.open(path_favicon)
st.set_page_config(
    page_title="AI27",
    page_icon= im,
    layout="wide",
)

# Title of the main page
pathLogo = './img/AI27P&G.png'
display = Image.open(pathLogo)
display = np.array(display)
col1, col2, col3 = st.columns([1,5,1])
col2.image(display, use_column_width=True)

@st.cache_data(show_spinner='Actualizando Datos... Espere...', persist=True)
def load_df():
    
    rEmbarques = './data/Salidas PG.xlsx'
    Embarques = pd.read_excel(rEmbarques, sheet_name = "Data")
    Embarques['Inicio'] = pd.to_datetime(Embarques['Inicio'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    Embarques['Arribo'] = pd.to_datetime(Embarques['Arribo'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    Embarques['Finalización'] = pd.to_datetime(Embarques['Finalización'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    Embarques.Arribo.fillna(Embarques.Finalización, inplace=True)
    Embarques['TiempoCierreServicio'] = (Embarques['Finalización'] - Embarques['Arribo'])
    Embarques['TiempoCierreServicio'] = Embarques['TiempoCierreServicio']/np.timedelta64(1,'h')
    Embarques['TiempoCierreServicio'].fillna(Embarques['TiempoCierreServicio'].mean(), inplace=True)
    Embarques['TiempoCierreServicio'] = Embarques['TiempoCierreServicio'].astype(int)
    Embarques['Destinos'].fillna('OTRO', inplace=True)
    Embarques['Línea Transportista'].fillna('OTRO', inplace=True)
    Embarques['Duración'].fillna(Embarques['Duración'].mean(), inplace=True)
    Embarques['Duración'] = Embarques['Duración'].astype(int)
    Embarques['Mes'] = Embarques['Inicio'].apply(lambda x: x.month)
    #Embarques['Mes'] = Embarques['MesN'].map({1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"})
    Embarques['DiadelAño'] = Embarques['Inicio'].apply(lambda x: x.dayofyear)
    Embarques['SemanadelAño'] = Embarques['Inicio'].apply(lambda x: x.weekofyear)
    Embarques['DiadeSemana'] = Embarques['Inicio'].apply(lambda x: x.dayofweek)
    Embarques['Quincena'] = Embarques['Inicio'].apply(lambda x: x.quarter)
    #Embarques['Mes'] = Embarques['MesN'].map({1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"})
    Embarques['Origen Destino'] = Embarques['Estado Origen'] + '-' + Embarques['Estado Destino']
    #Embarques = Embarques.dropna() 
    return Embarques

@st.cache_data(show_spinner='Cargando Datos... Espere...', persist=True)
def load_HR():

    rutaA = r'./data/Robos PG.xlsx'
    Robos = pd.read_excel(rutaA, sheet_name = "Data")
    Robos = Robos.drop(['Operadores','CM', 'Línea Reacción'], axis=1)
    Robos['Fecha'] = Robos['Fecha'].dt.strftime('%m/%d/%Y')
    Robos['Fecha'] = pd.to_datetime(Robos['Fecha'], format="%Y/%m/%d", infer_datetime_format=True)
    Robos['Año'] = Robos.Fecha.apply(lambda x: x.year)
    Robos['MesN'] = Robos['Fecha'].apply(lambda x: x.month)
    Robos['Mes'] = Robos['MesN'].map({1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"})
    Robos['Dia'] = Robos.Fecha.apply(lambda x: x.day)
    Robos['Fecha y Hora'] = pd.to_datetime(Robos['Fecha y Hora'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    Robos = Robos.dropna()

    return Robos

@st.cache_data(show_spinner='Cargando Datos... Espere...', persist=True)
def load_AN():
    
    rutaAR = './data/AnomaliasPG.xlsx'
    ER = pd.read_excel(rutaAR, sheet_name = "Data")
    ER['Comentarios'] = ER['Comentarios'].fillna('SIN COMENTARIOS')
    ER['Anomalía'] = ER['Anomalía'].fillna('SIN ALERTAS')
    ER['Comentarios'] = ER['Comentarios'].astype(str)
    ER['Anomalía'] = ER['Anomalía'].astype(str)
    ER['Cliente'] = ER['Cliente'].astype(str)
    ER['Fecha'] = pd.to_datetime(ER['Fecha'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    ER['Año'] = ER['Fecha'].apply(lambda x: x.year)
    ER['MesN'] = ER['Fecha'].apply(lambda x: x.month)
    ER['Mes'] = ER['MesN'].map({1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"})
    ER['Dia'] = ER['Fecha'].apply(lambda x: x.day)
    ER['Hora'] = ER['Fecha'].apply(lambda x: x.hour)
    ER['Latitud'].fillna(ER['Latitud'].mean(), inplace=True)
    ER['Longitud'].fillna(ER['Longitud'].mean(), inplace=True)
    ER = ER.dropna()

    return ER

@st.cache_data(show_spinner='Procesando Datos... Espere...', persist=True)
def load_AR():
    rutaAR = './data/Anomalias Robos PG.xlsx'
    AR = pd.read_excel(rutaAR, sheet_name = "Data")
    AR['Año'] = AR['Fecha'].apply(lambda x: x.year)
    AR['MesN'] = AR['Fecha'].apply(lambda x: x.month)
    AR['Mes'] = AR['MesN'].map({1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto", 9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"})
    AR['Hora'] = AR['Fecha'].apply(lambda x: x.hour)
    AR['Estadías NOM-087'] = AR['DuracionEstimada'].map(lambda x: int(x/5) if x > 5 else 0)
    #AR['Estadías NOM-087'] = np.ceil(AR['Estadías NOM-087'])
    AR['Origen Destino'] = AR['EstadoOrigen'] + '-' + AR['EstadoDestino']
    AR = AR.drop(['Número Envío'], axis=1)
    AR = AR.dropna()
    return AR

def GenerarMapaBase(Centro=[20.5223, -99.8883], zoom=8):
        MapaBase = folium.Map(location=Centro, control_scale=True, zoom_start=zoom)
        return MapaBase

def map_coropleta_fol(df, df2):
    
        #geojson_url = './data/mexicoHigh.json'
        geojson_url = 'https://raw.githubusercontent.com/angelnmara/geojson/master/mexicoHigh.json'
        mx_estados_geo = requests.get(geojson_url).json()

        MapaMexico1 = GenerarMapaBase()

        FeatRobo = folium.FeatureGroup(name='Robos')
        #Recorrer marco de datos y agregar cada punto de datos al grupo de marcadores
        Latitudes2 = df['Latitud'].to_list()
        Longitudes2 = df['Longitud'].to_list()
        Popups2 = df['Cliente'].to_list()
        Popups3 = df['Tipo evento'].to_list()
        Popups4 = df['Estado'].to_list()
        Popups5 = df['Origen'].to_list()
        Popups6 = df['Destinos'].to_list()
        Popups7 = df['Línea transportista'].to_list()
        Popups8 = df['Fecha y Hora'].to_list()

        for lat2, long2, pop2, pop3, pop4, pop5, pop6, pop7, pop8 in list(zip(Latitudes2, Longitudes2, Popups2, Popups3, Popups4, Popups5, Popups6, Popups7, Popups8)):
            fLat2 = float(lat2)
            fLon2 = float(long2)
            if pop3 == "Consumado":
                folium.Circle(
                    radius=200,
                    location=[fLat2,fLon2],
                    popup= [pop2,pop3,pop4, pop5, pop6, pop7, pop8],
                    fill=False,
                    color="darkred").add_to(FeatRobo)
            else:
                folium.Circle(
                    radius=200,
                    location=[fLat2,fLon2],
                    popup= [pop2,pop3,pop4, pop5, pop6, pop7, pop8],
                    fill=False,
                    color="darkgreen").add_to(FeatRobo)
        
        df1 = pd.DataFrame(pd.value_counts(df['Estado']))
        df1 = df1.reset_index()
        df1.rename(columns={'index':'Estado','Estado':'Total'},inplace=True)

        folium.Choropleth(
            geo_data=mx_estados_geo,
            name="Mapa Coropleta",
            data=df1,
            columns=["Estado", "Total"],
            key_on="feature.properties.name",
            fill_color="OrRd",
            fill_opacity=0.7,
            line_opacity=.1,
            legend_name="Total de Robos",
            #nan_fill_color = "White",
            nan_fill_opacity=0.1,
            show=True,
            overlay=True,
            Highlight= True,
            ).add_to(MapaMexico1)

        df2['Contar'] = 1
        df_hora1 = []

        for hour in df2.Hora.sort_values().unique():
            df_hora1.append(df2.loc[df2.Hora == hour, ['Latitud', 'Longitud', 'Contar']].groupby(['Latitud', 'Longitud']).sum().reset_index().values.tolist())
    
        HeatMapWithTime(df_hora1, radius=5, gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'}, name="Mapa Calor", min_opacity=0.5, max_opacity=0.8, use_local_extrema=True).add_to(MapaMexico1)

        MapaMexico1.add_child(FeatRobo)
        folium.LayerControl().add_to(MapaMexico1)
        #Agregar Botón de Pantalla Completa 
        plugins.Fullscreen(position="topright").add_to(MapaMexico1)

        #Mostrar Mapa
        folium_static(MapaMexico1, width=1370)

def df_proba_robo(uploaded_file):
        
        input_df = pd.read_excel(uploaded_file, sheet_name = "Plantilla")
        input_df = input_df.dropna() 
        input_df['Fecha Creación'] = pd.to_datetime(input_df['Fecha Creación'], format='%Y-%m-%d %H:%M:%S',errors='coerce')
        input_df['Duración'] = input_df['Duración'].astype(int)
        input_df['Mes'] = input_df['Fecha Creación'].apply(lambda x: x.month)
        input_df['DiadelAño'] = input_df['Fecha Creación'].apply(lambda x: x.dayofyear)
        input_df['SemanadelAño'] = input_df['Fecha Creación'].apply(lambda x: x.weekofyear)
        input_df['DiadeSemana'] = input_df['Fecha Creación'].apply(lambda x: x.dayofweek)
        input_df['Quincena'] = input_df['Fecha Creación'].apply(lambda x: x.quarter)
        input_df.drop(['Fecha Creación'], axis = 'columns', inplace=True)
        input_df = input_df[['Origen Destino','Tipo Monitoreo', 'Tipo Unidad', 'Duración', 'Mes', 'DiadelAño', 'SemanadelAño', 'DiadeSemana', 'Quincena']]
        return input_df

def resultados_proba(uploaded_file):
    
    df = pd.read_excel(uploaded_file, sheet_name = "Plantilla")
    df = df.dropna()
    df = df[['Bitácora','Origen','Destino','Tipo Monitoreo', 'Tipo Unidad']]
    df['Bitácora'] = df['Bitácora'].astype('str')
    return  df
    
@st.cache_resource
def load_model():
    return pickle.load(open('risk_prob_pg.pkl', 'rb'))

def color(val):
    d = {90:'red', 60: 'yellow', 40:'goldenrod', 10: 'green'}
    return f'background-color: {d[val]}; color: {d[val]}' if val in d else ''

try:

    df = load_HR()
    df1 = load_AR()
    df2 = load_AN()

    #df = df[['Año', 'Tipo evento', 'Fecha y Hora', 'Estado', 'Tramo', 'Mes', 'Día']]

    #df['Estatus'] = df['Tipo evento'].map(lambda x: 1 if x == "Consumado" else 0)

    #El de abajo sirve
    #st.dataframe(df.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)
    #st.dataframe(df.style.applymap(lambda x: 'background-color: red' if x == "Consumado" else 'background-color: green', subset=['Tipo evento']), hide_index= True)

    #st.dataframe(df['Estatus'].style.map(lambda x: 'color: red' if x == 0 else 'color: green'))
    st.markdown("<h3 style='text-align: left;'>PLANNER MENSUAL</h3>", unsafe_allow_html=True)

    container1 = st.container()
    allb1 = st.checkbox("Seleccionar Todos", key="chk1")
    if allb1:
        sorted_unique_mes = sorted(df['Mes'].unique())
        selected_mes = container1.multiselect('Mes(es):', sorted_unique_mes, sorted_unique_mes, key="Mes1")
        df_selected_mes = df[df['Mes'].isin(selected_mes)].astype(str)
    else:
        sorted_unique_mes = sorted(df['Mes'].unique())
        selected_mes = container1.multiselect('Mes(es):', sorted_unique_mes, key="Mes2")
        df_selected_mes = df[df['Mes'].isin(selected_mes)].astype(str)

    c1, c2, c3, c4, c5, c6, c7 = st.columns([1,1,1,1,1,1,1])
    with c1:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>1</h5>", unsafe_allow_html=True)
            day1 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "1"]
            day1 = day1[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day1.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c2:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>2</h5>", unsafe_allow_html=True)
            day2 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "2"]
            day2 = day2[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day2.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c3:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>3</h5>", unsafe_allow_html=True)
            day3 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "3"]
            day3 = day3[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day3.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c4:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>4</h5>", unsafe_allow_html=True)
            day4 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "4"]
            day4 = day4[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day3.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c5:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>5</h5>", unsafe_allow_html=True)
            day5 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "5"]
            day5 = day5[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day5.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c6:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>6</h5>", unsafe_allow_html=True)
            day6 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "6"]
            day6 = day6[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day6.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c7:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>7</h5>", unsafe_allow_html=True)
            day7 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "7"]
            day7 = day7[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day7.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    c8, c9, c10, c11, c12, c13, c14 = st.columns([1,1,1,1,1,1,1])
    with c8:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>8</h5>", unsafe_allow_html=True)
            day8 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "8"]
            day8 = day8[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day8.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c9:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>9</h5>", unsafe_allow_html=True)
            day9 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "9"]
            day9 = day9[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day9.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c10:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>10</h5>", unsafe_allow_html=True)
            day10 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "10"]
            day10 = day10[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day10.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c11:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>11</h5>", unsafe_allow_html=True)
            day11 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "11"]
            day11 = day11[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day11.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c12:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>12</h5>", unsafe_allow_html=True)
            day12 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "12"]
            day12 = day12[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day12.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c13:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>13</h5>", unsafe_allow_html=True)
            day13 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "13"]
            day13 = day13[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day13.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c14:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>14</h5>", unsafe_allow_html=True)
            day14 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "14"]
            day14 = day14[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day14.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    c15, c16, c17, c18, c19, c20, c21 = st.columns([1,1,1,1,1,1,1])
    with c15:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>15</h5>", unsafe_allow_html=True)
            day15 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "15"]
            day15 = day15[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day15.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c16:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>16</h5>", unsafe_allow_html=True)
            day16 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "16"]
            day16 = day16[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day16.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c17:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>17</h5>", unsafe_allow_html=True)
            day17 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "17"]
            day17 = day17[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day17.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c18:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>18</h5>", unsafe_allow_html=True)
            day18 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "18"]
            day18 = day18[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day18.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c19:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>19</h5>", unsafe_allow_html=True)
            day19 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "19"]
            day19 = day19[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day19.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c20:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>2o</h5>", unsafe_allow_html=True)
            day20 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "20"]
            day20 = day20[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day20.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c21:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>21</h5>", unsafe_allow_html=True)
            day21 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "21"]
            day21 = day21[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day21.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    c22, c23, c24, c25, c26, c27, c28 = st.columns([1,1,1,1,1,1,1])
    with c22:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>22</h5>", unsafe_allow_html=True)
            day22 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "22"]
            day22 = day22[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day22.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c23:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>23</h5>", unsafe_allow_html=True)
            day23 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "23"]
            day23 = day23[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day23.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c24:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>24</h5>", unsafe_allow_html=True)
            day24 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "24"]
            day24 = day24[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day24.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c25:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>25</h5>", unsafe_allow_html=True)
            day25 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "25"]
            day25 = day25[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day25.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c26:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>26</h5>", unsafe_allow_html=True)
            day26 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "26"]
            day26 = day26[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day26.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c27:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>27</h5>", unsafe_allow_html=True)
            day27 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "27"]
            day27 = day27[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day27.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c28:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>28</h5>", unsafe_allow_html=True)
            day28 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "28"]
            day28 = day28[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day28.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    c29, c30, c31, c32, c33, c34, c35 = st.columns([1,1,1,1,1,1,1])
    with c29:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>29</h5>", unsafe_allow_html=True)
            day29 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "29"]
            day29 = day29[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day29.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c30:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>30</h5>", unsafe_allow_html=True)
            day30 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "30"]
            day30 = day30[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day30.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c31:
        with st.container(border=True):
            st.markdown("<h5 style='text-align: left;'>31</h5>", unsafe_allow_html=True)
            day31 = df_selected_mes.loc[df_selected_mes.loc[:, 'Día'] == "31"]
            day31 = day31[['Año', 'Tipo evento', 'Estado', 'Tramo']]
            st.dataframe(day31.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

            #day31 = df_selected_mes.groupby(by=['Día'])
            #d31 = day31.apply(lambda x: x[x['Día'] == 31])
            #d31 = d31[['Año', 'Tipo evento', 'Fecha y Hora', 'Estado', 'Tramo']]
            #st.dataframe(d31.style.applymap(lambda x: 'color: red' if x == "Consumado" else 'color: green', subset=['Tipo evento']), hide_index= True)

    with c32:
        st.container(border=None)

    with c33:
        st.container(border=None)

    with c34:
        st.container(border=None)

    with c35:
        st.container(border=None)

    st.markdown("<h3 style='text-align: left;'>MAPA DE CALOR</h3>", unsafe_allow_html=True)

    # Mapa

    d1 = df_selected_mes.copy()
    d2 = df2.copy() # anomalías

    d1['Cod1'] = d1.Cliente + d1.Año.astype(str) + d1.Mes
    d2['Cod2'] = d2.Cliente + d2.Año.astype(str) + d2.Mes
    filtro = d2[d2['Cod2'].isin(d1['Cod1'])]

    mapa = map_coropleta_fol(df_selected_mes, filtro)

    #Modulo de Predictivo
    st.markdown("<h3 style='text-align: left;'>PRIORIZACIÓN DE LOS SERVICIOS</h3>", unsafe_allow_html=True)

    st.write(""" 
    Pasos a seguir para este módulo:
    1. Descargar archivo **"BITÁCORAS"** (Prebitácoras) de **P&G** del **Área de Centro de Monitoreo** del **PowerBI**, en el **Reporte CM**, sección **Prebitácoras**.
    2. Abrir archivos de Excel **"BITÁCORAS"** y **"Plantilla para Probabilidad de Robo"**.
    3. Convertir archivo descargado de prebitácora **"BITÁCORAS"** en plantilla para probabilidad de robo, para esto debe:
    + Copiar datos de la columna **"Creación"** del archivo **"BITÁCORAS"** y pegar en columna **"Fecha Creación"** del archivo **"Plantilla para Probabilidad de Robo"**.
    + Copiar datos de la columna **"Origen"** del archivo **"BITÁCORAS"** y pegar en columna **"Origen"** del archivo **"Plantilla para Probabilidad de Robo"**.
    + Copiar datos de la columna **"Destino"** del archivo **"BITÁCORAS"** y pegar en columna **"Destino"** del archivo **"Plantilla para Probabilidad de Robo"**.
    + Copiar datos de la columna **"Tipo Monitoreo"** del archivo **"BITÁCORAS"** y pegar en columna del mismo nombre en el archivo **"Plantilla para Probabilidad de Robo"**.
    + Registrar datos de la columna **"Tipo Unidad"** por cada servicio en el archivo **"Plantilla para Probabilidad de Robo"**
    + Por último, guardar archivo **"Plantilla para Probabilidad de Robo"**.
    4. Finalmente, subir archivo **"Plantilla para Probabilidad de Robo"** en la aplicación.
    """)

    df3 = load_df()
    
    uploaded_file = st.file_uploader("Subir archivo Excel de pre-bitácora", type=['xlsx'])

    if uploaded_file is not None:

        entrada_datos = df_proba_robo(uploaded_file)

    else:
        st.warning("Se requiere subir archivo Excel")

    dsr = df3.copy()
    dsr.drop(['Bitácora','Total Anomalías','Calificación','TiempoCierreServicio','Cliente','Origen','Estado Origen','Destinos','Estado Destino','Línea Transportista','Inicio','Arribo','Finalización','Tiempo Recorrido'], axis = 'columns', inplace=True)
    dsr = dsr[['Origen Destino','Tipo Monitoreo', 'Tipo Unidad', 'Duración', 'Mes', 'DiadelAño', 'SemanadelAño', 'DiadeSemana', 'Quincena', 'Robo']]
    data_sr = dsr.drop(columns=['Robo'])
    data_proba_robos = pd.concat([entrada_datos,data_sr],axis=0)

    # Codificación de características ordinales

    encode = ['Origen Destino', 'Tipo Unidad', 'Tipo Monitoreo']
    for col in encode:
        dummy = pd.get_dummies(data_proba_robos[col], prefix=col)
        data_proba_robos = pd.concat([data_proba_robos,dummy], axis=1)
        del data_proba_robos[col]

    cantidad_datos_input = len(entrada_datos)
    data_proba_robos1 = data_proba_robos[:cantidad_datos_input] # Selects only the first row (the user input data)

    load_clf = load_model()
    prediction_proba = load_clf.predict_proba(data_proba_robos1)

    prediction_proba1 = pd.DataFrame(prediction_proba, columns = ['NO','SI'])
    entrada_datos1 = resultados_proba(uploaded_file)
    entrada_datos2 = pd.concat([entrada_datos1,prediction_proba1], axis=1)
    entrada_datos2 = entrada_datos2[['Bitácora','Origen','Destino','Tipo Monitoreo', 'Tipo Unidad', 'SI']]
    entrada_datos2 = entrada_datos2.rename(columns={'SI':'% Riesgo'})
    entrada_datos2['% Riesgo'] = round(entrada_datos2['% Riesgo'] * 100,2)

    #Indice de priorizacion
    elementos = {"Prioridad 1" : 90, "Prioridad 2": 60, "Prioridad 3": 40, "Prioridad 4": 10}
    prioridad = pd.DataFrame(elementos, index = [0])

    st.markdown("<h5 style='text-align: left;'>Orden de Priorización de Servicios</h5>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.dataframe(prioridad.style.applymap(color), hide_index= True)

    col4, col5, col6 = st.columns([1,5,1])
    #st.markdown("<h5 style='text-align: left;'>% Riesgo de los Servicios</h5>", unsafe_allow_html=True)
    with col5:
        #entrada_datos2.style.format({'% Riesgo': "{:.2}"})
        st.dataframe(entrada_datos2.style.format({'% Riesgo': "{:.2f}"}).applymap(lambda x: f'background-color: red; color: darkred' if x >= 70 else \
                                            f'background-color: yellow; color: darkgoldenrod' if x < 70 and x >= 50 else \
                                            (f'background-color: goldenrod; color: gold' if x < 50 and x >= 20 else f'background-color: green; color: greenyellow'), subset= ['% Riesgo']), hide_index= True)

    #Modulo de Zonas de Riesgo
    st.markdown("<h3 style='text-align: left;'>ZONAS DE RIESGO DE LOS SERVICIOS</h3>", unsafe_allow_html=True)

    df4 = entrada_datos.copy()  # Aca tiene el origen destino, la columna se llama Origen Destino
    df5 = entrada_datos2.copy()
    df6 = pd.concat([df5,df4], axis=1)
    df6 = df6[['Bitácora','Origen','Destino','Origen Destino']]
    
    df7= df.copy() # copiar historico de robos
    df7['Origen Destino'] = df7['Estado Origen'] + '-' + df7['Estado Destino']

    filtro1 = df7[df7['Origen Destino'].isin(df6['Origen Destino'])] # aca se aplica filtro para buscar los tramos basados en origen y destino

    res= df6.merge(df7, on="Origen Destino", how="left")
    res['Location'] = res['Latitud'].astype(str) + ',' +  res['Longitud'].astype(str)
    res['Ubic'] = 'https://maps.google.com?q='+ res.Location
    res = res[['Bitácora_x','Origen_x','Destino','Tramo','Ubic']]
    res = res.rename(columns={'Bitácora_x':'Bitácora', 'Origen_x':'Origen', 'Destino':'Destino', 'Tramo':'Zona de Riesgo', 'Ubic':'Ubicación de Referencia'})
    res = res.drop_duplicates()
    res['Zona de Riesgo'] = res['Zona de Riesgo'].fillna('Sin registro histórico')
    col4, col5, col6 = st.columns([0.5,6,0.5])
    with col5:
        st.dataframe(res,column_config={"Ubicación de Referencia": st.column_config.LinkColumn("Ubicación Referencial")}, hide_index=True)
    
    # Patron de Anomalias en Robos
    st.markdown("<h3 style='text-align: left;'>PATRÓN DE ANOMALÍAS EN ROBOS</h3>", unsafe_allow_html=True)
    df8 = df1.copy() #Anomalias en Robos
    df9 = filtro1.copy() #filtro de origen destino de zonas de riesgo

    df10 = df8[df8['Origen Destino'].isin(df9['Origen Destino'])] # aca se aplica filtro para buscar los tramos basados en origen y destino

    df11 = df.copy()
    df11['Origen Destino'] = df11['Estado Origen'] + '-' + df11['Estado Destino']
    df12 = df11[df11['Origen Destino'].isin(df10['Origen Destino'])] # aca se aplica filtro para buscar los tramos basados en origen y destino
    df13 = pd.DataFrame(df12.groupby("Origen Destino")["Bitácora"].count())
    table = pd.pivot_table(df10, index = ["Origen Destino", "Distancia", "DuracionEstimada", "Estadías NOM-087"], columns = ["Anomalía"], aggfunc = 'size', fill_value=0)
    df14 = table.reset_index()
    df15 = table.div(df13.values)
    df15 = df15.apply(np.ceil)
    st.dataframe(df15)

    
except UnboundLocalError as e:
    print("Seleccionar: ", e)

except ZeroDivisionError as e:
    print("Seleccionar: ", e)

except KeyError as e:
    print("Seleccionar: ", e)

except ValueError as e:
    print("Seleccionar: ", e)

except IndexError as e:
    print("Seleccionar: ", e)

except NameError as e:
    print("Seleccionar: ", e)