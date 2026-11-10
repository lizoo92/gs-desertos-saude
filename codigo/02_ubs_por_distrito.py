import geopandas as gpd

ubs = gpd.read_file("dados/bruto/geoportal_equipamento_saude_ubs_posto_centro_v2.gpkg")
distritos = gpd.read_file("dados/bruto/geoportal_distrito_municipal_v2.gpkg")

print(len(ubs), len(distritos))
print(ubs["nm_esfera_administrativa_equipamento"].value_counts())
print(ubs.crs == distritos.crs)

publicas = ubs[ubs["nm_esfera_administrativa_equipamento"].isin(["Municipal", "Estadual"])]

ubs_distrito = gpd.sjoin(
    publicas,
    distritos[["nm_distrito_municipal", "geometry"]],
    how="left",
    predicate="within",
)

print(len(publicas))
print(len(ubs_distrito))
print(ubs_distrito["nm_distrito_municipal"].isna().sum())

contagem = ubs_distrito.groupby("nm_distrito_municipal").size().reset_index(name="qtd_ubs")

base = distritos[["nm_distrito_municipal"]].merge(contagem, on="nm_distrito_municipal", how="left")
base["qtd_ubs"] = base["qtd_ubs"].fillna(0).astype(int)

base.to_csv("dados/tratado/tb_ubs_distrito.csv", index=False)

print(len(base))
print(base["qtd_ubs"].sum())
print((base["qtd_ubs"] == 0).sum())
print(base.sort_values("qtd_ubs").head(5))