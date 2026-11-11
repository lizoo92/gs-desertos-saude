import pandas as pd
import unicodedata


def limpar(nome):
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return sem_acento.upper().strip()


renda = pd.read_csv(
    "dados/bruto/Agregados_por_distritos_renda_responsavel_BR.csv",
    sep=";", encoding="latin-1", dtype=str,
)
renda = renda[renda["CD_DIST"].str.startswith("3550308")].copy()
renda["chave"] = renda["NM_DIST"].apply(limpar)
renda["renda_media"] = pd.to_numeric(renda["V06004"].str.replace(",", ".", regex=False))

indicador = pd.read_csv("dados/tratado/tb_indicador_distrito.csv")
base = indicador.merge(renda[["chave", "renda_media"]], on="chave")

carentes = base[base["classe"].isin([0, 1])].sort_values("renda_media")
colunas = ["nome_distrito", "populacao", "qtd_ubs", "ubs_por_100mil", "hab_por_ubs", "renda_media", "classe"]
print("--- distritos das classes 0 e 1, da menor para a maior renda ---")
print(carentes[colunas].round(1).to_string(index=False))

total = base["populacao"].sum()
sem_ubs = base.loc[base["classe"] == 0, "populacao"].sum()
classe01 = carentes["populacao"].sum()
print("\npopulação dos 96 distritos:", total)
print("população nos distritos sem UBS (classe 0):", sem_ubs)
print("população nas classes 0 e 1:", classe01, f"({classe01 / total:.1%})")