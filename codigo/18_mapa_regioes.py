import geopandas as gpd
import pandas as pd
import unicodedata
import folium
from branca.colormap import LinearColormap


def limpar(nome):
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return sem_acento.upper().strip()


def com_ponto(valor):
    return f"{int(round(valor)):,}".replace(",", ".")


distritos = gpd.read_file("dados/bruto/geoportal_distrito_municipal_v2.gpkg")
distritos["chave"] = distritos["nm_distrito_municipal"].apply(limpar)

tabela = pd.read_csv("dados/tratado/tb_indicador_distrito.csv")
base = tabela.merge(distritos[["chave", "nm_regiao_05"]], on="chave")

regioes = base.groupby("nm_regiao_05").agg(
    distritos=("chave", "size"),
    populacao=("populacao", "sum"),
    qtd_ubs=("qtd_ubs", "sum"),
    distritos_sem_ubs=("classe", lambda s: (s == 0).sum()),
).reset_index()
regioes["ubs_por_100mil"] = regioes["qtd_ubs"] / regioes["populacao"] * 100000
regioes["hab_por_ubs"] = regioes["populacao"] / regioes["qtd_ubs"]

formas = distritos[["nm_regiao_05", "geometry"]].dissolve(by="nm_regiao_05").reset_index()
formas = formas.to_crs(epsg=4326)
dados = formas.merge(regioes, on="nm_regiao_05")
print(len(dados))

dados["pop_texto"] = dados["populacao"].apply(com_ponto)
dados["hab_texto"] = dados["hab_por_ubs"].apply(com_ponto)
dados["ind_texto"] = dados["ubs_por_100mil"].apply(lambda v: f"{v:.2f}".replace(".", ","))

escala = LinearColormap(
    ["#b10026", "#ffffb2"],
    vmin=dados["ubs_por_100mil"].min(),
    vmax=dados["ubs_por_100mil"].max(),
)
escala.caption = "UBS públicas por 100 mil habitantes (por região)"


def estilo(feature):
    return {
        "fillColor": escala(feature["properties"]["ubs_por_100mil"]),
        "color": "#333333",
        "weight": 1.5,
        "fillOpacity": 0.85,
    }


mapa = folium.Map(location=[-23.55, -46.63], zoom_start=10, tiles="OpenStreetMap")

colunas = ["nm_regiao_05", "pop_texto", "qtd_ubs", "ind_texto", "hab_texto", "distritos", "distritos_sem_ubs", "ubs_por_100mil", "geometry"]

folium.GeoJson(
    dados[colunas],
    style_function=estilo,
    tooltip=folium.GeoJsonTooltip(
        fields=["nm_regiao_05", "distritos", "pop_texto", "qtd_ubs", "ind_texto", "hab_texto", "distritos_sem_ubs"],
        aliases=["Região", "Distritos", "População", "UBS públicas", "UBS por 100 mil hab.", "Habitantes por UBS", "Distritos sem UBS"],
    ),
).add_to(mapa)

escala.add_to(mapa)

pontos = dados.geometry.representative_point()
for nome, valor, ponto in zip(dados["nm_regiao_05"], dados["ind_texto"], pontos):
    html = (
        '<div style="transform:translate(-50%,-50%);white-space:nowrap;text-align:center;'
        'font-weight:700;font-size:13px;color:#222;pointer-events:none;'
        'text-shadow:-1px -1px 0 #fff,1px -1px 0 #fff,-1px 1px 0 #fff,1px 1px 0 #fff;">'
        f"{nome}<br>{valor}</div>"
    )
    folium.Marker(
        location=[ponto.y, ponto.x],
        icon=folium.DivIcon(html=html, icon_size=(0, 0), icon_anchor=(0, 0)),
    ).add_to(mapa)

ubs = gpd.read_file("dados/bruto/geoportal_equipamento_saude_ubs_posto_centro_v2.gpkg")
ubs = ubs[ubs["nm_esfera_administrativa_equipamento"].isin(["Municipal", "Estadual"])]
ubs = ubs.to_crs(epsg=4326)

camada_ubs = folium.FeatureGroup(name="UBS públicas (pontos)", show=False)
for nome, endereco, ponto in zip(ubs["nm_equipamento"], ubs["tx_endereco_equipamento"], ubs.geometry):
    folium.CircleMarker(
        location=[ponto.y, ponto.x],
        radius=3,
        color="#000000",
        weight=1,
        fill=True,
        fill_color="#ffffff",
        fill_opacity=1,
        tooltip=f"{nome}<br>{endereco}",
    ).add_to(camada_ubs)
camada_ubs.add_to(mapa)
folium.LayerControl(position="bottomleft", collapsed=False).add_to(mapa)

titulo = """
<div style="position:fixed;top:10px;left:50%;transform:translateX(-50%);z-index:9999;
background:white;padding:6px 14px;border:1px solid #888;border-radius:6px;
font-size:15px;font-weight:bold;box-shadow:0 1px 4px rgba(0,0,0,0.3);">
Oferta de UBS públicas por região, município de São Paulo
</div>
<div style="position:fixed;bottom:30px;right:10px;z-index:9999;background:white;
padding:8px 10px;border:1px solid #888;border-radius:6px;font-size:11px;color:#555;
max-width:300px;box-shadow:0 1px 4px rgba(0,0,0,0.3);">
Regiões conforme o campo nm_regiao_05 do GeoSampa. Indicador recalculado a partir
da soma de população e UBS de cada região. Fontes: GeoSampa; IBGE, Censo 2022.
</div>
"""

mapa.get_root().html.add_child(folium.Element(titulo))
mapa.save("saidas/mapa_regioes.html")
print("mapa de regiões salvo")