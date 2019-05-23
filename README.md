

# ik-elasticsearch

需要了解Docker, 基础linux命令

## 概述

全文搜索引擎，可以快速地储存、搜索和分析海量数据.

Lucene是一个高性能和全功能搜索引擎功能的库

es相当于 Lucene 的一层封装，它提供了一套简单一致的 RESTful API 

特点:

- 一个分布式的实时文档存储，每个字段可以被索引与搜索
- 一个分布式实时分析搜索引擎
- 能胜任上百个服务节点的扩展，并支持 PB 级别的结构化或者非结构化数据

维基百科、Stack Overflow、GitHub 都纷纷采用它来做搜索

## Elasticsearch 基本概念

### Node 和 Cluster

Elasticsearch 本质上是一个分布式数据库，允许多台服务器协同工作，每台服务器可以运行多个 Elasticsearch 实例。

单个 Elasticsearch 实例称为一个节点（Node）。一组节点构成一个集群（Cluster）。

### Index

Elasticsearch 会索引所有字段，经过处理后写入一个反向索引（Inverted Index）。查找数据的时候，直接查找该索引。

所以，Elasticsearch 数据管理的顶层单位就叫做 Index（索引),每个 Index 的名字必须是小写。

### Document

Index 里面单条的记录称为 Document（文档）。许多条 Document 构成了一个 Index。

Document 使用 JSON 格式表示

同一个 Index 里面的 Document，不要求有相同的结构（scheme），但是最好保持相同，这样有利于提高搜索效率。

### Type

Document 可以分组，比如 weather 这个 Index 里面，可以按城市分组（北京和上海），也可以按气候分组（晴天和雨天）。这种分组就叫做 Type，它是虚拟的逻辑分组，用来过滤 Document，

不同的 Type 应该有相似的结构（Schema），举例来说，id 字段不能在这个组是字符串，在另一个组是数值。性质完全不同的数据（比如 products 和 logs）应该存成两个 Index，而不是一个 Index 里面的两个 Type（虽然可以做到）。

根据规划，Elastic 6.x 版只允许每个 Index 包含一个 Type，7.x 版将会彻底移除 Type。

### Fields

即字段，每个 Document 都类似一个 JSON 结构，它包含了许多字段，每个字段都有其对应的值，多个字段组成了一个 Document.

![](./img/compare.png)



## install docker

```bash
# for centos install
sudo yum update

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

sudo systemctl start docker

sudo docker -v
# Docker version 18.06.1-ce, build e68fc7a ==> 代表 success 
```

## install elasticsearch

```bash
1. 
mkdir es && cd es
touch Dockerfile
# 在Dockerfile 中写下面的一句话, 不要#
# FROM docker.elastic.co/elasticsearch/elasticsearch:7.1.0@sha256:802b6a299260dbaf21a9c57e3a634491ff788a1ea13a51598d4cd105739509c4

2. 
# 编译es镜像
docker build -t es:0.1 .
# 查看镜像
docker images -a
```

## run es image

```bash
docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" es:0.1

# 新窗口test: 
curl http://127.0.0.1:9200/_cat/health
curl http://localhost:9200/
# 默认情况下，Elastic 只允许本机访问，如果需要远程访问，可以修改 Elastic 安装目录的config/elasticsearch.yml文件，去掉network.host的注释，将它的值改成0.0.0.0，然后重新启动 Elastic。
```



## add plugins to es

```bash
# 1.查看容器，得到CONTAINER ID
docker ps
docker container ls -a

# 2. 进入container
docker exec -it b77e94f5200d bash
cd plugins && mkdir ik

# 3. 下载ik zip包
wget https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v7.1.0/elasticsearch-analysis-ik-7.1.0.zip

# 4. 解压到ik目录下
unzip elasticsearch-analysis-ik-7.1.0.zip -d ik/

# 5. 退出容器, 快捷键
# ctrl + p + q 

# 6. ctrl + c 重启容器
docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" es:0.1 
```

## test ik-es

参考 https://github.com/medcl/elasticsearch-analysis-ik 的Quick Example 测试命令理解ik， 如需配置IKAnalyzer.cfg.xml也可以参考 



1. curl 是一个发起网络请求的命令, -X是指发起请求的方式,  -H 后面是请求体的format, -d 是我们传递给es的数据

2. Elasticsearch 默认运行在9200端口
3. Elasticsearch提供网络接口，可以通过HTTP请求创建index(相当于数据库)，插入数据; 内部做存储和分析插入的数据; 再通过HTTP请求进行search数据

