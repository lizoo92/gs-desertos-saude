import geopandas as gpd
import pandas as pd

ubs = gpd.read_file("dados/bruto/geoportal_equipamento_saude_ubs_posto_centro_v2.gpkg")
distritos = gpd.read_file("dados/bruto/geoportal_distrito_municipal_v2.gpkg")
tabela = pd.read_csv("dados/tratado/tb_ubs_distrito.csv")

publicas = ubs[ubs["nm_esfera_administrativa_equipamento"].isin(["Municipal", "Estadual"])]
publicas = publicas.to_crs(distritos.crs)

junta = gpd.sjoin(publicas, distritos[["nm_distrito_municipal", "geometry"]], how="left", predicate="within")
conta = junta.groupby("nm_distrito_municipal").size().rename("pontos")

comp = tabela.merge(conta, on="nm_distrito_municipal", how="left")
comp["pontos"] = comp["pontos"].fillna(0).astype(int)

print((comp["qtd_ubs"] != comp["pontos"]).sum())
print(comp[comp["nm_distrito_municipal"].str.upper().isin(["MARSILAC", "PARELHEIROS"])])
print(comp[comp["qtd_ubs"] == 1])
