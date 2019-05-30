# es管理

- Kinada -> Dev Tools -> 127.0.0.1:5601

- # 127.0.0.1:9200/?pretty

## 检查集群的健康状况

```bash
cat /_cat/health?v
```

- green: 每个index的primary shard和replica shard 都是active状态
- green: 每个index的primary shard都是active状态，但是部分replica shard 不是active状态,处于不可用状态
- red, 不是所有索引的primary shard都是active状态，部分索引有数据丢失

```bash
GET _cat/indices?v

PUT /test_index?pretty

DELETE /test_index?pretty

```

```bash
PUT /ecommerce/product/1 {"name": 'new', "des": 'product'} # 新增和更新，需要全部数据
POST /ecommerce/product/1/_update {"doc": {"name": "new"}} # 需要更新


_version: 设计乐观锁的并发控制策略
es会对每个document的每个field建立倒排索引

```

## search

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

