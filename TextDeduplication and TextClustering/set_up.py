# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 10:32:13 2018

@author: guanguan & Liwei Wang
"""

from cleaning_main_function import main_func
import pymysql

def setup(hostname, username, password, schema,tableinsertname,tablesourcename,damping=0.6): #damping阻尼系数，0.5-1之间
    conn = pymysql.connect(
                host=hostname,
                port=3306,
                database=schema,
                user=username,
                password=password,
                charset='utf8')# 创建与mysql的连接
    conn.autocommit(True)
    cur = conn.cursor() # 获取操作游标，cursor为游标位置
    print('----------------------Successfully connected to Source Database{}!--------------------------------'.format(tablesourcename))
    stoppath =  "./dict/stopwords_cn.txt" 
    select_sql = 'select * from {}'.format(tablesourcename) #SQL语句
    cur.execute(select_sql) #执行该SQL语句
    data_number = cur.rowcount
    print('------------------------------There are {} news in source Databases{}.--------------------------'.format(data_number,tablesourcename))

#########################

    main_func(cur,stoppath,data_number,damping,tableinsertname)

if __name__ == '__main__':
    #setup(hostname="10.2.17.208", username="root", password="mysql", schema="financial",
    #      tableinsertname='netfin_filtered_message',tablesourcename='netfin_source_message',
    #      damping= 0.8)

    setup(hostname="127.0.0.1", username="root", password="889", schema="test",
          tableinsertname='netfin_filtered_message',tablesourcename='netfin_source_message',
          damping= 0.8)

