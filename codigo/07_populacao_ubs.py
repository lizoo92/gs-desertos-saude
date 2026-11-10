import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

base = pd.read_csv("dados/tratado/tb_indicador_distrito.csv")

print("distritos por número de UBS:")
print(base["qtd_ubs"].value_counts().sort_index().to_string())

com_ubs = base[base["qtd_ubs"] > 0]
print("\nacima de 18 mil hab/UBS:", (com_ubs["hab_por_ubs"] > 18000).sum(), "de", len(com_ubs), "com UBS")
print("acima de 12 mil hab/UBS:", (com_ubs["hab_por_ubs"] > 12000).sum(), "de", len(com_ubs), "com UBS")
print("sem nenhuma UBS:", (base["qtd_ubs"] == 0).sum())

pop_pinheiros = base.loc[base["nome_distrito"] == "Pinheiros", "populacao"].iloc[0]
parecidos = base[
    (base["populacao"] >= pop_pinheiros * 0.8) & (base["populacao"] <= pop_pinheiros * 1.2)
].sort_values("populacao")
print("\n--- distritos com população entre 80% e 120% da de Pinheiros ---")
print(parecidos[["nome_distrito", "populacao", "qtd_ubs", "hab_por_ubs", "classe"]].to_string(index=False))

grupos = [
    ("Demais distritos", base[~base["classe"].isin([0, 8])], "#8a8a8a"),
    ("Sem UBS (classe 0)", base[base["classe"] == 0], "#3b5b92"),
    ("Outliers (classe 8)", base[base["classe"] == 8], "#7570b3"),
]

fig, eixo = plt.subplots(figsize=(11, 7))

limite = base["populacao"].max() * 1.05
eixo.plot([0, limite], [0, limite / 18000], color="#b0b0b0", linestyle="--", linewidth=1)
eixo.plot([0, limite], [0, limite / 12000], color="#b0b0b0", linestyle=":", linewidth=1.2)
eixo.text(limite, limite / 18000, "  18 mil hab/UBS", va="center", fontsize=8, color="#666666")
eixo.text(limite, limite / 12000, "  12 mil hab/UBS", va="center", fontsize=8, color="#666666")

for nome, parte, cor in grupos:
    eixo.scatter(
        parte["populacao"], parte["qtd_ubs"], s=40, color=cor,
        edgecolors="white", linewidths=0.8, zorder=3, label=nome,
    )

pinheiros = base[base["nome_distrito"] == "Pinheiros"]
eixo.scatter(
    pinheiros["populacao"], pinheiros["qtd_ubs"], s=140, facecolors="none",
    edgecolors="#222222", linewidths=1.5, zorder=4,
)

rotulos = {
    "Pinheiros": (8, -14),
    "Moema": (8, 6),
    "Jardim Paulista": (8, 8),
    "Mooca": (8, -10),
    "Tatuapé": (8, 6),
    "Campo Belo": (8, 6),
    "Marsilac": (8, 6),
    "Parelheiros": (8, 6),
}
for nome, deslocamento in rotulos.items():
    linha = base[base["nome_distrito"] == nome].iloc[0]
    eixo.annotate(
        nome, (linha["populacao"], linha["qtd_ubs"]),
        xytext=deslocamento, textcoords="offset points", fontsize=8.5,
    )

eixo.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}".replace(",", ".")))
eixo.set_xlim(0, limite * 1.12)
eixo.set_ylim(-0.5, base["qtd_ubs"].max() + 2)
eixo.set_xlabel("População do distrito (Censo 2022)")
eixo.set_ylabel("UBS públicas dentro do distrito")
eixo.set_title("População x número de UBS, 96 distritos de São Paulo", fontsize=13)
eixo.set_axisbelow(True)
eixo.grid(True, color="#e6e6e6")
for lado in ["top", "right"]:
    eixo.spines[lado].set_visible(False)
eixo.legend(frameon=False, loc="upper left")

fig.tight_layout()
fig.savefig("saidas/populacao_x_ubs.png", dpi=150)
print("\ngráfico salvo")