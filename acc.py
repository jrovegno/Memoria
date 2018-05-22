import os
import requests
from io import StringIO
from functools import reduce
from random import sample
from urllib.parse import urlparse
from posixpath import join
import pandas as pd

"""
Metodo Cualicuantitativo para el cálculo de Indice de Recarga de Acuíferos
"""

# Pure functions
mult = lambda x, y: x * y

def diff(x, y):
    return x - y

def var_list(prefix, n):
    """Genera nombres para columans e indices"""
    return [f'{prefix}{x}' for x in range(1, n+1)]

def expert_survey(n):
    """Genera resultado encuesta de un experto para n variables"""
    return sample(range(1, n+1), n)

def random_survey(n=13, m=10):
    """Genera resultados de encuesta de m expertos para n varibles """
    # Genera un DataFrame vacio
    df = pd.DataFrame(index=var_list('v', n))
    # Rellena encuesta con resultados aleatorios
    return df.assign(**{col: expert_survey(n) for col in var_list('expert', m)})

def Fc(df):
    """Calculo de la comparación por pares"""
    aux = pd.DataFrame()
    for index, row in df.iterrows():
        row_index = df.loc[index,:]
        k = df.apply(lambda row: diff(row, row_index), axis=1)
        m = k > 0
        l = k.mask(m, 1).mask(~m, 0)
        aux[index] = l.apply(sum)
    return aux.T

def Wt(df):
    """Calcula pesos relativos"""
    fc = Fc(df)
    return fc.apply(sum, axis=1) / reduce(mult, fc.shape)

def W(df):
    """Calcula ponderaciones"""
    s = Wt(df)
    return s / sum(s)

def index(W, V):
    """
    Index: Indice cuali-cuantitativo, rango [1, n]
    W: Porderadores de las variables (Resultado de procesar encuestas expertos), rango (0, 1)
    V: Valor relativo de las variables en un lugar dado, rango [-r1, rj]
    """
    return sum(map(mult, W, V))

def fetch_survey(url):
    # Revisa url de la encuesta
    up = urlparse(url)
    if up.query != 'format=csv&gid=0':
        url = up._replace(path=join(os.path.dirname(up.path), 'export'),
                          query='format=csv&gid=0',
                          fragment='').geturl()
    # Leer datos desde resultados encuesta
    data = requests.get(url).content.decode('utf-8')
    df = pd.read_csv(StringIO(data), index_col=0, parse_dates=['Timestamp'])
    return df

def load_survey(n=13, m=10, filename='survey.xlsx'):
    # Leer excel guardado si existe
    df = pd.read_excel(filename) if os.path.isfile(filename) else None
    # Muestra encuesta a utilizar
    return df

def write_survey(df, filename='survey.xlsx'):
    df.to_excel(filename)