```bash
# 举例 1.create a index （create一个名为"index"的index, index唯一，再次创建会报错)
# curl -XPUT http://id addr:port/index_name
curl -XPUT http://localhost:9200/index

# 2.create a mapping (声明映射格式，这里只是一个简单的text)
# 参数说明: ik_max_word: 会将文本做最细粒度的拆分，比如会将“中华人民共和国国歌”拆分为“中华人民共和国,中华人民,中华,华人,人民共和国,人民,人,民,共和国,共和,和,国国,国歌”，会穷尽各种可能的组合，适合 Term Query；
# ik_smart: 会做最粗粒度的拆分，比如会将“中华人民共和国国歌”拆分为“中华人民共和国,国歌”，适合 Phrase 查询。
curl -XPOST http://localhost:9200/index/_mapping -H 'Content-Type:application/json' -d'
{
        "properties": {
            "content": {
                "type": "text",
                "analyzer": "ik_max_word",
                "search_analyzer": "ik_smart"
            }
        }

}'

# 3.index some docs (给index库添加Document, 里面只有一个"content" Field)
# curl -XPOST http://localhost:9200/index_name/operate_method/id      (id是这个Document的唯一标识符)
# 如果自定义字典参数，需要格式为UTF8编码
curl -XPOST http://localhost:9200/index/_create/1 -H 'Content-Type:application/json' -d'
{"content":"美国留给伊拉克的是个烂摊子吗"}
'
curl -XPOST http://localhost:9200/index/_create/2 -H 'Content-Type:application/json' -d'
{"content":"公安部：各地校车将享最高路权"}
'
curl -XPOST http://localhost:9200/index/_create/3 -H 'Content-Type:application/json' -d'
{"content":"中韩渔警冲突调查：韩警平均每天扣1艘中国渔船"}
'
curl -XPOST http://localhost:9200/index/_create/4 -H 'Content-Type:application/json' -d'
{"content":"中国驻洛杉矶领事馆遭亚裔男子枪击 嫌犯已自首"}
'

# 4.query with highlighting (根据关键词检索)
curl -XPOST http://localhost:9200/index/_search  -H 'Content-Type:application/json' -d'
{
    "query" : { "match" : { "content" : "中国" }},
    "highlight" : {
        "pre_tags" : ["<tag1>", "<tag2>"],
        "post_tags" : ["</tag1>", "</tag2>"],
        "fields" : {
            "content" : {}
        }
    }
}
'

# return Result
{
    "took": 14,
    "timed_out": false,
    "_shards": {
        "total": 5,
        "successful": 5,
        "failed": 0
    },
    "hits": {
        "total": 2,
        "max_score": 2,
        "hits": [
            {
                "_index": "index",
                "_type": "fulltext",
                "_id": "4",
                "_score": 2,
                "_source": {
                    "content": "中国驻洛杉矶领事馆遭亚裔男子枪击 嫌犯已自首"
                },
                "highlight": {
                    "content": [
                        "<tag1>中国</tag1>驻洛杉矶领事馆遭亚裔男子枪击 嫌犯已自首 "
                    ]
                }
            },
            {
                "_index": "index",
                "_type": "fulltext",
                "_id": "3",
                "_score": 2,
                "_source": {
                    "content": "中韩渔警冲突调查：韩警平均每天扣1艘中国渔船"
                },
                "highlight": {
                    "content": [
                        "均每天扣1艘<tag1>中国</tag1>渔船 "
                    ]
                }
            }
        ]
    }
}
```



# python use
pip elasticsearch==6.3.1

- python的elasticsearch模块对上面的请求方式做了一次封装，不需要使用post发送HTTP请求，直接提供了方法操作elastic
```python
from elasticsearch import Elasticsearch
es = Elasticsearch({"host": "localhost", "port": 9200})
```

- 更上面结构类似es有create, update, search, delete等几个方法
 - 参数: index=str()   必须小写, doc_type=str(), body=dict(), refresh=Bool(), id=int()

 ```python
 result = es.indices.create(index='news', ignore=400)
 print(result)

# {'acknowledged': True, 'shards_acknowledged': True, 'index': 'news'} # acknowledged表示成功
# 如果再执行返回失败 status=400, 因为index已经存在
 ```

- python简单使用 <https://cuiqingcai.com/6214.html>
- my project's one part, 

# 参考

<https://elasticsearch-py.readthedocs.io/en/master/>

中文文档 <https://es.xiaoleilu.com/index.html>

<http://www.ruanyifeng.com/blog/2017/08/elasticsearch.html>

<https://www.elasticsearch.cn/>

<https://github.com/elastic/elasticsearch-py>



query API文档 <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html>