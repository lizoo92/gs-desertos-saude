import geopandas as gpd
import pandas as pd
import unicodedata
import folium
from branca.element import MacroElement
from jinja2 import Template

def limpar(nome):
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return sem_acento.upper().strip()


distritos = gpd.read_file("dados/bruto/geoportal_distrito_municipal_v2.gpkg")
tabela = pd.read_csv("dados/tratado/tb_indicador_distrito.csv")

distritos["chave"] = distritos["nm_distrito_municipal"].apply(limpar)
distritos["area_km2"] = distritos.geometry.area / 1e6
dados_mapa = distritos[["chave", "area_km2", "geometry"]].merge(tabela, on="chave")
dados_mapa = dados_mapa.to_crs(epsg=4326)

def com_ponto(valor):
    return f"{int(valor):,}".replace(",", ".")


def texto_indicador(linha):
    taxa = f"{linha['ubs_por_100mil']:.2f}".replace(".", ",")
    if pd.isna(linha["hab_por_ubs"]):
        return f"{taxa} (sem nenhuma UBS)"
    return f"{taxa} ({com_ponto(linha['hab_por_ubs'])} hab. por UBS)"

dados_mapa["area_texto"] = dados_mapa["area_km2"].apply(lambda v: f"{v:.1f}".replace(".", ","))
dados_mapa["pop_texto"] = dados_mapa["populacao"].apply(com_ponto)
dados_mapa["indicador_texto"] = dados_mapa.apply(texto_indicador, axis=1)

print(len(dados_mapa))
print(dados_mapa.crs)
print(dados_mapa[["nome_distrito", "ubs_por_100mil", "classe"]].head())


CORES = {
    0: "#3b5b92",
    1: "#b10026",
    2: "#e31a1c",
    3: "#fc4e2a",
    4: "#fd8d3c",
    5: "#feb24c",
    6: "#fed976",
    7: "#ffffb2",
    8: "#7570b3",
}


def estilo(feature):
    classe = feature["properties"]["classe"]
    return {
        "fillColor": CORES[classe],
        "color": "#555555",
        "weight": 0.8,
        "fillOpacity": 0.85,
    }


mapa = folium.Map(location=[-23.55, -46.63], zoom_start=10, tiles=None)
folium.TileLayer("OpenStreetMap", name="Mapa base (OpenStreetMap)").add_to(mapa)

colunas = ["nome_distrito", "pop_texto", "area_texto", "qtd_ubs", "indicador_texto", "classe", "faixa_texto", "geometry"]

def texto_faixa(classe):
    if classe == 0:
        return "sem UBS dentro do distrito"
    if classe == 8:
        return "outlier (fora das 7 faixas)"
    return f"{classe} de 7 (1 = menor oferta)"


dados_mapa["faixa_texto"] = dados_mapa["classe"].apply(texto_faixa)

folium.GeoJson(
    dados_mapa[colunas],
    style_function=estilo,
    name="Distritos (UBS por 100 mil hab.)",
    tooltip=folium.GeoJsonTooltip(
        fields=["nome_distrito", "pop_texto", "area_texto", "qtd_ubs", "indicador_texto", "faixa_texto"],
        aliases=["Distrito", "População", "Área (km²)", "UBS públicas", "UBS por 100 mil hab.", "Faixa"],
    ),
).add_to(mapa)

ubs = gpd.read_file("dados/bruto/geoportal_equipamento_saude_ubs_posto_centro_v2.gpkg")
ubs = ubs[ubs["nm_esfera_administrativa_equipamento"].isin(["Municipal", "Estadual"])]
ubs = ubs.to_crs(epsg=4326)

camada_ubs = folium.FeatureGroup(name="UBS públicas (pontos)", show=True)

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
folium.LayerControl(collapsed=False).add_to(mapa)

dados_mapa["ordem_area"] = dados_mapa["area_km2"].rank(ascending=False, method="first")


def zoom_do_rotulo(ordem):
    if ordem <= 24:
        return 10
    if ordem <= 48:
        return 11
    if ordem <= 72:
        return 12
    return 13


