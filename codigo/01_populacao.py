import pandas as pd

df = pd.read_csv(
    "dados/bruto/Agregados_por_distritos_basico_BR.csv",
    sep=";",
    encoding="latin-1",
    decimal=",",
)

sp = df[df["CD_MUN"] == 3550308]

pop = pd.DataFrame({
    "distrito_id": sp["CD_DIST"],
    "nome_distrito": sp["NM_DIST"],
        "populacao": pd.to_numeric(sp["v0001"], errors="coerce"),
    "ano_censo": 2022,
    "data_carga": "2026-11-10",
})

pop.to_csv("dados/tratado/tb_populacao_distrito.csv", index=False)

print(len(pop))
print(pop["populacao"].isna().sum())
print(pop["populacao"].sum())