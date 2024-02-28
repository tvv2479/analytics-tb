
-- ABC анализ: https://www.youtube.com/watch?v=U48FCR95Qco
-- https://t.me/andron_233/25
-- https://www.unisender.com/ru/glossary/chto-takoe-abc-analiz-i-kak-ego-provesti/#anchor-1
-- https://www.unisender.com/ru/glossary/chto-takoe-xyz-analiz-i-kak-ego-primenyat-v-biznese/

-- Многомерный ABC АНАЛИЗ

/*В базе в таблице заказов нельзя увидеть наименование и тип товаров.
  Наименования и типы товаров можно увидеть в корзине.
  Смотрим типы товаров без названий т.к. наименования меняются каждый месяц, а товар может "жить" всего несколько месяцев*/

with orders as (
     -- Все закрытые (оплаченные) заказы за период времени
     select order_id,
            date_update::date
       from site_update_order2
      where date_update::date between current_date - 90 and current_date - 1 
            and status_id  in ('F', 'SP')
            ),
            tovar as (
            -- Уникальные типы товаров из корзин по каждому заказу 
            select distinct lower(trim(both from product_type)) as tovar_name
              from site_update_basket
             where order_id in (select order_id from orders)
                   and product_type is not null
                       and product_type != ''
                   ),
                   prodagi as (
                   -- Выручка и количество по каждому типу товаров
                   select lower(trim(both from product_type)) as tovar_name,
                          coalesce(count(product_type), 0) as kol_prodano,
                          sum(price) as viruchka
                     from site_update_basket 
                    where order_id in (select order_id from orders)
                    group by 1
                    order by 2 desc
                         ),
                         prod_sort as (
                         -- Продажи по каждому типу товаров (количество, выручка). 
                         -- Доходности нет т.к. отсутствуют данные по себестоимости.
                         select t.tovar_name,
                              coalesce(kol_prodano, 0) as kol_prodano,
                              coalesce(viruchka, 0) as viruchka
                         from tovar as t
                         left join prodagi as p
                              on t.tovar_name = p.tovar_name
                         order by 2 desc
                              ),
                              kol as (
                              -- Считаем процент от общего количества и суммы по каждому типу товаров.
                              select tovar_name,
                                   kol_prodano,
                                   viruchka,
                                   kol_prodano / sum(kol_prodano) over() as rel_kol,
                                   viruchka / sum(viruchka) over() as rel_viruchka
                              from prod_sort
                                   ),
                                   cumsum as (
                                   -- Считаем накопительный итог по процентам от общего количества
                                   select tovar_name,
                                             kol_prodano,
                                             viruchka,
                                             sum(rel_kol) over(order by rel_kol desc) as cum_sum_kol,
                                             sum(rel_viruchka) over(order by rel_viruchka desc) as cum_sum_viruchka
                                        from kol
                                             ),
                                             ABC_group as (
                                             -- Присваиваем группы ABC по количеству и по выручке
                                             select tovar_name,
                                                  kol_prodano,
                                                  viruchka,
                                                  case 
                                                       when cum_sum_kol <= 0.8 then 'A'
                                                       when cum_sum_kol <= 0.95 then 'B'
                                                       else 'C'
                                                  end as ABC_kol,
                                                  case 
                                                       when cum_sum_viruchka <= 0.8 then 'A'
                                                       when cum_sum_viruchka <= 0.95 then 'B'
                                                       else 'C'
                                                  end ABC_viruchka
                                             from cumsum
                                                  )
                                                  select tovar_name,
                                                            kol_prodano,
                                                            viruchka, 
                                                            ABC_kol||ABC_viruchka as abc,
                                                            case 
                                                            when stddev_pop(kol_prodano) over(order by kol_prodano desc) / avg(kol_prodano) over() <= 0.1 then 'X'
                                                            when stddev_pop(kol_prodano) over(order by kol_prodano desc) / avg(kol_prodano) over() <= 0.25 then 'Y'
                                                            else 'Z'
                                                            end as xyz
                                                       from ABC_group;
                                                
                                                
