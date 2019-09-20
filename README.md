

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

单个 Elasticsearch 实例称为一个节点（Node）。一组节点构成一个集群（Cluster, 由名称唯一标识）。

### Index

Document的集合

Elasticsearch 会索引所有字段，经过处理后写入一个反向索引（Inverted Index）。查找数据的时候，直接查找该索引。

所以，Elasticsearch 数据管理的顶层单位就叫做 Index（索引),每个 Index 的名字必须是小写。

### Document

能被索引的基础单元

Index 里面单条的记录称为 Document（文档）。许多条 Document 构成了一个 Index。

Document 使用 JSON 格式表示

同一个 Index 里面的 Document，不要求有相同的结构（scheme），但是最好保持相同，这样有利于提高搜索效率。

### Type

Document 可以分组，比如 weather 这个 Index 里面，可以按城市分组（北京和上海），也可以按气候分组（晴天和雨天）。这种分组就叫做 Type，它是虚拟的逻辑分组，用来过滤 Document，

不同的 Type 应该有相似的结构（Schema），举例来说，id 字段不能在这个组是字符串，在另一个组是数值。性质完全不同的数据（比如 products 和 logs）应该存成两个 Index，而不是一个 Index 里面的两个 Type（虽然可以做到）。

根据规划，Elastic 6.x 版只允许每个 Index 包含一个 Type，7.x 版将会彻底移除 Type。

### Fields

即字段，每个 Document 都类似一个 JSON 结构，它包含了许多字段，每个字段都有其对应的值，多个字段组成了一个 Document.

## shard

索引的物理分区，是一个最小的 Lucene 索引单元。分为 primary shard(主分片) 和 replica shard(简称replicas)。

- 可以水平切分和扩展内容容量
- 在shards 间分发和并行执行操作，从而提供性能和吞吐量

## replicas

副本/备份(replicas)：主分片的备份

- 当 shard 失效时提供高可用性。因为这个原因，一个primary shard的replica不会分配到和该shard所处的同一节点
- 扩展查询的容量/吞吐量，因为查询操作是一个读操作，可以在所有replica上并行执行

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

# if is root, ignore the following
# the Docker daemon binds to a Unix socket instead of a TCP port. By default that Unix socket is owned by the user root and other users can only access it using sudo, the Docker daemon always runs as the root user.
sudo groupadd docker # create the docker group
sudo usermod -aG docker $USER # add your user to the docker group
# login out && login in
```

## install elasticsearch

```bash
1. 
mkdir es && cd es
touch Dockerfile
# 在Dockerfile 中写下面的一句话, 不要#
# FROM docker.elastic.co/elasticsearch/elasticsearch:7.1.0@sha256:802b6a299260dbaf21a9c57e3a634491ff788a1ea13a51598d4cd105739509c4
# 自动添加elasticsearch-ik
# RUN ./bin/elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v7.1.0/elasticsearch-analysis-ik-7.1.0.zip
# 或者
# RUN wget -c --tries=0 -O /tmp/elasticsearch-analysis-ik.zip https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v7.1.0/elasticsearch-analysis-ik-7.1.0.zip && mkdir /usr/share/elasticsearch/plugins/ik && unzip /tmp/elasticsearch-analysis-ik.zip -d /usr/share/elasticsearch/plugins/ik && rm -rf /tmp/elasticsearch-analysis-ik.zip

2. 
# 编译es镜像
docker build -t es:0.1 .
# 查看镜像
docker images -a
```

## run es image

```bash
# -p 映射本地的9200和9300端口到docker container的9200和9300端口
# -e Set environment variables,
# discovery.type=single-node  Elasticsearch以单节点的形式运行
docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" es:0.1

# 设置jvm.options设置JVM堆通道的大小, 默认2G,所设置的值取决于你的服务器的可用内存大小.
# docker run -d --name elasticsearch-ik -p 9200:9200 -p 9300:9300 -e "ES_JAVA_OPTS=-Xms256m -Xmx256m" -e "discovery.type=single-node" es:0.1

