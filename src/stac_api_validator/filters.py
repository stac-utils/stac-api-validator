"""Filter Extension Filters."""

from typing import Any
from typing import Dict


def cql2_text_ex_1(item_id: str, collection: str) -> str:
    return f"id='{item_id}' AND collection='{collection}'"


def cql2_json_ex_1(item_id: str, collection: str) -> Dict[str, Any]:
    return {
        "op": "and",
        "args": [
            {"op": "=", "args": [{"property": "id"}, item_id]},
            {"op": "=", "args": [{"property": "collection"}, collection]},
        ],
    }


def cql2_text_ex_2(item_id: str, collection: str) -> str:
    return (
        f"collection = '{collection}'"
        " AND eo:cloud_cover <= 10"
        " AND datetime >= TIMESTAMP('2021-04-08T04:39:23Z')"
        " AND S_INTERSECTS(geometry, POLYGON((43.5845 -79.5442, 43.6079 -79.4893, 43.5677 -79.4632, 43.6129 -79.3925, 43.6223 -79.3238, 43.6576 -79.3163, 43.7945 -79.1178, 43.8144 -79.1542, 43.8555 -79.1714, 43.7509 -79.6390, 43.5845 -79.5442)))"
    )


def cql2_json_ex_2(item_id: str, collection: str) -> Dict[str, Any]:
    return {
        "filter-lang": "cql2-json",
        "filter": {
            "op": "and",
            "args": [
                {"op": "=", "args": [{"property": "collection"}, collection]},
                {"op": "<=", "args": [{"property": "eo:cloud_cover"}, 10]},
                {
                    "op": ">=",
                    "args": [
                        {"property": "datetime"},
                        {"timestamp": "2021-04-08T04:39:23Z"},
                    ],
                },
                {
                    "op": "s_intersects",
                    "args": [
                        {"property": "geometry"},
                        {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [43.5845, -79.5442],
                                    [43.6079, -79.4893],
                                    [43.5677, -79.4632],
                                    [43.6129, -79.3925],
                                    [43.6223, -79.3238],
                                    [43.6576, -79.3163],
                                    [43.7945, -79.1178],
                                    [43.8144, -79.1542],
                                    [43.8555, -79.1714],
                                    [43.7509, -79.6390],
                                    [43.5845, -79.5442],
                                ]
                            ],
                        },
                    ],
                },
            ],
        },
    }


# {
#     "filter-lang": "cql2-json",
#     "filter": {
#         "op": "and",
#         "args": [
#             {"op": "=", "args": [{"property": "collection"}, "sentinel-2-l2a"]},
#             {
#                 "op": "s_intersects",
#                 "args": [
#                     {"property": "geometry"},
#                     {
#                         "type": "Polygon",
#                         "coordinates": [
#                             [
#                                 [-79.71679687499928, -19.89072302399748],
#                                 [139.83398437500085, -19.89072302399748],
#                                 [139.83398437500085, 63.665760337788015],
#                                 [-79.71679687499928, 63.665760337788015],
#                                 [-79.71679687499928, -19.89072302399748],
#                             ]
#                         ],
#                     },
#                 ],
#             },
#             {
#                 "op": "anyinteracts",
#                 "args": [
#                     {"property": "datetime"},
#                     {"interval": ["2015-06-27T00:00:00Z", "2022-09-29T23:59:59Z"]},
#                 ],
#             },
#             {"op": "<=", "args": [{"property": "eo:cloud_cover"}, 50]},
#         ],
#     },
#     "limit": 50,
# }
