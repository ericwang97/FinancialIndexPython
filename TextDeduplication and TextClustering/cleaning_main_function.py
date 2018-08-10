# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 10:24:13 2018

@author: guanguan
"""

import cleaning_sub_function as text_simi
import pymysql
import time

def main_func(cur,stop_path,data_num,damping,tableinsertname):
    print('------------------------------开始获取字段----------------------------------')
    whole_content = list(cur.fetchall()) #获取数据表中所有字段
    temp_content = []
    urls = []
    for m in whole_content:
        urls.append(m[2])
    contents = []
    for n in whole_content:
        contents.append(n[7])
    dict_url = {}
    dict_url = dict(zip(urls,whole_content))
    ################################################################
    print('-------------------------------开始计算TFIDF权重-------------------------------')
    tfidf = text_simi.tfidf_value(data_num,contents,stop_path)#############第一步，求TFIDF
    weight=tfidf.toarray() #tfidf权重
    #components = 20
    #decomp_result = text_simi.test_pca(weight,components) #降维
    #print(decomp_result)
    print('------------------------------计算TFIDF完成------------------------------')
    print('-------------------------------开始计算聚类-------------------------------')
    result = text_simi.AP(weight,damping)            ######################第二步，求AP聚类
    #print(result) #聚类后结果
    source = result
    print('------------------------------计算聚类完成------------------------------')
    print('-------------------------------开始计算相似度-------------------------------')
    dict_ = text_simi.similarity(tfidf,source,whole_content,dict_url)######第三步，求相似度字典，容易出错的地方
    print('------------------------------计算相似度完成------------------------------')
    print('-------------------------------开始整理数据进入数据库-------------------------------')

    for value in dict_.values():
        temp_content.append(value)
    print('------------------------------There are {} news in Filtered Database------------------------------'.format(len(temp_content)))

    wipe_table = 'truncate {}'.format(tableinsertname) #清空数据库中放筛选数据的表
    print('------------------------------Filtered Database {} has already been truncated------------------------------'.format(tableinsertname))
    cur.execute(wipe_table)
    
    for content in temp_content:
        source_messageInsert = '''insert into {}(title,url,net_name,ent_time,keyword,digest,content,hot_degree,scan_id)
                            values('{title}','{url}','{net_name}','{ent_time}','{keyword}','{digest}','{content}','{hot_degree}','{scan_id}')'''
                            
        sqltext = source_messageInsert.format(tableinsertname,title=pymysql.escape_string(content[1]),
                                                   url=pymysql.escape_string(content[2]),
                                                   net_name=pymysql.escape_string(content[3]),
                                                   #ent_time=pymysql.escape_string(time.strftime("%Y-%m-%d %H:%M:%S",content[4].timetuple())),
                                                   ent_time=pymysql.escape_string(str(content[4])),
                                                   keyword=pymysql.escape_string(content[5]),
                                                   digest=pymysql.escape_string(content[6]),
                                                   content=pymysql.escape_string(content[7]),
                                                   hot_degree=pymysql.escape_string(str(content[8])),
                                                   scan_id=pymysql.escape_string(str(content[9])),
                                                   )
        cur.execute(sqltext)

    print('------------------------------Inserting Data into {} is finished------------------------------'.format(tableinsertname))
        
if __name__ == '__main__':
    main_func(cur,stop_path,data_num,damping,tableinsertname)


