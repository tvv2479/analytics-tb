-- Многомерный ABC АНАЛИЗ

/*В таблице заказов нельзя увидеть наименование и тип товаров.
  Наименования и типы товаров можно увидеть в корзине. Собираем всё в одну таблицу.
  Смотрим типы товаров без названий т.к. наименования меняются каждый месяц, а товар 
  может "жить" всего несколько месяцев*/

with orders as (
     -- Готовим данные
     -- Все закрытые (оплаченные) заказы за период времени
     select order_id,
            date_update::date
       from site_update_order2
      where date_update::date between current_date - 90 and current_date - 1 
            and status_id  in ('F', 'SP')
            ),
            tovar as (
            -- Товары в каждом заказе
            select order_id,
                   date_update::date,
                   "name",
                   lower(trim(both from product_type)) as product_type,
                   product_size,
                   price
              from site_update_basket
             where order_id in (select order_id from orders)
                   and product_type is not null
                       and product_type != ''
                   ),
                   tovar_name as (
                   -- Упорядывачиваем тип  товаров
                   select order_id,
                          date_update,
                          "name",
                          case 
                   	         when product_type = 'платье-кафтан' then 'платье'
                   	         when product_type = 'платье-рубашка' then 'платье'
                   	         when product_type = 'платье-сарафан' then 'платье'
                   	         when product_type = 'платье-туника' then 'платье'
                   	         when product_type = 'комплект  с юбкой' then 'комплект с юбкой'
                   	         when product_type = 'блузка' then 'блуза'
                   	         when product_type = 'блуза двухсторонняя' then 'блуза'
                      	     when product_type = 'пальто-бомбер' then 'бомбер'
                   	         when product_type = 'брючный комплект' then 'брючный костюм'
                   	         when product_type = 'комплект с юбкой' then 'костюм с юбкой'
                   	         else product_type
                          end as name_type,
                          price
                     from tovar
                          ),
                          abc_sales as (
                          -- Выручка и количество по каждому типу товаров
                          select name_type,
                                 sum(price) as revenue,
                                 coalesce(count(name_type), 0) as amount
                            from tovar_name
                           group by name_type
                           order by 3 desc
                                 ),
                                 xyz_sales as (
                                 select name_type,
                                        to_char(date_update, 'YYYY-WW') as ym,
                                        count(name_type) as sales
                                   from tovar_name
                                  group by name_type, 2
                                  order by 2
                                        ),
                                        xyz_analysis as (
                                        select name_type,
                                               case
                                                 when stddev_samp(sales)/avg(sales) <= 0.75 then 'Z'
                                                 when stddev_samp(sales)/avg(sales) <= 0.9 then 'Y'
                                                 else 'X'
                                               end xyz_sales
                                          from xyz_sales
                                         group by name_type
                                               )
                                               select s.name_type,
                                                      case
                                                        when sum(amount) over(order by amount desc) / sum(amount) over() <= 0.8 then 'A'
                                                        when sum(amount) over(order by amount desc) / sum(amount) over() <= 0.95 then 'B'
                                                      else 'C'
                                                      end as amount_ABC,
                                                      case
                                                        when sum(revenue) over(order by revenue desc) / sum(revenue) over() <= 0.8 then 'A'
                                                        when sum(revenue) over(order by revenue desc) / sum(revenue) over() <= 0.95 then 'B'
                                                      else 'C'
                                                      end as revenue_ABC,
                                                      xyz.xyz_sales
                                                 from abc_sales s
                                                      left join xyz_analysis xyz
                                                           on s.name_type = xyz.name_type
                                                order by name_type;
                                                
