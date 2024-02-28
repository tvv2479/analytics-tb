
#%%
from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import psycopg2
import pandas as pd
import configparser
import os
import sys
import scipy as sp
import numpy as np
import statistics as st

sys.path.append(os.path.abspath('..'))
from load_data import dataSite

# Загрузка данных
sql = '''
with orders as (
     -- Все закрытые (оплаченные) заказы за период времени.
     select order_id,
            date_update::date
       from site_update_order2
      where date_update::date between current_date - 90 and current_date - 1 
            and status_id  in ('F', 'SP')
            )
            -- Все товары из ордеров.
            select order_id,
                   date_update,
                   "name",
                   product_type,
                   product_size,
                   base_price,
                   price
              from site_update_basket sub 
             where order_id in (select order_id from orders)
                   and product_type is not null
                       and product_type != '';
'''


orders = dataSite(sql)

# Очитстка данных. В названиях типов товаров есть лишние символы.
# Нужно удалить лишние символы и привести к общему виду

orders['product_type'] = orders['product_type'].str.strip(' ').str.lower()

# Замена названий типов на общепонятное.
orders['product_type'] = orders['product_type'].replace(['комплект  с юбкой', 'блузка', 'блуза двухсторонняя',
                                                         'платье-рубашка', 'платье-туника', 'платье-сарафан',
                                                         'платье-кафтан', 'пальто-бомбер', 'брючный комплект',
                                                         'комплект с юбкой'], 
                                                        ['комплект с юбкой', 'блуза', 'блуза', 'платье', 
                                                         'платье', 'платье', 'платье', 'бомбер', 
                                                         'брючный костюм', 'костюм с юбкой'])

types = list(set(orders['product_type']))

# Группировка по типу продукта и расчёт количества и суммы
or_tab = orders[['product_type', 'price']]
ord_t = or_tab.groupby(['product_type'])['price'] \
.agg(revenue ='sum', amount='count') \
.sort_values(by = 'amount', ascending=False)

# Расчёт ABC анализа

groupt_df = ord_t.copy()
columns = ['revenue', 'amount']

# Считаем относительное количество
for col in columns:
  groupt_df[f'rel_{col}'] = groupt_df[col] / sum(groupt_df[col])
  groupt_df = groupt_df.sort_values(f'rel_{col}', ascending=False)
  groupt_df[f'cumsum_{col}'] = groupt_df[f'rel_{col}'].cumsum()
  groupt_df[f'abc_{col}'] = groupt_df[f'cumsum_{col}'].apply(lambda x: 'A' if x <= 0.8 else \
                                                                      ('B' if x <= 0.95 else 'C'))
  
abc_groupt = groupt_df[['revenue',	'amount', 'abc_amount', 'abc_revenue']]
abc_groupt['abc'] = abc_groupt['abc_amount'] + abc_groupt['abc_revenue']

df = abc_groupt[['revenue', 'amount', 'abc']]
df

# %%
