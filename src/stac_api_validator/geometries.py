point = {"type": "Point", "coordinates": [100.0, 0.0]}

linestring = {"type": "LineString", "coordinates": [[100.0, 0.0], [101.0, 1.0]]}

polygon = {
    "type": "Polygon",
    "coordinates": [
        [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]
    ],
}

polygon_with_hole = {
    "type": "Polygon",
    "coordinates": [
        [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]],
        [[100.8, 0.8], [100.8, 0.2], [100.2, 0.2], [100.2, 0.8], [100.8, 0.8]],
    ],
}

multipoint = {"type": "MultiPoint", "coordinates": [[100.0, 0.0], [101.0, 1.0]]}

multilinestring = {
    "type": "MultiLineString",
    "coordinates": [[[100.0, 0.0], [101.0, 1.0]], [[102.0, 2.0], [103.0, 3.0]]],
}

multipolygon = {
    "type": "MultiPolygon",
    "coordinates": [
        [[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]],
        [
            [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]],
            [[100.2, 0.2], [100.2, 0.8], [100.8, 0.8], [100.8, 0.2], [100.2, 0.2]],
        ],
    ],
}

geometry_collection = {
    "type": "GeometryCollection",
    "geometries": [
        {"type": "Point", "coordinates": [100.0, 0.0]},
        {"type": "LineString", "coordinates": [[101.0, 0.0], [102.0, 1.0]]},
    ],
}
