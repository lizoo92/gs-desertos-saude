import geopandas as gpd
import pandas as pd
import numpy as np
import unicodedata


def limpar(nome):
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return sem_acento.upper().strip()


def cercas(serie):
    q1 = serie.quantile(0.25)
    q3 = serie.quantile(0.75)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


distritos = gpd.read_file("dados/bruto/geoportal_distrito_municipal_v2.gpkg")
tabela = pd.read_csv("dados/tratado/tb_indicador_distrito.csv")

distritos["chave"] = distritos["nm_distrito_municipal"].apply(limpar)
distritos["area_km2"] = distritos.geometry.area / 1e6

base = tabela.merge(distritos[["chave", "area_km2"]], on="chave")
base["hab_por_km2"] = (base["populacao"] / base["area_km2"]).round(1)
base["km2_por_ubs"] = (base["area_km2"] / base["qtd_ubs"]).replace(np.inf, np.nan).round(1)
base["log_densidade"] = np.log10(base["hab_por_km2"])

print("distritos:", len(base))

print("\n--- 10 distritos com MENOR densidade ---")
menores = base.sort_values("hab_por_km2").head(10)
print(menores[["nome_distrito", "populacao", "area_km2", "hab_por_km2", "qtd_ubs", "ubs_por_100mil"]].round(2).to_string(index=False))

inf_log, sup_log = cercas(base["log_densidade"])
print("\ncerca inferior da densidade (escala log):", round(10 ** inf_log, 1), "hab/km2")
print(base.loc[base["log_densidade"] < inf_log, ["nome_distrito", "hab_por_km2"]].to_string(index=False))

print("\n--- 10 distritos com MAIOR km2 por UBS ---")
maiores = base.dropna(subset=["km2_por_ubs"]).sort_values("km2_por_ubs", ascending=False).head(10)
print(maiores[["nome_distrito", "area_km2", "qtd_ubs", "km2_por_ubs"]].round(1).to_string(index=False))

_, sup_km = cercas(base["km2_por_ubs"].dropna())
print("\ncerca superior de km2 por UBS:", round(sup_km, 1))
print(base.loc[base["km2_por_ubs"] > sup_km, ["nome_distrito", "km2_por_ubs"]].to_string(index=False))