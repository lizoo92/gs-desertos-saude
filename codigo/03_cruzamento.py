import pandas as pd
import unicodedata


def limpar(nome):
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return sem_acento.upper().strip()


pop = pd.read_csv("dados/tratado/tb_populacao_distrito.csv")
ubs = pd.read_csv("dados/tratado/tb_ubs_distrito.csv")

pop["chave"] = pop["nome_distrito"].apply(limpar)
ubs["chave"] = ubs["nm_distrito_municipal"].apply(limpar)

cruzado = pop.merge(ubs, on="chave", how="outer", indicator=True)

print(cruzado["_merge"].value_counts())
print(cruzado[cruzado["_merge"] != "both"][["nome_distrito", "nm_distrito_municipal", "_merge"]])

base = cruzado[["distrito_id", "nome_distrito", "populacao", "qtd_ubs"]].copy()
base["chave"] = cruzado["chave"]
base["ubs_por_100mil"] = (base["qtd_ubs"] / base["populacao"] * 100000).round(2)
base["hab_por_ubs"] = (base["populacao"] / base["qtd_ubs"]).round(0)
base["hab_por_ubs"] = base["hab_por_ubs"].replace(float("inf"), float("nan"))

OUTLIERS = ["MARSILAC", "PARELHEIROS"]

tem_ubs = base["qtd_ubs"] > 0
eh_outlier = base["chave"].isin(OUTLIERS)
normais = tem_ubs & ~eh_outlier

assert eh_outlier.sum() == len(OUTLIERS)

base["classe"] = 0
base.loc[normais, "classe"] = pd.qcut(
    base.loc[normais, "ubs_por_100mil"], q=7, labels=[1, 2, 3, 4, 5, 6, 7]
).astype(int)
base.loc[eh_outlier, "classe"] = 8

print(base.groupby("classe")["ubs_por_100mil"].agg(["min", "max", "count"]))

base.to_csv("dados/tratado/tb_indicador_distrito.csv", index=False)