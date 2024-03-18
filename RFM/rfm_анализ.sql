

with users_activity as (
     -- Собмраем данные по давности, частоте и деньгам, 
     select sio.user_id,
            su.email,
            max(CURRENT_DATE) - max(sio.date_insert::date) as Recency,
            count(sio.date_insert::date) as Frequency,
            sum(sio.price) as Monetary
       from site_insert_order2 sio 
            join site_user2 su on sio.user_id = su.id 
      where sio.date_insert between CURRENT_DATE - INTERVAL '6 month' and CURRENT_DATE
      group by sio.user_id, su.email
     having user_id != 8753
             ),
             borders as (
             -- Подбираем пороги для градации
             select percentile_disc(0.33) within group (order by Recency desc) as R_33,
                    percentile_disc(0.66) within group (order by Recency desc) as R_66,
                    percentile_disc(0.33) within group (order by Frequency) as F_33, 
                    percentile_disc(0.66) within group (order by Frequency) as F_66,
                    percentile_disc(0.2) within group (order by Monetary) as M_02,
                    percentile_disc(0.4) within group (order by Monetary) as M_04,
                    percentile_disc(0.6) within group (order by Monetary) as M_06,
                    percentile_disc(0.8) within group (order by Monetary) as M_08
               from users_activity
               ),
               znacheniya as (
               -- Присваиваем значения по градации
               select users_activity.user_id,
                      users_activity.email,
                      case 
                          when users_activity.Recency < borders.R_33 then 3
                          when users_activity.Recency < borders.R_66 then 2
                          else 1
                       end as Recency,
                      case 
                          when users_activity.Frequency < borders.F_33 then 3
                          when users_activity.Frequency < borders.F_66 then 2
                          else 1
                       end as Frequency,
                     case 
                         when users_activity.Monetary < borders.M_02 then 5
                         when users_activity.Monetary < borders.M_04 then 4
                         when users_activity.Monetary < borders.M_06 then 3
                         when users_activity.Monetary < borders.M_08 then 2
                         else 1
                      end as Monetary        
                from users_activity, borders
                ),
                rfm_an as (
                -- Получаем RFM
                select user_id,
                       email,
                       Recency::text ||Frequency::text ||Monetary::text  as rfm
                  from znacheniya
                       )
                       select * from rfm_an;
                       
                      -- Элемент для визуализации 
                      select rfm,
                              count(rfm) as cnt                                     
                         from rfm_an
                        group by rfm
                        order by rfm