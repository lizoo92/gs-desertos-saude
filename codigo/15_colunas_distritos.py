import geopandas as gpd

distritos = gpd.read_file("dados/bruto/geoportal_distrito_municipal_v2.gpkg")
print(list(distritos.columns))
print(distritos.drop(columns="geometry").head(3).to_string())