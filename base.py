# https://stackoverflow.com/questions/55269763/return-a-pandas-dataframe-as-a-data-table-from-a-callback-with-plotly-dash-for-p

############################################################################################################################################################
# IMPORTACIONES 
############################################################################################################################################################
#Sistema
import os
#DB
from sqlalchemy import create_engine, text

import logging
logging.basicConfig()
logging.disable(logging.INFO)
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)

#Datos, procesamiento
import pandas as pd
import numpy as np

#Fechas
import datetime as dt
from datetime import datetime, date, time, timedelta
import calendar

#Visualizacion
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
#%matplotlib inline
import plotly.io as pio
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objs as go
from dash import Dash
from dash import dcc
from dash import html
from dash import ctx,callback
from dash.dependencies import Input, Output, State
from dash import dash_table
stylesheet = [dbc.themes.BOOTSTRAP]

# Otras importaciones
from matplotlib import ticker
from matplotlib.ticker import FuncFormatter
from babel.numbers import format_currency

#PDF
#rom weasyprint import HTML, CSS
#from weasyprint.text.fonts import FontConfiguration

#Requests
import requests as req

import locale
locale.setlocale(locale.LC_ALL, '')
locale._override_localeconv["thousands_sep"] = "."
locale._override_localeconv["decimal_point"] = ","

import base64
import datetime
import io

############################################################################################################################################################
############################################################################################################################################################
### VARIABLES GLOBALES ###
df_original = pd.DataFrame()

############################################################################################################################################################
############################################################################################################################################################
### DEFINICION DE FUNCIONES UTILES ###

####################################################
# Funcion para iniciar el servidor de dash
####################################################
def run_server(self,
               port=8050,
               debug=True,
               threaded=True,
               **flask_run_options):
    self.server.run(port=port, debug=debug, **flask_run_options)

####################################################
# Funcion para retornar un div con tamaño, fuente, hijos e ID especificos
####################################################
def div_con_tamaño(children=[], font_size: int = 14, id: str = "undefined"):
    return html.Div(children=children, id=id, style={"fontSize": f"{font_size}px"})

####################################################
# Funcion para formatear los valores
####################################################
def formatearMoneda(x):
    # return '{:,.2f}'.format(x).replace(',','*').replace('.', ',').replace('*','.')
    return f"$U {'{:,.2f}'.format(x).replace(',','*').replace('.', ',').replace('*','.')}"

####################################################
# Funcion para formatear el valor para eje de la grafica
####################################################
def formatearEje(x, pos):
    # Aca muestra como moneda local
    # return format_currency(x, currency="$U", locale="es_UY")     
    # Muestra resumida segun cantidad de millones
    return f'{x//1_000_000:.0f} M'

####################################################
# Funcion que retorna una conexion a mysql
####################################################
def retornarConexion():
    # Conexion al servidor de Base de datos
    connection_string = "mysql+mysqlconnector://cpiriz:123*Caps.@192.168.37.118:3306/durtributos"
    engine = create_engine(connection_string, echo=True)
    cnn= engine.connect()
    return cnn

####################################################
# Funcion para retornar datos de la consulta contra mysql
####################################################
def retornarDatos(sql):
    return retornarConexion().execute(text(sql))

####################################################
# Funcion que retorna un DataFrame a partir de unos resultados
####################################################
def retornarDataFrame(sql):
    res = retornarDatos(sql)
    return pd.DataFrame.from_records(res, columns= res.keys())

####################################################
# Funcion par aasignar tipós a las columnas
####################################################
def definirTiposColumnas(df ,cols,tipos):
    i=0
    for c in cols:
        if(tipos[i].lower()=='datetime'):
            df[c]=pd.to_datetime(df[c],format="mixed")
        else:
            df[c]=df[c].astype(tipos[i])
        i+=1
    return df

####################################################
# Generacion del layout
####################################################

# external JavaScript files
external_scripts = [
    'https://www.google-analytics.com/analytics.js',
    {'src': 'https://cdn.polyfill.io/v2/polyfill.min.js'},
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.10/lodash.core.js',
        'integrity': 'sha256-Qqd/EfdABZUcAxjOkMi8eGEivtdTkh3b65xCZL4qAQA=',
        'crossorigin': 'anonymous'
    }
]

# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]


# Inicializacion de la aplicacion
app_dash = Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}], external_scripts=external_scripts,external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)


# Creacion del layout
app_dash.layout = html.Div(
    [
        html.H1(''),
        dcc.Tabs(
            id="tabs_idd", 
            value='cobros_lugar_sistema_fechas', 
            children=
            [
                dcc.Tab(label='1 - Carga', value='carga', selected_style={"color": "blue","background-color":"yellow"}),
                dcc.Tab(label='2 - Duplicados', value='duplicados', selected_style={"color": "blue","background-color":"yellow"}),
                dcc.Tab(label='3 - Nulos', value='nulos', selected_style={"color": "blue","background-color":"yellow"}),
                dcc.Tab(label='4 - Correlaciones', value='correlaciones', selected_style={"color": "blue","background-color":"yellow"}),
                dcc.Tab(label='5 - Normalizacion', value='normalizacion', selected_style={"color": "blue","background-color":"yellow"}),
                dcc.Tab(label='6 - Algoritmo', value='algoritmo', selected_style={"color": "blue","background-color":"yellow"}),
                dcc.Tab(label='7 - Entrenamiento', value='entrenamiento', selected_style={"color": "blue","background-color":"yellow"}),
                dcc.Tab(label='8 - Verificacion', value='verificacion', selected_style={"color": "blue","background-color":"yellow"}),
                dcc.Tab(label='9 - Modelo', value='modelo', selected_style={"color": "blue","background-color":"yellow"}),
                dcc.Tab(label='10 - Uso Modelo', value='usar_modelo', selected_style={"color": "blue","background-color":"yellow"})
            ]
        ),
        html.Div(
            id='contenido_tab',
            children=[],
            style={"display": "flex", "flex-direction": "column"}
        )
    ]
)
############################################################################################################################################################
############################################################################################################################################################


############################################################################################################################################################
##	Funciones de generacion de pestañas
############################################################################################################################################################
# Operaciones pestaña de carga

def retornarTabCarga():
    children= []
    children = [
        dcc.Upload(
            id='subidor_datos',
            children=html.Div(
                [
                    'Arrastrar o  ',
                    html.A('seleccionar ...')
                ]
            ),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True
        ),
        html.Div(id='salida_archivo_subido'),
    ]
    return children

def importar_datos(contents, filename, date):
    content_type, content_string = contents.split(',')
    global df_original

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        df_original = df.copy()
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data = df.to_dict('records'),
            columns = [{'name': i, 'id': i} for i in df.columns],
            page_size =10 
            
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Contenido crudo'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

@callback(Output('salida_archivo_subido', 'children'),
              Input('subidor_datos', 'contents'),
              State('subidor_datos', 'filename'),
              State('subidor_datos', 'last_modified'))
def actualizar_salida(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            importar_datos(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
    

############################################################################################################################################################
##	Callbacks
############################################################################################################################################################


####################################################
##	Cambio de tab
####################################################
@app_dash.callback(   
    Output('contenido_tab','children'),
    [Input("tabs_idd", "value")]
)
def actualizar_tab(valor_tab):
    hijos = []
    match valor_tab:
        case 'carga':
            return retornarTabCarga()
        case 'datos_morosidad':
            pass
        case _:
            hijos = ["Algo salio mal"]
    return hijos





# Inicio de la aplicacion
if __name__ == '__main__':
    app_dash.run_server(debug=True,port=8050, jupyter_mode="external")
    
    