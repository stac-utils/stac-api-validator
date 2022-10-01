"""Filter Extension Filters."""

from typing import Any
from typing import Dict
from typing import List


comparison_ops = ["=", "<>", "<", "<=", ">", ">="]


def cql2_text_string_comparisons(collection: str) -> List[str]:
    return [f"collection {op} '{collection}'" for op in comparison_ops]


cql2_text_numeric_comparisons = [f"eo:cloud_cover {op} 10" for op in comparison_ops]
cql2_text_timestamp_comparisons = [
    f"datetime {op} TIMESTAMP('2021-04-08T04:39:23Z')" for op in comparison_ops
]

cql2_text_s_intersects = "S_INTERSECTS(geometry, POLYGON((43.5845 -79.5442, 43.6079 -79.4893, 43.5677 -79.4632, 43.6129 -79.3925, 43.6223 -79.3238, 43.6576 -79.3163, 43.7945 -79.1178, 43.8144 -79.1542, 43.8555 -79.1714, 43.7509 -79.6390, 43.5845 -79.5442)))"


def cql2_json_string_comparisons(collection: str) -> List[Dict[str, Any]]:
    return [
        {"op": op, "args": [{"property": "collection"}, collection]}
        for op in comparison_ops
    ]


cql2_json_numeric_comparisons = [
    {"op": op, "args": [{"property": "eo:cloud_cover"}, 10]} for op in comparison_ops
]
cql2_json_timestamp_comparisons = [
    {
        "op": op,
        "args": [
            {"property": "datetime"},
            {"timestamp": "2021-04-08T04:39:23Z"},
        ],
    }
    for op in comparison_ops
]

cql2_json_s_intersects = {
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
}


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
    }


def cql2_text_ex_3(item_id: str, collection: str) -> str:
    return "eo:cloud_cover >= 5 AND eo:cloud_cover < 10"


def cql2_json_ex_3(item_id: str, collection: str) -> Dict[str, Any]:
    return {
        "op": "and",
        "args": [
            {"op": ">", "args": [{"property": "eo:cloud_cover"}, 5]},
            {"op": "<", "args": [{"property": "eo:cloud_cover"}, 10]},
        ],
    }


def cql2_text_ex_4(item_id: str, collection: str) -> str:
    return "eo:cloud_cover > 50 OR eo:cloud_cover < 10"


def cql2_json_ex_4(item_id: str, collection: str) -> Dict[str, Any]:
    return {
        "op": "or",
        "args": [
            {"op": ">", "args": [{"property": "eo:cloud_cover"}, 50]},
            {"op": "<", "args": [{"property": "eo:cloud_cover"}, 10]},
        ],
    }


# ex5 is property - property comparisons, of which there are no implementations


def cql2_text_ex_6(item_id: str, collection: str) -> str:
    return "T_INTERSECTS(datetime, INTERVAL('2020-11-11T00:00:00Z', '2020-11-12T00:00:00Z'))"


def cql2_json_ex_6(item_id: str, collection: str) -> Dict[str, Any]:
    return {
        "op": "t_intersects",
        "args": [
            {"property": "datetime"},
            {"interval": ["2020-11-11T00:00:00Z", "2020-11-12T00:00:00Z"]},
        ],
    }


cql2_text_ex_8 = "S_INTERSECTS(geometry,POLYGON((-77.0824 38.7886,-77.0189 38.7886,-77.0189 38.8351,-77.0824 38.8351,-77.0824 38.7886))) OR S_INTERSECTS(geometry,POLYGON((-79.0935 38.7886,-79.0290 38.7886,-79.0290 38.8351,-79.0935 38.8351,-79.0935 38.7886)))"


cql2_json_ex_8 = {
    "op": "or",
    "args": [
        {
            "op": "s_intersects",
            "args": [
                {"property": "geometry"},
                {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-77.0824, 38.7886],
                            [-77.0189, 38.7886],
                            [-77.0189, 38.8351],
                            [-77.0824, 38.8351],
                            [-77.0824, 38.7886],
                        ]
                    ],
                },
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
                            [-79.0935, 38.7886],
                            [-79.0290, 38.7886],
                            [-79.0290, 38.8351],
                            [-79.0935, 38.8351],
                            [-79.0935, 38.7886],
                        ]
                    ],
                },
            ],
        },
    ],
}


def cql2_text_ex_9(item_id: str, collection: str) -> str:
    return "eo:cloud_cover > 50 OR eo:cloud_cover < 10 OR (eo:cloud_cover IS NULL AND eo:cloud_cover IS NULL)"


def cql2_json_ex_9(item_id: str, collection: str) -> Dict[str, Any]:
    return {
        "op": "or",
        "args": [
            {"op": ">", "args": [{"property": "eo:cloud_cover"}, 50]},
            {"op": "<", "args": [{"property": "eo:cloud_cover"}, 10]},
            {
                "op": "and",
                "args": [
                    {"op": "isNull", "args": [{"property": "eo:cloud_cover"}]},
                    {"op": "isNull", "args": [{"property": "eo:cloud_cover"}]},
                ],
            },
        ],
    }


def cql2_text_ex_10(item_id: str, collection: str) -> str:
    return "eo:cloud_cover BETWEEN 0 AND 50"


def cql2_json_ex_10(item_id: str, collection: str) -> Dict[str, Any]:
    return {"op": "between", "args": [{"property": "eo:cloud_cover"}, [0, 50]]}


def cql2_text_ex_11(item_id: str, collection: str) -> str:
    return "mission LIKE 'sentinel%'"


def cql2_json_ex_11(item_id: str, collection: str) -> Dict[str, Any]:
    return {"op": "like", "args": [{"property": "mission"}, "sentinel%"]}


# requires basic spatial and temporal
def cql2_json_common_1(item_id: str, collection: str) -> Dict[str, Any]:
    return {
        "op": "and",
        "args": [
            {"op": "=", "args": [{"property": "collection"}, "sentinel-2-l2a"]},
            {
                "op": "s_intersects",
                "args": [
                    {"property": "geometry"},
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-79.71679687499928, -19.89072302399748],
                                [139.83398437500085, -19.89072302399748],
                                [139.83398437500085, 63.665760337788015],
                                [-79.71679687499928, 63.665760337788015],
                                [-79.71679687499928, -19.89072302399748],
                            ]
                        ],
                    },
                ],
            },
            {
                "op": "t_intersects",
                "args": [
                    {"property": "datetime"},
                    {"interval": ["2015-06-27T00:00:00Z", "2022-09-29T23:59:59Z"]},
                ],
            },
            {"op": "<=", "args": [{"property": "eo:cloud_cover"}, 50]},
        ],
    }
