import pandas as pd
import unicodedata
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def limpar(nome):
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return sem_acento.upper().strip()


def para_numero(serie):
    return pd.to_numeric(serie.str.replace(",", ".", regex=False), errors="coerce")


renda = pd.read_csv(
    "dados/bruto/Agregados_por_distritos_renda_responsavel_BR.csv",
    sep=";", encoding="latin-1", dtype=str,
)
renda = renda[renda["CD_DIST"].str.startswith("3550308")].copy()
renda["chave"] = renda["NM_DIST"].apply(limpar)
renda["renda_media"] = para_numero(renda["V06004"])
renda["renda_mediana"] = para_numero(renda["V06006"])

indicador = pd.read_csv("dados/tratado/tb_indicador_distrito.csv")

cruzado = indicador.merge(
    renda[["chave", "renda_media", "renda_mediana"]], on="chave", how="outer", indicator=True
)
print(cruzado["_merge"].value_counts())
print(cruzado[cruzado["_merge"] != "both"][["nome_distrito", "chave", "_merge"]])

base = cruzado[cruzado["_merge"] == "both"].copy()
com_ubs = base[base["qtd_ubs"] > 0]

print("\n--- correlação de Spearman (renda x UBS por 100 mil) ---")
for rotulo, grupo in [("96 distritos (zeros incluídos)", base), ("92 distritos com UBS", com_ubs)]:
    for coluna in ["renda_media", "renda_mediana"]:
        rho = grupo[coluna].corr(grupo["ubs_por_100mil"], method="spearman")
        print(f"{rotulo} | {coluna}: {rho:.2f}")

base["quartil_renda"] = pd.qcut(
    base["renda_media"], q=4, labels=["Q1 menor renda", "Q2", "Q3", "Q4 maior renda"]
)
resumo = base.groupby("quartil_renda", observed=True).agg(
    distritos=("chave", "count"),
    mediana_ubs_por_100mil=("ubs_por_100mil", "median"),
    mediana_qtd_ubs=("qtd_ubs", "median"),
    sem_ubs=("qtd_ubs", lambda s: (s == 0).sum()),
)
print("\n--- por quartil de renda média ---")
print(resumo.round(2).to_string())

foco = ["Pinheiros", "Campo Belo", "Jardim Paulista", "Mooca", "Tatuapé"]
base["posicao_renda"] = base["renda_media"].rank(ascending=False).astype(int)
colunas = ["nome_distrito", "renda_media", "renda_mediana", "posicao_renda",
           "quartil_renda", "ubs_por_100mil", "qtd_ubs", "classe"]
print("\n--- distritos em foco (posição 1 = maior renda) ---")
print(base[base["nome_distrito"].isin(foco)][colunas].round(1).to_string(index=False))

grafico = base[base["classe"] != 8]
normais = grafico[grafico["classe"] != 0]
zeros = grafico[grafico["classe"] == 0]

fig, eixo = plt.subplots(figsize=(10, 6.5))
eixo.scatter(normais["renda_media"], normais["ubs_por_100mil"], s=40, color="#8a8a8a",
             edgecolors="white", linewidths=0.8, zorder=3, label="Distritos com UBS")
eixo.scatter(zeros["renda_media"], zeros["ubs_por_100mil"], s=40, color="#3b5b92",
             edgecolors="white", linewidths=0.8, zorder=3, label="Sem UBS (classe 0)")
for nome in foco:
    linha = base[base["nome_distrito"] == nome].iloc[0]
    eixo.annotate(nome, (linha["renda_media"], linha["ubs_por_100mil"]),
                  xytext=(6, 6), textcoords="offset points", fontsize=8.5)

eixo.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"R$ {int(v):,}".replace(",", ".")))
eixo.set_xlabel("Renda média mensal da pessoa responsável pelo domicílio (Censo 2022)")
eixo.set_ylabel("UBS públicas por 100 mil habitantes")
eixo.set_title("Renda x oferta de UBS por distrito (sem os 2 outliers da classe 8)", fontsize=12)
eixo.set_axisbelow(True)
eixo.grid(True, color="#e6e6e6")
for lado in ["top", "right"]:
    eixo.spines[lado].set_visible(False)
eixo.legend(frameon=False, loc="upper right")

fig.tight_layout()
fig.savefig("saidas/renda_x_ubs.png", dpi=150)
print("\ngráfico salvo")