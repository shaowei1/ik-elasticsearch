# es管理

- Kibana -> Dev Tools -> 127.0.0.1:5601
- curl http://localhost:9200?pretty

- curl http://localhost:9200/_aliases

*GET, PUT测试使用Kibana, curl使用命令行*

## 检查集群的健康状况

curl -XGET 'localhost:9200/_cat/health?v&pretty'

GET /_cat/health?v

```bash
epoch      timestamp cluster        status node.total node.data shards pri relo init unassign pending_tasks max_task_wait_time active_shards_percent
1559222575 13:22:55  docker-cluster yellow          1         1     10  10    0    0       10             0                  -                 50.0%

```

- green: 每个index的primary shard和replica shard 都是active状态
- green: 每个index的primary shard都是active状态，但是部分replica shard 不是active状态,处于不可用状态
- red, 不是所有索引的primary shard都是active状态，部分索引有数据丢失

另外，从上面的响应中，我们可以看到共计 **1** 个 node（节点）和 **0** 个 shard（分片），因为我们还没有放入数据的。注意，因为我们使用的是默认的集群名称（**elasticsearch**），并且 **Elasticsearch**默认情况下使用 **unicast network**（单播网络）来发现同一机器上的其它节点。有可能您不小心在您的电脑上启动了多个节点，然后它们全部加入到了单个集群。在这种情况下，你会在上面的响应中看到不止 1 个 **node**（节点）。

## 集群的节点列表

curl -XGET 'localhost:9200/_cat/nodes?v&pretty'

```bash
ip         heap.percent ram.percent cpu load_1m load_5m load_15m node.role master name
172.17.0.2           46          90   0    0.00    0.01     0.05 mdi       *      RbYD59a
```

## 列出所有索引

curl -XGET 'localhost:9200/_cat/indices?v&pretty'

GET _cat/indices?v

```bash
health status index uuid                   pri rep docs.count docs.deleted store.size pri.store.size
yellow open   ecpro ZmNa0dcdQx-i9IL7fZuDIw   5   1          3            0     22.4kb         22.4kb
yellow open   index n8l4-ne-SWKj2HEwUKgEPg   5   1          2            0      7.2kb          7.2kb

```

- create a index

```bash
curl -XPUT 'localhost:9200/customer?pretty&pretty'
curl -XGET 'localhost:9200/_cat/indices?v&pretty'


PUT /test_index?pretty
DELETE /test_index?pretty

# pretty 到调用命令的末尾，来告诉它漂亮的打印成 JSON 响应
# 第一个命令的结果告诉我们现在已经有 1 个名为 customer 的索引，并且它有 5 个主分片和 1 个副本（默认）以及它包含了 0 文档在索引中。
```

您可以也注意到 **customer** 索引有一个 **yellow** 标记在索引中。回想下我们先前讨论的 **yellow** 意味着有些副本没有被分配。该索引发生这种情的原因是因为 **Elasticsearch** 默认为该索引创建了 1 个副本。因为目前我们只有一个节点在运行，这一个副本不能够被分配（为了高可用性, 数据和副本不能放在同一个节点上），直到稍候其它节点加入到集群。如果副本被分配到第二个节点，该索引的 **heath status**（健康状态）将会转换成 **green**。

## insert data

- PUT /index_name/document_type/id

```http
# 更新 if id is exist else 插入，需要全部数据
PUT /megacorp/employee/1
{
    "first_name" : "John",
    "last_name" :  "Smith",
    "age" :        25,
    "about" :      "I love to go rock climbing",
    "interests": [ "sports", "music" ]
}

# _version: 设计乐观锁的并发控制策略
# es会对每个document的每个field建立倒排索引
```

## update data

```http
# 只需要添加需要更新的数据
POST /megacorp/employee/1/_update 
{
	"doc": {"name": "new"}
} 
```

# search

- query string search
- query DSL
- query filter
- full-text search
- phrase search
- highlight search



```HTTP
GET /ecommerce/product/_search
```

- took: spend 几毫秒
- timed_out: is or not timeout
- _shards, 数据拆成了5个分片，对于搜索请求，会打到所有primary shard(或者是replica shard)
- hits.total: result have 3 document
- max_score: document对于一个search的相关度匹配分数
- hits.hits: 匹配搜索的详细数据

```http
GET /ecommerce/product/_search?q=name:yang&sort=price:desc
```

## query DSL

- Domain Specified Language

```HTTP
GET /ecommerce/product/_search
{
    "query": {"match_all": {}}
}

GET /ecommerce/product/_search
{
    "query": {"match_all": {
        "name": "yang"
    }
    },
    "sort": [
        {"price": "desc}
    ]
}


GET /ecommerce/product/_search
{
    "query": {"match_all": {}},
	"from": 1,
	"size": 1
}

GET /ecommerce/product/_search
{
    "query": {"match_all": {}},
	"_source": ["name", "price"]
}

```

## query filter

```http
get /ecommerce/product/_search
{
    "query": {
        "bool": {
            "must": {
                "name": "yang"
            }
        },
        "filter": {
            "range": {
                "price":{
                    "gt": 25
                }
            }
        }
    }
}
```

## full-text search

```http
GET /ecommerce/product/_search
{
	"query": {
        "match": {
            "producer": "yang yue"
        }
	}
}
```

## phrase search(短语搜索)

- 跟full-text search相反，full-text search回见输入的搜索串拆解开来，去倒排索引里面去一一匹配，只要能匹配上任意一个差节后的单词，就可作为结果返回
- phrase search 输入的搜索串,必须在指定的字段文本中，完全包含一抹一眼的，才能算匹配，才能作为结果返回

```
GET /ecommerce/product/_search
{
	"query": {
        "match_phrase": {
            "producer": "yang yue"
        }
	}
}
```

## highlight search

```
GET /ecommerce/product/_search
{
	"query": {
        "match_phrase": {
            "producer": "yang yue"
        }
	},
	"highlight" {
        "fields": {
            "producer": {}
        }
	}
}
```

# 聚合

### 计算每个tag下的商品数量

```http
GET /ecommerce/product/_search
{
    "aggs":{
        "group_by_tags":{ # name Optional
            "terms": {"field": "tags"}
        }
    }
}
# 将field的fielddata设为true
put /ecommerce/_mapping/product
{
    "properties": {
        "tags":{
            "type": "string",
            "fielddata": true
        }
    }
}
```

## reference

[文档](<https://es.xiaoleilu.com/010_Intro/30_Tutorial_Search.html>)