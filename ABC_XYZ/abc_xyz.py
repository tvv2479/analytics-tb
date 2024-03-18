#%%
# ПОЛУЧАЕМ ДАННЫЕ ИЗ БАЗЫ

from datetime import datetime, timedelta
import pandas as pd
import os
import sys
import plotly.express as px

sys.path.append(os.path.abspath('..'))
from load_data import dataSite
#%%
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
                            and product_type != ''
                                and name not like '%%ПОДАРОК%%';
'''


orders = dataSite(sql)
orders
# %%
# ОЧИСТКА ДАННЫХ. 
# В названиях типов товаров есть лишние символы.
# Нужно удалить лишние символы и привести к общему виду.

# Убираем лишние пробелы и переводим в нижний регистр
orders['product_type'] = orders['product_type'].str.strip(' ').str.lower()

# Замена названий типов на общепонятное.
orders['product_type'] = orders['product_type'].replace(['комплект  с юбкой', 'блузка', 'блуза двухсторонняя',
                                                         'платье-рубашка', 'платье-туника', 'платье-сарафан',
                                                         'платье-кафтан', 'пальто-бомбер', 'брючный комплект',
                                                         'комплект с юбкой'], 
                                                        ['комплект с юбкой', 'блуза', 'блуза', 'платье', 
                                                         'платье', 'платье', 'платье', 'бомбер', 
                                                         'брючный костюм', 'костюм с юбкой'])
# %%
# Группировка по типу продукта и расчёт количества и суммы
or_tab = orders[['name', 'price']]
ord_t = or_tab.groupby(['name'])['price'] \
.agg(revenue ='sum', amount='count') \
.sort_values(by = 'amount', ascending=False)
#%%

or_tab
# %%
# СЧИТАЕМ ABC

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

df_abc = abc_groupt[['revenue', 'amount', 'abc']].reset_index()
df_abc
# %%

# СЧИТАЕМ XYZ

# делаем дату без времени
orders['date'] = orders['date_update'].apply(lambda x: x.strftime('%Y-%m-%d'))
orders['year'] = orders['date_update'].apply(lambda x: x.strftime('%Y'))
orders['week'] = orders['date'].apply(lambda x: datetime.strptime(x, ('%Y-%m-%d')).isocalendar().week)

df = orders[['name', 'year', 'week']]
# Смотрим сколько раз покупали в каждый день
df_sales = df.groupby(['name', 'year', 'week'])['name'].agg(sales='count').reset_index()

# df_sal = df_sales[df_sales['sales'] >= 4]

# Считаем XYZ
# Находим стандиртное отклонение и среднее знячения
df_group = df_sales.groupby(['name'])['sales'].agg(standotkl='std', srednee='mean').reset_index()
# Получаем % (стандартное отклонение  / среднее)
df_group['prots'] = df_group['standotkl'] / df_group['srednee']
# Присваиваем значения по условию
df_group['xyz'] = df_group['prots'].apply(lambda x: 'X' if x <= 0.1 else ('Y' if x <= 0.25 else 'Z'))

df_xyz = df_group[['name', 'xyz']]
#%%
# ОБЪЕДИНЯЕМ В ABC-XYZ АНАЛИЗ

# Объединяем
df.abc_xyz = df_abc.merge(df_xyz, left_on='name', right_on='name')

df.abc_xyz['abc-xyz'] = df.abc_xyz['abc'] + df.abc_xyz['xyz']
# Оставляем количество покупок не менне 4х
df.abc_xyz = df.abc_xyz[df.abc_xyz['amount'] > 4]

abc_xyz = df.abc_xyz.groupby('abc-xyz')['abc-xyz'].agg(kol='count').reset_index()
abc_xyz
#%%

# ВИЗУАЛИЗАЦИЯ
fig = px.treemap(abc_xyz, path=['abc-xyz'], values = 'kol')
fig.show()
# %%
# ABC-XYZ анализ в таблице
df.abc_xyz

# %%
