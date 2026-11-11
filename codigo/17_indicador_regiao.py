import geopandas as gpd
import pandas as pd
import unicodedata


def limpar(nome):
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return sem_acento.upper().strip()


distritos = gpd.read_file("dados/bruto/geoportal_distrito_municipal_v2.gpkg")
distritos["chave"] = distritos["nm_distrito_municipal"].apply(limpar)

tabela = pd.read_csv("dados/tratado/tb_indicador_distrito.csv")
base = tabela.merge(distritos[["chave", "nm_regiao_05"]], on="chave")
print(len(base))

regioes = base.groupby("nm_regiao_05").agg(
    distritos=("chave", "size"),
    populacao=("populacao", "sum"),
    qtd_ubs=("qtd_ubs", "sum"),
    distritos_sem_ubs=("classe", lambda s: (s == 0).sum()),
)
regioes["ubs_por_100mil"] = regioes["qtd_ubs"] / regioes["populacao"] * 100000
regioes["hab_por_ubs"] = regioes["populacao"] / regioes["qtd_ubs"]

print(regioes.round(2).to_string())
print(base["populacao"].sum(), base["qtd_ubs"].sum())