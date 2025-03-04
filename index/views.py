from django.shortcuts import render
from utils import exe_sql_dict
import logging
import json

# Create your views here.
def index(request):
    
    if request.method == 'GET':
        monthly_sales_query = get_month_sales_query()
        monthly_sales = {
            'month_keys' : [i['month'] for i in monthly_sales_query],
            'month_values' : [i['monthly_sales'] for i in monthly_sales_query]
        }
        

        spu_sales_query = get_spu_sales_num_query()
        spu_sales_num={
            'name' : [i['spu_id'] for i in spu_sales_query],
            'values' : [i['total_sales'] for i in spu_sales_query]
        }
        
        insufficient_sku_list=get_skus_with_insufficient_stock()
        
        top_ten_consumers_query = get_top_ten_consumers_query()
        top_ten_consumers = {
            'customer_id_keys' : [i['customer_name'] for i in top_ten_consumers_query],
            'customer_id_values' : [i['total_sales'] for i in top_ten_consumers_query]
        }

        today_total_sales= get_today_total_sales_query()
        today_count_orders = get_today_count_orders()
        not_submitted_orders_count = get_not_submitted_orders_count()
        data = {
            'monthly_sales':json.dumps(monthly_sales),
            'spu_sales_num':json.dumps(spu_sales_num),
            'insufficient_sku_list':insufficient_sku_list,
            'top_ten_consumers':json.dumps(top_ten_consumers),
            'today_total_sales':today_total_sales,
            'today_count_orders':today_count_orders,
            'not_submitted_orders_count':not_submitted_orders_count
        }
        return render(request,'index/index.html',data)

def get_month_sales_query():
    get_total_sales_sql = '''
    SELECT 
        substr(date,1,7) AS month, 
        SUM(total_price) AS monthly_sales
    FROM 
        order_order
    WHERE 
        date >= DATE('now','-1 year')
    GROUP BY 
        month
    ORDER BY 
        month;
'''
    return exe_sql_dict(get_total_sales_sql)

def get_spu_sales_num_query():

    spu_num_sql = '''
    SELECT
        spu.id as spu_id,
        sum(ood.sku_num) as total_sales
    from
        order_orderdetail ood
    LEFT JOIN
        style_sku sku
    ON
        ood.sku_id = sku.id
    LEFT JOIN
        style_spu spu
    ON
        sku.spu_id = spu.id
    GROUP BY 
        sku.spu_id
    ORDER BY
        total_sales DESC
    limit 10;
    '''

    spu_sum = exe_sql_dict(spu_num_sql)
    return spu_sum

def get_skus_with_insufficient_stock():
    get_skus_with_insufficient_stock_sql = '''
  SELECT
        sku.id as sku_id,
        stock,
        loc.location_name||':'||loc.location_address as loc
    FROM
        style_sku sku
        LEFT JOIN inventory_inventory inv ON sku.id = inv.sku_id
        LEFT JOIN inventory_storage_location loc on inv.storage_location_id = loc.id
    WHERE
        inv.stock < 10
    OR 
        inv.stock IS NULL
    '''
    insufficient_sku_list = exe_sql_dict(get_skus_with_insufficient_stock_sql)
    return insufficient_sku_list

def get_top_ten_consumers_query():
    get_top_ten_consumers_sql = '''
    SELECT
        cc.name as customer_name,
        sum(oo.total_price) as total_sales
    from
        order_order oo
        LEFT JOIN customer_customer cc ON oo.customer_id = cc.id
    GROUP BY
        cc.name
    order BY
        sum(oo.total_price) DESC
    LIMIT
        10;
    '''
    top_ten_consumers_query = exe_sql_dict(get_top_ten_consumers_sql)
    return top_ten_consumers_query

def get_today_total_sales_query():
    get_today_total_sales_sql = '''
    SELECT
        SUM(total_price) AS total_sales
    FROM
        order_order
    WHERE
        DATE(date) = DATE('now');
    '''
    today_total_sales_query = exe_sql_dict(get_today_total_sales_sql)[0]
    logging.debug(today_total_sales_query)
    return today_total_sales_query

def get_today_count_orders():
    get_today_count_orders_sql = '''
    SELECT
        COUNT(*) AS total_orders
    FROM
        order_order
    WHERE
        DATE(date) = DATE('now');
    ''' 
    today_total_orders_query = exe_sql_dict(get_today_count_orders_sql)[0]
    logging.debug(today_total_orders_query)
    return today_total_orders_query

def get_not_submitted_orders_count():
    get_not_submitted_orders_count_sql = '''
    SELECT
        COUNT(*) AS order_count
    FROM
        order_order
    WHERE
        status = '0';
    '''
    not_submitted_orders_count_query = exe_sql_dict(get_not_submitted_orders_count_sql)[0]
    logging.debug(not_submitted_orders_count_query)
    return not_submitted_orders_count_query