import geopandas as gpd
import pandas as pd
import unicodedata


def limpar(nome):
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return sem_acento.upper().strip()


distritos = gpd.read_file("dados/bruto/geoportal_distrito_municipal_v2.gpkg")
tabela = pd.read_csv("dados/tratado/tb_indicador_distrito.csv")

distritos["chave"] = distritos["nm_distrito_municipal"].apply(limpar)
distritos["area_km2"] = distritos.geometry.area / 1e6

base = tabela.merge(distritos[["chave", "area_km2"]], on="chave")
base["hab_por_km2"] = base["populacao"] / base["area_km2"]

print("mediana da área (km²):", round(base["area_km2"].median(), 1))
print("mediana da população:", int(base["populacao"].median()))
print("mediana da densidade (hab/km²):", int(base["hab_por_km2"].median()))

poucas = base[base["qtd_ubs"] <= 1].sort_values("populacao", ascending=False)
colunas = ["nome_distrito", "populacao", "area_km2", "hab_por_km2", "qtd_ubs", "hab_por_ubs", "classe"]
print("\n--- distritos com 0 ou 1 UBS (", len(poucas), ") ---")
print(poucas[colunas].round(1).to_string(index=False))