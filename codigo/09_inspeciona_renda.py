import glob
import pandas as pd

arquivo = "dados/bruto/Agregados_por_distritos_renda_responsavel_BR.csv"
tabela = pd.read_csv(arquivo, sep=";", encoding="latin-1", dtype=str)

sao_paulo = tabela[tabela["CD_DIST"].str.startswith("3550308")]
print("linhas de São Paulo:", len(sao_paulo))
print((sao_paulo["V06004"] == "x").sum(), "distritos de SP com V06004 omitido ('x')")
print(sao_paulo[["NM_DIST", "V06001", "V06004", "V06006"]].head(10).to_string(index=False))

dicionarios = glob.glob("dados/bruto/dicionario_de_dados*.xlsx")
abas = pd.read_excel(dicionarios[0], sheet_name=None, dtype=str)
print("\nabas do dicionário:", list(abas.keys()))
for nome_aba, aba in abas.items():
    if "Variável" in aba.columns:
        linhas = aba[aba["Variável"].str.startswith("V06", na=False)]
        if len(linhas) > 0:
            print("\n--- aba:", nome_aba, "---")
            print(linhas.to_string(index=False))