dados_mapa["zoom_rotulo"] = dados_mapa["ordem_area"].apply(zoom_do_rotulo)
print(dados_mapa["zoom_rotulo"].value_counts().sort_index())

pontos = dados_mapa.geometry.representative_point()

def quadradinho(cor):
    return (
        f'<span style="display:inline-block;width:14px;height:14px;'
        f'background:{cor};border:1px solid #555;margin-right:6px;'
        f'vertical-align:middle;"></span>'
    )


limites = dados_mapa.groupby("classe")["ubs_por_100mil"].agg(["min", "max"])

linhas = ""
for classe in [1, 2, 3, 4, 5, 6, 7]:
    menor = f"{limites.loc[classe, 'min']:.2f}".replace(".", ",")
    maior = f"{limites.loc[classe, 'max']:.2f}".replace(".", ",")
    extra = ""
    if classe == 1:
        extra = " (menor oferta)"
    if classe == 7:
        extra = " (maior oferta)"
    linhas += f"<div>{quadradinho(CORES[classe])}{menor} a {maior}{extra}</div>"
for nome, ponto, zoom, ordem in zip(
    dados_mapa["nome_distrito"], pontos, dados_mapa["zoom_rotulo"], dados_mapa["ordem_area"]
):
    html = f'<div class="rotulo-distrito" data-zoom="{zoom}" data-ordem="{int(ordem)}">{nome}</div>'
    folium.Marker(
        location=[ponto.y, ponto.x],
        icon=folium.DivIcon(html=html, icon_size=(0, 0), icon_anchor=(0, 0)),
    ).add_to(mapa)

class ZoomRotulos(MacroElement):
    _template = Template("""
        {% macro script(this, kwargs) %}
        var mapaRef = {{ this._parent.get_name() }};

        function atualizarRotulos() {
            var zoomAtual = mapaRef.getZoom();
            var rotulos = Array.from(document.querySelectorAll('.rotulo-distrito'));
            rotulos.sort(function (a, b) {
                return Number(a.dataset.ordem) - Number(b.dataset.ordem);
            });

            var ocupados = [];
            rotulos.forEach(function (el) {
                var visivel = zoomAtual >= Number(el.dataset.zoom);

                if (visivel) {
                    var caixa = el.getBoundingClientRect();
                    var bate = ocupados.some(function (o) {
                        return caixa.left < o.right + 3 && caixa.right > o.left - 3 &&
                               caixa.top < o.bottom + 2 && caixa.bottom > o.top - 2;
                    });
                    if (bate) {
                        visivel = false;
                    } else {
                        ocupados.push(caixa);
                    }
                }

                el.style.opacity = visivel ? 1 : 0;
            });
        }

        mapaRef.on('zoomend', atualizarRotulos);
        atualizarRotulos();
        {% endmacro %}
    """)


mapa.add_child(ZoomRotulos())

outl = dados_mapa[dados_mapa["classe"] == 8]
nomes = ", ".join(outl["nome_distrito"])
menor8 = f"{outl['ubs_por_100mil'].min():.2f}".replace(".", ",")
maior8 = f"{outl['ubs_por_100mil'].max():.2f}".replace(".", ",")
linhas += f"<div style='margin-top:6px'>{quadradinho(CORES[8])}{menor8} a {maior8} (outlier: {nomes})</div>"
linhas += f"<div style='margin-top:6px'>{quadradinho(CORES[0])}Sem UBS pública dentro do distrito</div>"

legenda = f"""
<div style="position:fixed;bottom:30px;left:30px;z-index:9999;background:white;
padding:10px 12px;border:1px solid #888;border-radius:6px;font-size:12px;
line-height:1.5;box-shadow:0 1px 4px rgba(0,0,0,0.3);">
<b>UBS públicas por 100 mil habitantes</b><br>
<span style="color:#555;">7 faixas por quantil, entre os distritos com UBS, exceto outliers</span>
{linhas}
<div style="margin-top:6px;color:#555;font-size:11px;">
Fontes: GeoSampa (Prefeitura de SP); IBGE, Censo 2022</div>
</div>
"""

