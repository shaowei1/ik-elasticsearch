# 这是我们项目中的部分使用, 可以做一下参考
import datetime

from elasticsearch import Elasticsearch

es = Elasticsearch({"host": "localhost", "port": 9200})  # 本地运行项目使用


def create(template_id, name, styles_id_list, apply_count, body):
    data = {
        'title': body.get('title'),
        'template_id': template_id,
        'businesses': name,
        'styles': list(map(lambda _style: _style['name'], styles_id_list)),
        'apply_count': apply_count,
        'preview_thumb_image': body.get('preview_thumb_image'),
        'preview_image': body.get('preview_image'),
        'width': body.get('width'),
        'device': body.get('device'),
        'status': 'created',
        'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    res = es.create(index='my_index', doc_type='template', body=data, refresh=True, id=template_id)
    return res


def search(q, sort, page, per_page):
    """
    # 使用标题进行查询,使用created_at或者apply_count排序, 排序结果分页
    :param q:
    :param sort:
    :param page:
    :param per_page:
    :return:
    """
    dsl = {
        "query": {
            "bool": {
                "must": [{
                    "match": {"title": q}
                }]
            }
        },
        "sort": [
            {
                "{}".format(sort): "{}".format("desc")  # desc代表降序, asc
            }

        ],
        "from": (page - 1) * per_page,
        "size": per_page
    }

    _templates = es.search(index='my_index', doc_type='template', body=dsl)
    # :arg body: The search definition using the Query DSL
    # old version Elasticsearch 2.0 https://www.elastic.co/guide/cn/elasticsearch/guide/current/query-dsl-intro.html
    # latest version Elasticsearch 7.1 , https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
    return _templates


def delete(template_id):
    res = es.delete(index='my_index', doc_type='template', id=template_id, refresh=True)
    return res


def update(apply_count, template_id):
    """

    :param apply_count: 使用数量
    :param template_id:
    :return:
    """
    data = {
        'apply_count': apply_count + 1
    }

    res = es.update(index='my_index', doc_type='template', body={"doc": data}, refresh=True, id=template_id)
    return res


def search_all(status, template_id):
    """

    :param status:  通过status可以管理template的状态
    :param template_id:
    :return:
    """
    data = {
        'status': status,
        'updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    es.update(index='my_index', doc_type='template', body={"doc": data}, refresh=True, id=template_id)
    res = es.search(index='my_index', doc_type='template')
    return res

