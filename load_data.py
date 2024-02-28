#%%
from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import psycopg2
import pandas as pd
import configparser

config = configparser.ConfigParser()
config.read('E:/Projects/tb/Analytics/config.ini')

# Подключение к базе аналитики

BdAnalisHost = config['KeyBd']['host']
BdAnalisUser = config['KeyBd']['bd_user']
BdAnalisName = config['KeyBd']['bd_name']
BdAnalisPass = config['KeyBd']['password']


engine = create_engine(f'postgresql+psycopg2://{BdAnalisUser}:{BdAnalisPass}@{BdAnalisHost}/{BdAnalisName}')


#%%
# Получение данных с сайта

def dataSite(sql):
    '''
    Функция получает данные из источника.\n
    dataSite(sql)\n
    sql - запрос к базе для получения данных.
    '''
    
    try:
        res = pd.read_sql(sql, engine)        
    except Exception as err:
            res = err
    
    return res


# %%
