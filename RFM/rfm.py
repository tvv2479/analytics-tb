#%%
from datetime import datetime, timedelta
import pandas as pd
import os
import sys
import plotly.express as px

sys.path.append(os.path.abspath('..'))
from load_data import dataSite
# %%
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