


with count_clients as (
     -- Уникальные посетители за 5 месяцев каждый день
     select date_event,
            count(distinct client_id) as kol
       from ym_hits_obshee2
      where date_event between '2023-10-01' and '2024-02-29'
      group by 1
            ),
            october as (
            -- размах октября
            select max(kol) - min(kol) as razmah
              from count_clients
             where to_char(date_event, 'MM') = '10'
                   ),
                   november as (
                   -- размах ноября
                   select max(kol) - min(kol) as razmah
                     from count_clients
                    where to_char(date_event, 'MM') = '11'
                          ),
                          december as (
                          -- размах декабря
                          select max(kol) - min(kol) as razmah
                            from count_clients
                           where to_char(date_event, 'MM') = '12'
                                 ),
                                 january as (
                                 -- размах января
                                 select max(kol) - min(kol) as razmah
                                   from count_clients
                                  where to_char(date_event, 'MM') = '01'
                                        ),
                                        february as (
                                        -- размах февраля
                                        select max(kol) - min(kol) as razmah,
                                               round(avg(kol), 2) as srednee_feb
                                          from count_clients
                                         where to_char(date_event, 'MM') = '02'
                                               ),
                                               series as (
                                               select * from generate_series(1, 5) as ser
                                                      ),
                                                      razmah as (
                                                      -- собираем размахи по каждому месяцу
                                                      select ser,
                                                             case
	                                                           when ser = 1 then (select * from october)
                                                      	       when ser = 2 then (select * from november)
                                                      	       when ser = 3 then (select * from december)
                                                      	       when ser = 4 then (select * from january)
                                                      	       when ser = 5 then (select razmah from february)
                                                             end as month_t
                                                        from series
                                                             ),
                                                             sigm as (
                                                             -- считаем средний размах, сигму и откладываем 6 сигм
                                                             select sum(month_t) / max(ser) as avg_razmah,
                                                                    -- Применяем коэффициэнты из контрольных карт Шухарта для 5 месяцев 
                                                                    -- https://meganorm.ru/Data2/1/4294819/4294819315.pdf                                   
                                                                    round((sum(month_t) / max(ser)) / 2.326 , 2) as sigma,
                                                                    (select srednee_feb from february) as avg_feb,
                                                                    (select srednee_feb from february) + round((sum(month_t) / max(ser)) / 2.326, 2) as sigma_1,
                                                                    (select srednee_feb from february) + round((sum(month_t) / max(ser)) / 2.326, 2)*2 as sigma_2,
                                                                    (select srednee_feb from february) + round((sum(month_t) / max(ser)) / 2.326, 2)*3 as sigma_3,
                                                                    (select srednee_feb from february) - round((sum(month_t) / max(ser)) / 2.326, 2) as minus_sigma_1,
                                                                    (select srednee_feb from february) - round((sum(month_t) / max(ser)) / 2.326, 2)*2 as minus_sigma_2,
                                                                    (select srednee_feb from february) - round((sum(month_t) / max(ser)) / 2.326, 2)*3 as minus_sigma_3
                                                               from razmah
                                                                    ) 
                                                                    select date_event,
                                                                           kol,
                                                                           round(avg(kol) over(), 2) as avg_month,
                                                                           max((select avg_razmah from sigm)) over() as avg_razmah,
                                                                           max((select sigma_1 from sigm)) over() as sigma_1,
                                                                           max((select sigma_2 from sigm)) over() as sigma_2,
                                                                           max((select sigma_3 from sigm)) over() as sigma_3,
                                                                           max((select minus_sigma_1 from sigm)) over() as minus_sigma_1,
                                                                           max((select minus_sigma_2 from sigm)) over() as minus_sigma_2,
                                                                           max((select minus_sigma_3 from sigm)) over() as minus_sigma_3
                                                                      from count_clients
                                                                     where to_char(date_event, 'MM') = '02'
                                                                    
                                                             
                                                      
            

      
      
      
          