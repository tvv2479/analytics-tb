#%%
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import plotly.express as px

sys.path.append(os.path.abspath('..'))
from load_data import dataSite

# Получаем первичные данные.

sql = '''
      select * 
        from new_hits nh 
       where date_event between '2023-10-01' and '2024-02-29'
      '''

hits = dataSite(sql)

# Количество кникальных посетителей в каждой дате
hitsGroupDay = hits.groupby('date_event')['client_id'].unique().apply(lambda x: len(x)).reset_index()
hitsGroupDay.rename(columns = {'client_id':'kol'}, inplace = True)
                    
# Добавляем в DF колонки с годом, месяцем и днём
hitsGroupDay['year_h'] = pd.to_datetime(hitsGroupDay['date_event']).dt.year
hitsGroupDay['month_h'] = pd.to_datetime(hitsGroupDay['date_event']).dt.month
hitsGroupDay['day_h'] = pd.to_datetime(hitsGroupDay['date_event']).dt.day

# Расчёт размаха по количеству в каждом месяце

# Размах в октябре
october = hitsGroupDay[hitsGroupDay['month_h'] == 10]
diff_kol_oct =(october['kol'].max() - october['kol'].min())

# Размах в ноябре
november = hitsGroupDay[hitsGroupDay['month_h'] == 11]
diff_kol_nov =(november['kol'].max() - november['kol'].min())

# Размах в декабре
december = hitsGroupDay[hitsGroupDay['month_h'] == 12]
diff_kol_dec =(december['kol'].max() - december['kol'].min())

# Размах в январе
january = hitsGroupDay[hitsGroupDay['month_h'] == 1]
diff_kol_jan =(january['kol'].max() - january['kol'].min())

# Размах в феврале
february = hitsGroupDay[hitsGroupDay['month_h'] == 2]
diff_kol_feb =(february['kol'].max() - february['kol'].min())

# Среднее занчение по количеству в феврале
feb = hitsGroupDay[hitsGroupDay['month_h'] == 2]
avg_feb = round(feb['kol'].mean(), 2)

# Средний размах за все месяцы
mes = [diff_kol_oct, diff_kol_nov, diff_kol_dec, diff_kol_jan, diff_kol_feb]
avg_razmah = np.average(mes)

# Считаем сигму
# Сумму размахов за каждый месяц делим на корличество месяцев.
# И результат делим на значенин d2 карт Шухарта. Значение за 5 месяцев.
# https://meganorm.ru/Data2/1/4294819/4294819315.pdf 

sigma = avg_razmah / 5

# Откладываем 6 сигм от среднего значения за февраль
sigma_1 = round(avg_feb - (sigma * 3), 2)
sigma_2 = round(avg_feb - (sigma * 2), 2)
sigma_3 = round(avg_feb - sigma , 2)
sigma_4 = round(avg_feb + sigma , 2)
sigma_5 = round(avg_feb + (sigma * 2), 2)
sigma_6 = round(avg_feb + (sigma * 3), 2)

# Визуализвция сигм
fig = plt.figure(figsize=(10,5))
plt.title('Метод 6 сигм')
plt.xlabel('Дата', labelpad=20)
plt.ylabel('Количество уникальных посещений', labelpad=20)
plt.xticks(rotation=90)

plt.plot(feb['date_event'], feb['kol'])
plt.axhline(y=avg_feb, alpha=0.5, linestyle='--', color='gray')
plt.axhline(y=sigma_1, alpha=0.5, linestyle='-', color='pink')
plt.axhline(y=sigma_6, alpha=0.5, linestyle='-', color='pink')
plt.axhline(y=sigma_2, alpha=0.5, linestyle='-', color='yellow')
plt.axhline(y=sigma_3, alpha=0.5, linestyle='-', color='yellow')
plt.axhline(y=sigma_4, alpha=0.5, linestyle='-', color='yellow')
plt.axhline(y=sigma_5, alpha=0.5, linestyle='-', color='yellow')

d1 = datetime.strptime('2024-02-03', '%Y-%m-%d')
d2 = datetime.strptime('2024-02-01', '%Y-%m-%d')

plt.annotate(
    'Среднее кол-во посетителей сайта',
    xy=(d1, avg_feb),
    xytext=(d2, 4100),
    arrowprops={
        'width': 0.3,
        'alpha': 0.5
    }
)

s1 = datetime.strptime('2024-02-27', '%Y-%m-%d')
plt.annotate('sigma 1', xy=(s1, sigma_1))
plt.annotate('sigma 2', xy=(s1, sigma_2))
plt.annotate('sigma 3', xy=(s1, sigma_3))
plt.annotate('sigma 4', xy=(s1, sigma_4))
plt.annotate('sigma 5', xy=(s1, sigma_5))
plt.annotate('sigma 6', xy=(s1, sigma_6))

