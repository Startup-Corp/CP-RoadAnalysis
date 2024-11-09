from flask import Flask, jsonify, render_template
import geopandas as gpd
import json
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString
from pyproj import Transformer
import pandas as pd

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template('./test.html')

@app.route("/data")
def get_data():
    shapefile_path = [
        'data/House_1очередь_ЖК.shp',
        'data/House_2очередь_ЖК.shp',
        'data/House_3очередь_ЖК.shp',
        # 'data/Дома_исходные.shp',
        # 'data/Выходы_метро',
        # 'data/Streets_1очередь.shp',
        # 'data/Streets_2очередь.shp',
        'data/Streets_3очередь.shp',
    ];

    polygons_gdfs = []
    lines_gdfs = []

    for path in shapefile_path:
        # Прочитайте .shp файл
        gdf = gpd.read_file(path)
        print(gdf[["geometry"]].head())

        # Преобразование координат в географические координаты (широта, долгота)
        transformer = Transformer.from_crs(gdf.crs, "EPSG:4326", always_xy=True)
        gdf['coordinates'] = gdf['geometry'].apply(extract_coordinates).apply(lambda coords: transform_coordinates(coords, transformer))
        print(gdf[["geometry", "coordinates"]].head())

        # Разделите данные на полигоны и линии
        polygons_gdf = gdf[gdf['geometry'].geom_type.isin(['Polygon', 'MultiPolygon'])]
        lines_gdf = gdf[gdf['geometry'].geom_type.isin(['LineString', 'MultiLineString'])]

        polygons_gdfs.append(polygons_gdf)
        lines_gdfs.append(lines_gdf)

        # Объедините данные в один GeoDataFrame
        # gdfs.append(gdf)

    # Объедините все GeoDataFrames в один
    # combined_gdf = pd.concat(gdfs, ignore_index=True)
    # geojson_data = json.loads(combined_gdf.to_json())

    combined_polygons_gdf = pd.concat(polygons_gdfs, ignore_index=True)
    combined_lines_gdf = pd.concat(lines_gdfs, ignore_index=True)

    geojson_data = {
        'polygons': json.loads(combined_polygons_gdf.to_json()),
        'lines': json.loads(combined_lines_gdf.to_json())
    }
    
    return jsonify({'data': geojson_data}), 201


# Функция для извлечения координат из полигонов и мультиполигонов
def extract_coordinates(geometry):
    if isinstance(geometry, Polygon):
        return list(geometry.exterior.coords)
    elif isinstance(geometry, MultiPolygon):
        return [list(polygon.exterior.coords) for polygon in geometry.geoms]
    elif isinstance(geometry, LineString):
        return list(geometry.coords)
    elif isinstance(geometry, MultiLineString):
        return [list(line.coords) for line in geometry.geoms]
    else:
        return None
    
def transform_coordinates(coords, transformer):
    if isinstance(coords, list) and isinstance(coords[0], tuple):
        return [[y, x] for x, y in [transformer.transform(x, y) for x, y in coords]]
    elif isinstance(coords, list) and isinstance(coords[0], list):
        return [transform_coordinates(polygon, transformer) for polygon in coords]
    else:
        return None