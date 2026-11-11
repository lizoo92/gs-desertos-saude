import geopandas as gpd

ubs = gpd.read_file("dados/bruto/geoportal_equipamento_saude_ubs_posto_centro_v2.gpkg")

publicas = ubs[ubs["nm_esfera_administrativa_equipamento"].isin(["Municipal", "Estadual"])]

publicas = publicas.to_crs(epsg=4326)

print(len(publicas))
print(publicas.geometry.geom_type.value_counts())
print(publicas.geometry.isna().sum())
print(list(publicas.columns))