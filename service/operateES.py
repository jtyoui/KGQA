# !/usr/bin/python3.8
# -*- coding: utf-8 -*-
# @Time  : 2021/1/14 上午9:50
# @Author: 张伟
# @EMAIL: Jtyoui@qq.com
# @Notes : ES的一些简单操作
from elasticsearch import Elasticsearch, helpers

from config import QUE_TXT, HOST_LIST

es = Elasticsearch(HOST_LIST)


def delete_index(index, force=False):
    """删除索引
    :param index: 索引
    :param force: 是否强制删除索引，如果索引存在true强制删除，false不删除
    """
    if force and es.indices.exists(index):
        es.indices.delete(index=index)


def create_index(index, doc):
    """创建索引"""
    settings = {
        'mappings': {
            doc: {
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'word': {
                        'type': 'text',
                        'analyzer': 'ik_smart',
                        'search_analyzer': 'ik_smart'
                    }
                }
            }
        }
    }
    es.indices.create(index=index, ignore=400, body=settings)


def batch_data(index, doc, count=5000):
    """批量写入数据
    :param index: 索引
    :param doc: 文档
    :param count: 批量插入的条数
    """
    action = []
    flag = 0
    with open(QUE_TXT, encoding='utf-8')as fp:
        for i, line in enumerate(fp):
            line = line.strip()
            if line:
                data = {
                    'id': i,
                    'word': line
                }
                every_body = {
                    '_index': index,
                    '_type': doc,
                    '_source': data
                }
            if flag < count:
                action.append(every_body)
                flag += 1
            else:
                helpers.bulk(es, action)
                action = [every_body]
                flag = 1
    if flag > 0:  # 最后
        helpers.bulk(es, action)


def find_key(index, doc, word):
    """查找信息
    :param index: 索引
    :param doc: 文档
    :param word: 关键词
    :return: 文本数据
    """
    search = {
        "query": {
            "match": {
                'word': word
            }
        }
    }
    result = es.search(body=search, index=index, size=5, doc_type=doc)
    return [item['_source']['word'] for item in result['hits']['hits']]


if __name__ == '__main__':
    que_index = 'que_index'
    que_doc = 'que_doc'
    # delete_index(que_index, True)
    # create_index(que_index, que_doc)
    # batch_data(que_index, que_doc, 10000)
    r = find_key(que_index, que_doc, '玉米大斑病什么病原')
    print(r)