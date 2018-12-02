from bson import SON, ObjectId
from datetime import datetime

parents = {
    'item_title': 'Content Parents Aggregation',
    'datasource': {
        'source': 'content',
        'aggregation': {

            'pipeline': [
                {
                    "$match": {
                        "_id": "$start_id",
                        "parent": {
                            "$ne": None
                        }
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "title": 1,
                        "slug": 1,
                        "space_key": 1,
                        "parent": 1
                    }
                },
                {
                    "$graphLookup": {
                        "from": "content",
                        "startWith": "$parent",
                        "connectFromField": "parent",
                        "connectToField": "_id",
                        "maxDepth": 3,
                        "depthField": "levelAbove",
                        "as": "parents"
                    }
                },
                {
                    "$project": {
                        "parents._id": 1,
                        "parents.title": 1,
                        "parents.slug": 1,
                        "parents.space_key": 1,
                        "parents.levelAbove": 1
                    }
                },
                {
                    "$sort": SON([("parents.levelAbove", -1)])
                },
            ]

        }
    }
}

children = {
    'item_title': 'Content Parents Aggregation',
    'datasource': {
        'source': 'content',
        'aggregation': {

            'pipeline':

                [
                    {
                        "$match": {
                            "_id": "$start_id",
                        }
                    },
                    {
                        "$project": {
                            "_id": 1,
                            "title": 1,
                            "slug": 1,
                            "space_key": 1
                        }
                    },
                    {
                        "$graphLookup": {
                            "from": "content",
                            "startWith": "$_id",
                            "connectFromField": "_id",
                            "connectToField": "parent",
                            "maxDepth": "$max_depth",
                            "depthField": "levelBelove",
                            "as": "children"
                        }
                    },
                    {
                        "$project": {
                            "children._id": 1,
                            "children.title": 1,
                            "children.slug": 1,
                            "children.space_key": 1,
                            "children.levelBelove": 1
                        }
                    },
                    {
                        "$sort": {
                            "children.leveBelove": 1
                        }
                    }
                ]
        }
    }
}

siblings = {
    'item_title': 'Content Parents Aggregation',
    'datasource': {
        'source': 'content',
        'aggregation': {

            'pipeline':

                [
                    {
                        "$match": {
                            "_id": "$parent_id",
                        }
                    },
                    {
                        "$project": {
                            "_id": 1,
                            "title": 1,
                            "slug": 1,
                            "space_key": 1
                        }
                    },
                    {
                        "$graphLookup": {
                            "from": "content",
                            "startWith": "$_id",
                            "connectFromField": "_id",
                            "connectToField": "parent",
                            "maxDepth": 0,
                            "depthField": "levelBelove",
                            "restrictSearchWithMatch": {"_id": {"$ne": "$current_id"}},
                            "as": "siblings"
                        }
                    },
                    {
                        "$project": {
                            "siblings._id": 1,
                            "siblings.title": 1,
                            "siblings.slug": 1,
                            "siblings.space_key": 1,
                            "siblings.levelBelove": 1
                        }
                    },
                    {
                        "$sort": {
                            "siblings.leveBelove": 1
                        }
                    }
                ]
        }
    }
}
