# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 09:13:20 2018

@author: Administrator
"""
import re
import warnings
import jieba
import jieba.analyse
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from collections import defaultdict
from sklearn import decomposition
from sklearn.cluster import AffinityPropagation
import numpy as np
import copy
jieba.load_userdict("./dict/user_dict.txt")
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')


# 文档预处理
def preprocess(doc,stoppath):
    doc = str(doc)
    doc = re.findall(u'[\u4e00-\u9fa5].+?', doc)
    re_h = re.compile(r'</?\w+[^>]*>')
    doc = str(doc)
    doc = re_h.sub('',doc) #去除html字符
    doc = re.sub('\s','',doc)
    data = jieba.cut(doc) #jieba分词
    stopwords =[line.strip() for line in open(stoppath,mode='r',encoding='UTF-8').readlines()]#加载停用词
    output = ''
    for word in data: #去除停用词
       if word not in stopwords:
           if word !='\t':
               output +=word
               output +=" "
    return output

# tfidf权值计算
def tfidf_value(data_num,cont,stoppath):
    corpus = []
    for i in cont:
        content = preprocess(i,stoppath)
        corpus.append(content)#获取语料
    vectorizer = CountVectorizer()#将文本中的词语转换为词频矩阵
    transformer = TfidfTransformer()#统计每个词语的tfidf权值
    tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))#第一个fit_transform计算tfidf，第二个是将文本转换为词频矩阵
    return(tfidf)

# PCA
#def test_pca(weight,components_num):
#    kpca = decomposition.KernelPCA(components_num,degree=3,kernel='rbf',gamma=4)
#    principle_weight = kpca.fit_transform(weight)
#    return(principle_weight)

#AffinityPropagation 亲和力传播算法
def AP(weight,damp):
    simi = []
    for m in weight: ##每个数字与所有数字的相似度列表，即矩阵中的一行
        temp = []
        for n in weight:
            s =-np.sqrt((m[0]-n[0])**2 + (m[1]-n[1])**2) ##采用负的欧式距离计算相似度
            temp.append(s)
        simi.append(temp)
    p = np.min(simi) #p值为参考度
    #p = np.median(simi) #将所有相似度高的文章分为一类，其余一篇为一类
    ap = AffinityPropagation(damping=damp,max_iter=800,convergence_iter=30,
                             preference=p).fit(weight)  #damping为阻尼系数，取值为【0.5-1.0】
    y = ap.labels_
    return(y)

# 获取聚类后的各个类
def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items() 
                            if len(locs)>=1)

def similarity(tfidf,cluster_result,text_content,dictionary):
    dict2 = copy.deepcopy(dictionary)
    text_class = []
    SimMatrix = (tfidf * tfidf.T).A
    for dup in sorted(list_duplicates(cluster_result)):
        #print(dup)
        text_class = dup[1]
        for i in range(len(text_class)): #一一计算相似度（类似冒泡法）#########第i类，作为一个列表
            sims = []
            num = 0
            for j in range(i+1,len(text_class)):
                sim = SimMatrix[text_class[i],text_class[j]]
                key_list = []
                value_list = []

                if sim > 0.8: #删除相似度高于阈值的文本
                    print('the '+str(text_class[j]+1)+' th text is similar with the '+str(text_class[i]+1)+
                          ' th text, so it should be deleted!')
                    for key,val in dict2.items():
                        key_list.append(key)
                        value_list.append(val)


                    get_value_index=value_list.index(text_content[text_class[j]])
                    url_del = key_list[get_value_index] #获取重复文本的url
                    if url_del in dictionary:
                        dictionary.pop(url_del)
                    num += 1 #每个文本的重复个数，是否可作为热度？


                sims.append(sim)
            #print('The number of repetitions of the '+str(text_class[i]+1)+' th text is ' + str(num) + '.')
    return(dictionary)


