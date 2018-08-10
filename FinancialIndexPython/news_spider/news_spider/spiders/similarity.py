# -*- coding: utf-8 -*-

import jieba
import codecs
from gensim import corpora, models, similarities
import os


class TextSimilarity:
    text_list = []
    stopwords_path = ''

    def __init__(self, target_path, stopwords_path):
        self.text_list = self.get_target(target_path)
        self.stopwords_path = stopwords_path

    # 加载停用词
    def stopwordslist(self, path):
        stopwords = codecs.open(path, 'r', encoding='utf8').readlines()
        stopwords = [w.strip() for w in stopwords]
        return stopwords

    # 分词
    def tokenization(self, text, stopwords_path):
        seg_list = jieba.cut(text, cut_all=False)  # 精确模式
        stopwords = self.stopwordslist(stopwords_path)
        seg_words = []
        # 去停用词
        for word in seg_list:
            if word not in stopwords:
                seg_words.append(word)
        return seg_words

    # 读取目标文本
    def get_target(self, dirpath):
        text_list = []
        list = os.listdir(dirpath)  # 列出文件夹下的所有目录和文件
        for i in range(0, len(list)):
            path = os.path.join(dirpath, list[i])
            if os.path.isfile(path):
                with open(path, 'r') as f:
                    text_list.append(f.read())
        return text_list

    # 计算文本相似度
    def cal_similarities(self, test_news):
        list = []
        for text in self.text_list:
            list.append(self.tokenization(text, self.stopwords_path))
        test_news = self.tokenization(test_news, self.stopwords_path)
        dictionary = corpora.Dictionary(list)
        new_vec = dictionary.doc2bow(test_news)
        corpus = [dictionary.doc2bow(i) for i in list]
        tfidf = models.TfidfModel(corpus)
        # 特征数
        featureNUM = len(dictionary.token2id.keys())
        # 通过TfIdf对整个语料库进行转换并将其编入索引，以准备相似性查询
        index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=featureNUM)
        # 计算向量相似度
        sim = index[tfidf[new_vec]]
        return sim
