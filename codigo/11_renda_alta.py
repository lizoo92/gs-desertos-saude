import geopandas as gpd
import pandas as pd
import unicodedata


def limpar(nome):
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return sem_acento.upper().strip()


distritos = gpd.read_file("dados/bruto/geoportal_distrito_municipal_v2.gpkg")
distritos["chave"] = distritos["nm_distrito_municipal"].apply(limpar)
distritos["area_km2"] = distritos.geometry.area / 1e6
area = pd.DataFrame(distritos[["chave", "area_km2"]])

renda = pd.read_csv(
    "dados/bruto/Agregados_por_distritos_renda_responsavel_BR.csv",
    sep=";", encoding="latin-1", dtype=str,
)
renda = renda[renda["CD_DIST"].str.startswith("3550308")].copy()
renda["chave"] = renda["NM_DIST"].apply(limpar)
renda["renda_media"] = pd.to_numeric(renda["V06004"].str.replace(",", ".", regex=False))

indicador = pd.read_csv("dados/tratado/tb_indicador_distrito.csv")
base = indicador.merge(renda[["chave", "renda_media"]], on="chave").merge(area, on="chave")
print(len(base), "distritos após os cruzamentos")

base["hab_por_km2"] = base["populacao"] / base["area_km2"]
base["km2_por_ubs"] = (base["area_km2"] / base["qtd_ubs"]).where(base["qtd_ubs"] > 0)

CORTE = 8000

alta = base[base["renda_media"] > CORTE].sort_values("renda_media", ascending=False)
resto = base[base["renda_media"] <= CORTE]

colunas = ["nome_distrito", "renda_media", "area_km2", "hab_por_km2",
           "qtd_ubs", "km2_por_ubs", "ubs_por_100mil", "classe"]
print(f"\n--- renda média acima de R$ {CORTE} ({len(alta)} distritos) ---")
print(alta[colunas].round(1).to_string(index=False))

medidas = ["area_km2", "hab_por_km2", "km2_por_ubs", "qtd_ubs", "ubs_por_100mil"]
comparar = pd.DataFrame({
    f"acima de {CORTE} ({len(alta)})": alta[medidas].median(),
    f"até {CORTE} ({len(resto)})": resto[medidas].median(),
})
print("\n--- mediana dos dois grupos ---")
print(comparar.round(1).to_string())

print("\nsem UBS no grupo acima:", (alta["qtd_ubs"] == 0).sum())
print("sem UBS no grupo abaixo:", (resto["qtd_ubs"] == 0).sum())