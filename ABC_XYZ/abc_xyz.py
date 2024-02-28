
#%%
from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import psycopg2
import pandas as pd
import configparser

# https://sky.pro/wiki/python/kak-importirovat-klass-python-iz-direktorii-vyshe/
import os
import sys
sys.path.append(os.path.abspath('..'))
from load_data import dataSite
#%%

sql = '''
select order_id,
       date_update::date
  from site_update_order2
 where date_update::date between current_date - 90 and current_date - 1 
       and status_id  in ('F', 'SP')
'''

#pd.read_sql(sql, engine)

df = dataSite(sql)
df
# %%
