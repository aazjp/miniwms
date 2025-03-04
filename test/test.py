

p=['1','2','3']
where_clause = " WHERE " + " AND ".join(p)
print(where_clause)

a= ','.join(['?']*9)
print(a)

import sqlite3

with sqlite3.connect('./db.sqlite3') as conn:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT * FROM inventory_inventory_record 
                   where operation_type in (?)
                   '''
                   ,
                   ['扫码入库']
                   )
    ret = cursor.fetchall()
    print(ret)