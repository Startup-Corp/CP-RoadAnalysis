from flask import Flask, jsonify, render_template
import geopandas as gpd
import json
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, Point
from pyproj import Transformer
import pandas as pd

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template('./test.html')

@app.route("/data")
def get_data():
    shapefile_path = [
        # 'data/Дома_исходные.shp',
        'data/House_1очередь_ЖК.shp',
        # 'data/House_2очередь_ЖК.shp',
        # 'data/House_3очередь_ЖК.shp',
        'data/Выходы_метро.shp',
        'data/Остановки_ОТ.shp',
        # 'data/Streets_1очередь.shp',
        # 'data/Streets_2очередь.shp',
        # 'data/Streets_3очередь.shp',
    ];

    polygons_gdfs = []
    lines_gdfs = []
    points_gdfs = []
    
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
        points_gdf = gdf[gdf['geometry'].geom_type == 'Point']

        polygons_gdfs.append(polygons_gdf)
        lines_gdfs.append(lines_gdf)
        points_gdfs.append(points_gdf)
        # Объедините данные в один GeoDataFrame
        # gdfs.append(gdf)

    # Объедините все GeoDataFrames в один
    # combined_gdf = pd.concat(gdfs, ignore_index=True)
    # geojson_data = json.loads(combined_gdf.to_json())

    # Прочитайте данные из файла houses1.json
    # with open('houses1.json', 'r', encoding='utf-8') as file:
    #     houses_data = json.load(file)

    # Преобразование координат и фильтрация данных
    transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
    # transformed_houses_data = transform_and_filter_houses_data(houses_data, transformer)
    # print(transformed_houses_data)

    combined_polygons_gdf = pd.concat(polygons_gdfs, ignore_index=True)
    # combined_lines_gdf = pd.concat(lines_gdfs, ignore_index=True)
    combined_points_gdf = pd.concat(points_gdfs, ignore_index=True) 

    # Открываем файл и загружаем данные
    with open('data.json', 'r') as file:
        lines = json.load(file)
    
    transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
    transformed_coordinates_list = transform_coordinates_list(lines, transformer)

    geojson_data = {
        'polygons': json.loads(combined_polygons_gdf.to_json()),
        'lines': transformed_coordinates_list,
        'points': json.loads(combined_points_gdf.to_json()),
        # 'houses': transformed_houses_data
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
    elif isinstance(geometry, Point):
        return list(geometry.coords)
    else:
        return None
    
def transform_coordinates(coords, transformer):
    if isinstance(coords, list) and isinstance(coords[0], tuple):
        return [[y, x] for x, y in [transformer.transform(x, y) for x, y in coords]]
    elif isinstance(coords, list) and isinstance(coords[0], list):
        return [transform_coordinates(polygon, transformer) for polygon in coords]
    else:
        return None

def transform_coordinates_list(coordinates_list, transformer):
    transformed_list = []
    for line in coordinates_list:
        transformed_line = []
        for point in line[:2]:  # Игнорируем третий элемент, если он есть
            x, y = point
            lat, lon = transformer.transform(x, y)
            transformed_line.append([lon, lat])

        transformed_line.append(line[2])
        transformed_list.append(transformed_line)
    return transformed_list

# def transform_and_filter_houses_data(houses_data, transformer):
#     transformed_houses = []
#     for item in houses_data:
#         if isinstance(item, list) and len(item) == 2 and item[1] not in ["ot", "metro"]:
#             transformed_item = transform_coordinates(item[0], transformer)
#             transformed_houses.append([transformed_item, item[1]])
#         elif isinstance(item, list) and len(item) > 2 and item[-1] not in ["ot", "metro"]:
#             transformed_item = transform_coordinates(item[0], transformer)
#             transformed_houses.append([transformed_item, item[-1]])
#     return transformed_houses