# 打开新窗口test: 
curl http://127.0.0.1:9200/_cat/health
curl http://localhost:9200/
# 默认情况下，Elastic 只允许本机访问，如果需要远程访问，可以修改 Elastic 安装目录的config/elasticsearch.yml文件，去掉network.host的注释，将它的值改成0.0.0.0，然后重新启动 Elastic。
```

> > - 最小堆的大小和最大堆的大小应该相等。
> >
> > - Elasticsearch可获得越多的堆，并且内存也可以使用更多的缓存。但是需要注意，分配了太多的堆给你的项目，将会导致有长时间的垃圾搜集停留。
> >
> > - 设置最大堆的值不能超过你物理内存的50%，要确保有足够多的物理内存来保证内核文件缓存。
> >
> > - 不要将最大堆设置高于JVM用于压缩对象指针的截止值。确切的截止值是有变化，但接近32gb。您可以通过在日志中查找以下内容来验证您是否处于限制以下:
> >
> >   heap size [1.9gb], compressed ordinary object pointers [true]
> >
> > - 最好尝试保持在基于零压缩oops的阈值以下;当确切的截止值在大多数时候处于26GB是安全的。但是在大多数系统中也可以等于30GB。在启动Elasticsearch之后，你也可以在JVM参数中验证这个限制`-XX:+UnlockDiagnosticVMOptions -XX:+PrintCompressedOopsMode`和查询类似于下面这一行：
> >
> >   ```html
> >   
> >   ```

## 手动 add ik plugins to es

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
docker restart es:0.1
```

## test ik-es

参考 https://github.com/medcl/elasticsearch-analysis-ik 的Quick Example 测试命令理解ik， 如需配置IKAnalyzer.cfg.xml也可以参考 



1. curl 是一个发起网络请求的命令, -X是指发起请求的方式,  -H 后面是请求体的format, -d 是我们传递给es的数据
2. Elasticsearch 默认运行在9200端口
3. Elasticsearch提供RESTful网络接口，可以通过HTTP请求创建index，在index中插入数据; 内部做存储和分析插入的数据; 再通过HTTP请求进行search数据

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

# 3.index some docs (给index库添加Document, 里面只有一个Field "content" )
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

# 4.query with highlighting (根据关键词检索， 匹配"content"字段包含“中国”的Document)
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

- python的elasticsearch模块对上面的请求方式做了一次封装，不需要使用post发送HTTP请求，es实例直接提供了方法操作elastic
```python
from elasticsearch import Elasticsearch
es = Elasticsearch({"host": "localhost", "port": 9200})
```

- es实例有create, delete, update, search 等几个方法,分别是增删改查
 - 参数: index=str()   必须小写, doc_type=str(), body=dict(), refresh=Bool(), id=int()

 ```python
 result = es.indices.create(index='news', ignore=400)
 print(result)

# {'acknowledged': True, 'shards_acknowledged': True, 'index': 'news'} # acknowledged表示成功
# 如果再执行返回失败 status=400, 因为index已经存在
 ```

# Es 迁移

- elasticsearch-dump
- snapshot
- reindex
- logstash

## elasticsearch-dump

### 适用场景

适合数据量不大，迁移索引个数不多的场景  

[github]: https://github.com/taskrabbit/elasticsearch-dump

1. install

```
docker pull taskrabbit/elasticsearch-dump
```

​	2 . 主要参数说明

```js
	    --input: 源地址，可为ES集群URL、文件或stdin,可指定索引，格式为：{protocol}://{host}:{port}/{index}
	    --input-index: 源ES集群中的索引
	    --output: 目标地址，可为ES集群地址URL、文件或stdout，可指定索引，格式为：{protocol}://{host}:{port}/{index}
	    --output-index: 目标ES集群的索引
	    --type: 迁移类型，默认为data,表明只迁移数据，可选settings, analyzer, data, mapping, alias
	    --limit：每次向目标ES集群写入数据的条数，不可设置的过大，以免bulk队列写满
```

3. 迁移

```bash
# Copy an index from production to staging with mappings:
docker run --rm -ti taskrabbit/elasticsearch-dump \
  --input=http://production.es.com:9200/my_index \
  --output=http://staging.es.com:9200/my_index \
  --type=mapping
docker run --rm -ti taskrabbit/elasticsearch-dump \
  --input=http://production.es.com:9200/my_index \
  --output=http://staging.es.com:9200/my_index \
  --type=data
# 注意第一条命令先将索引的settings先迁移，如果直接迁移mapping或者data将失去原有集群中索引的配置信息如分片数量和副本数量等，当然也可以直接在目标集群中将索引创建完毕后再同步mapping与data

# Backup index data to a file:
docker run --rm -ti -v /data:/tmp taskrabbit/elasticsearch-dump \
  --input=http://production.es.com:9200/my_index \
  --output=/tmp/my_index_mapping.json \
  --type=data
```



# 参考

<https://github.com/taskrabbit/elasticsearch-dump/> 

<https://www.elasticsearch.cn/>

<https://github.com/elastic/elasticsearch-py>

<https://cloud.tencent.com/developer/article/1145944/>

query API文档 <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html>