titulo = """
<div style="position:fixed;top:10px;left:50%;transform:translateX(-50%);z-index:9999;
background:white;padding:6px 14px;border:1px solid #888;border-radius:6px;
font-size:15px;font-weight:bold;box-shadow:0 1px 4px rgba(0,0,0,0.3);">
Oferta de UBS públicas por distrito, município de São Paulo
</div>
"""

estilo_rotulos = """
<style>
.rotulo-distrito {
  transition: opacity 0.3s;
  position: absolute;
  transform: translate(-50%, -50%);
  white-space: nowrap;
  pointer-events: none;
  font-size: 11px;
  font-weight: 600;
  color: #222;
  text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;
}
</style>
"""

dados_ranking = dados_mapa[["nome_distrito", "ubs_por_100mil", "qtd_ubs", "populacao"]].to_json(orient="records", force_ascii=False)

ranking = """
<div id="ranking" style="position:fixed;bottom:30px;right:10px;z-index:9999;background:white;
border:1px solid #888;border-radius:6px;box-shadow:0 1px 4px rgba(0,0,0,0.3);font-size:12px;width:360px;">
<div style="padding:6px 10px;font-weight:bold;border-bottom:1px solid #ccc;">
Ranking de distritos
<span style="font-weight:normal;color:#555;">(clique no título da coluna para ordenar)</span>
</div>
<div style="max-height:260px;overflow-y:auto;">
<table style="width:100%;border-collapse:collapse;">
<thead><tr>
<th data-chave="nome_distrito" data-rotulo="Distrito">Distrito</th>
<th data-chave="ubs_por_100mil" data-rotulo="UBS por 100 mil">UBS por 100 mil</th>
<th data-chave="qtd_ubs" data-rotulo="UBS">UBS</th>
<th data-chave="populacao" data-rotulo="População">População</th>
</tr></thead>
<tbody id="rank-corpo"></tbody>
</table>
</div>
</div>
<style>
#ranking th { cursor:pointer; position:sticky; top:0; background:#f0f0f0; text-align:left; padding:4px 6px; }
#ranking td { padding:3px 6px; border-top:1px solid #eee; }
</style>
<script>
(function () {
    var dados = __DADOS__;
    var chave = "ubs_por_100mil";
    var crescente = true;

    function desenhar() {
        dados.sort(function (a, b) {
            var va = a[chave];
            var vb = b[chave];
            if (typeof va === "string") {
                return crescente ? va.localeCompare(vb, "pt-BR") : vb.localeCompare(va, "pt-BR");
            }
            return crescente ? va - vb : vb - va;
        });

        document.getElementById("rank-corpo").innerHTML = dados.map(function (d) {
            return "<tr><td>" + d.nome_distrito + "</td><td>" +
                d.ubs_por_100mil.toFixed(2).replace(".", ",") + "</td><td>" +
                d.qtd_ubs + "</td><td>" + d.populacao.toLocaleString("pt-BR") + "</td></tr>";
        }).join("");

        document.querySelectorAll("#ranking th").forEach(function (th) {
            var seta = "";
            if (th.dataset.chave === chave) {
                seta = crescente ? " ▲" : " ▼";
            }
            th.textContent = th.dataset.rotulo + seta;
        });
    }

    document.querySelectorAll("#ranking th").forEach(function (th) {
        th.addEventListener("click", function () {
            if (chave === th.dataset.chave) {
                crescente = !crescente;
            } else {
                chave = th.dataset.chave;
                crescente = true;
            }
            desenhar();
        });
    });

    desenhar();
})();
</script>
"""
ranking = ranking.replace("__DADOS__", dados_ranking)

mapa.get_root().html.add_child(folium.Element(legenda + titulo + estilo_rotulos + ranking))
mapa.save("saidas/mapa_ubs_distrito.html")
print("mapa salvo")