from django.conf import settings
from elasticsearch import Elasticsearch

es = Elasticsearch(
    [{"host": settings.ES_HOST, "port": settings.ES_PORT, "scheme": "http"}]
)


def index_advertisement(advertisements):
    index_name = "advertisements"
    es.indices.create(
        index=index_name,
        body={
            "settings": {
                "analysis": {
                    "analyzer": {
                        "autocomplete": {
                            "tokenizer": "autocomplete",
                            "filter": ["lowercase"],
                        }
                    },
                    "tokenizer": {
                        "autocomplete": {
                            "type": "edge_ngram",
                            "min_gram": 1,
                            "max_gram": 20,
                            "token_chars": ["letter", "digit"],
                        }
                    },
                }
            },
            "mappings": {
                "properties": {
                    "name": {"type": "text", "analyzer": "autocomplete"},
                    "description": {"type": "text", "analyzer": "autocomplete"},
                }
            },
        },
        ignore=400,
    )

    for advertisement in advertisements:
        document = {
            "id": advertisement.id,
            "name": advertisement.name,
            "description": advertisement.description,
        }
        es.index(index=index_name, document=document)


def search_description(name_query, description_query):
    result = es.search(
        index="advertisements",
        body={
            "query": {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "name": {
                                    "query": name_query,
                                    "fuzziness": "auto",
                                }
                            }
                        },
                        {
                            "match": {
                                "description": {
                                    "query": description_query,
                                    "fuzziness": "auto",
                                }
                            }
                        },
                        {
                            "match_phrase": {
                                "name": {"query": name_query, "slop": 6}
                            }
                        },
                        {
                            "match_phrase": {
                                "description": {
                                    "query": description_query,
                                    "slop": 6,
                                }
                            }
                        },
                    ]
                }
            },
        },
    )

    if "hits" in result and "hits" in result["hits"]:
        return result["hits"]["hits"]

    else:
        return []
