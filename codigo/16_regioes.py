import geopandas as gpd

distritos = gpd.read_file("dados/bruto/geoportal_distrito_municipal_v2.gpkg")

print(distritos.groupby("nm_regiao_05").size())
print(distritos.groupby("nm_regiao_05")["nm_distrito_municipal"].apply(lambda s: ", ".join(sorted(s))).to_string())
print(distritos["nm_regiao_05"].isna().sum())