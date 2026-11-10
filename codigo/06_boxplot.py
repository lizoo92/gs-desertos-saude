import geopandas as gpd
import pandas as pd
import numpy as np
import unicodedata
import matplotlib.pyplot as plt


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
base["hab_por_km2"] = base["populacao"] / base["area_km2"]
base["km2_por_ubs"] = base["area_km2"] / base["qtd_ubs"]

com_ubs = base[base["qtd_ubs"] > 0].copy()
print("distritos com UBS:", len(com_ubs))

variaveis = [
    ("ubs_por_100mil", "UBS por 100 mil hab.", False),
    ("hab_por_ubs", "Habitantes por UBS", False),
    ("km2_por_ubs", "km² por UBS", False),
    ("hab_por_km2", "Habitantes por km² (log10)", True),
]

fig, eixos = plt.subplots(1, 4, figsize=(15, 6))

for eixo, (coluna, titulo, usa_log) in zip(eixos, variaveis):
    valores = np.log10(com_ubs[coluna]) if usa_log else com_ubs[coluna]
    inferior, superior = cercas(valores)
    fora = com_ubs[(valores < inferior) | (valores > superior)]

    mostra_inf = 10 ** inferior if usa_log else inferior
    mostra_sup = 10 ** superior if usa_log else superior
    print(f"\n--- {titulo} ---")
    print(f"cerca inferior: {mostra_inf:.2f} | cerca superior: {mostra_sup:.2f}")
    for indice in fora.index:
        print(f"  fora: {fora.loc[indice, 'nome_distrito']} = {com_ubs.loc[indice, coluna]:.2f}")

    eixo.boxplot(
        valores, whis=1.5, widths=0.45, patch_artist=True,
        boxprops={"facecolor": "#dfe5f0", "edgecolor": "#3b5b92"},
        medianprops={"color": "#3b5b92", "linewidth": 2},
        whiskerprops={"color": "#3b5b92"},
        capprops={"color": "#3b5b92"},
        flierprops={"marker": "o", "markersize": 5, "markerfacecolor": "#3b5b92", "markeredgecolor": "white"},
    )
    for indice in fora.index:
        eixo.annotate(
            fora.loc[indice, "nome_distrito"], (1, valores[indice]),
            xytext=(10, 0), textcoords="offset points", fontsize=8, va="center",
        )

    eixo.set_title(titulo, fontsize=11)
    eixo.set_xticks([])
    eixo.set_axisbelow(True)
    eixo.yaxis.grid(True, color="#e6e6e6")
    for lado in ["top", "right", "bottom"]:
        eixo.spines[lado].set_visible(False)

fig.suptitle("Boxplots dos 92 distritos com UBS: busca de outliers", fontsize=13)
fig.tight_layout()
fig.savefig("saidas/boxplot_outliers.png", dpi=150)
print("\nboxplot salvo")

baixa_densidade = ["Anhanguera", "Marsilac", "Parelheiros", "Perus", "Socorro", "Tremembé"]
colunas_conferencia = ["nome_distrito", "ubs_por_100mil", "classe", "qtd_ubs", "hab_por_km2", "km2_por_ubs"]
print("\n--- distritos de baixa densidade ---")
print(base[base["nome_distrito"].isin(baixa_densidade)][colunas_conferencia].round(2).to_string(index=False))