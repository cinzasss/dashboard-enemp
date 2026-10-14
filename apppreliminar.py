import re
import unicodedata
from difflib import SequenceMatcher
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================================
# VERSÃO DE CACHE
# ----------------------------------------------------------
# Incrementar SEMPRE que a ESTRUTURA do retorno de funções
# cacheadas mudar. Isso força o Streamlit a descartar a cache
# antiga e recalcular.
# ==========================================================
CACHE_VERSION = 2

# Descomente UMA vez se quiser forçar a limpeza total da cache agora.
# st.cache_data.clear()

# ==========================================================
# DICIONÁRIO DE ALIASES DE INSTITUIÇÕES
# ==========================================================
ALIASES_INSTITUICAO = [
    ("UNIFESSPA - Universidade Federal do Sul e Sudeste do Pará", [r'\bUNIFESSPA\b']),
    ("UFPA - Universidade Federal do Pará", [r'\bUFPA\b', r'FEDERAL DO PAR[ÁA]\b(?!.{0,15}SUL)']),
    ("UFRRJ - Universidade Federal Rural do Rio de Janeiro", [r'\bUFRRJ\b', r'\bUFRURALRJ\b', r'RURAL DO RIO DE JANEIRO']),
    ("UFRJ - Universidade Federal do Rio de Janeiro", [r'\bUFRJ\b', r'\bCOPPE\b', r'\bNIDF\b', r'^UNIVERSIDADE FEDERAL DO RIO DE JANEIRO$']),
    ("UFU - Universidade Federal de Uberlândia", [r'\bUFU\b', r'FEDERAL DE UBERL[ÂA]NDIA', r'FEDRAL DE UBERL[ÂA]NDIA']),
    ("UFS - Universidade Federal de Sergipe", [r'\bUFS\b', r'FEDERAL DE SERGIPE']),
    ("UFAL - Universidade Federal de Alagoas", [r'\bUFAL\b', r'FEDERAL DE ALAGOAS']),
    ("IFTM - Instituto Federal do Triângulo Mineiro", [r'\bIFTM\b']),
    ("UFTM - Universidade Federal do Triângulo Mineiro", [r'\bUFTM\b', r'FEDERAL DO TRI[ÂA]NGULO MINEIRO']),
    ("IFES - Instituto Federal do Espírito Santo", [r'\bIFES\b', r'INSTITUTO FEDERAL.{0,40}ESP[IÍ]RITO SANTO']),
    ("UFES - Universidade Federal do Espírito Santo", [r'\bUFES\b', r'\bCEUNES\b', r'FEDERAL DO ESP[IÍ]RITO SANTOS?\b']),
    ("UTFPR - Universidade Tecnológica Federal do Paraná", [r'\bUTFPR\b', r'\bCERNN\b', r'TECNOL[ÓO]GICA FEDERAL DO PARAN[ÁA]']),
    ("UFV - Universidade Federal de Viçosa", [r'\bUFV\b', r'FEDERAL DE VI[ÇC]OSA']),
    ("UFLA - Universidade Federal de Lavras", [r'\bUFLA\b', r'FEDERAL DE LAVRAS']),
    ("UFSCAR - Universidade Federal de São Carlos", [r'\bUFSCAR\b', r'FEDERAL DE S[ÃA]O CARLOS']),
    ("UNIPAMPA - Universidade Federal do Pampa", [r'\bUNIPAMPA\b', r'FEDERAL DO PAMPA']),
    ("UFMT - Universidade Federal de Mato Grosso", [r'\bUFMT\b', r'FEDERAL DE? MATO GROSSO']),
    ("UENF - Universidade Estadual do Norte Fluminense", [r'\bUENF\b', r'ESTADUAL DO NORTE FLUMINENSE']),
    ("UEM - Universidade Estadual de Maringá", [r'\bUEM\b', r'ESTADUAL DE ?MARING[ÁA]']),
    ("UNICAMP - Universidade Estadual de Campinas", [r'\bUNICAMP\b', r'ESTADUAL DE CAMPINAS']),
    ("UEG - Universidade Estadual de Goiás", [r'\bUEG\b', r'ESTADUAL DE GOI[ÁA]S']),
    ("UFG - Universidade Federal de Goiás", [r'\bUFG\b', r'FEDERAL DE GOI[ÁA]S']),
    ("USP - Universidade de São Paulo", [r'\bUSP\b', r'\bFCFRP\b', r'^UNIVERSIDADE DE S[ÃA]O PAULO$']),
    ("UFRN - Universidade Federal do Rio Grande do Norte", [r'\bUFRN\b', r'FEDERAL DO RIO GRANDE DO NORTE']),
    ("IFRN - Instituto Federal do Rio Grande do Norte", [r'\bIFRN\b']),
    ("UFAM - Universidade Federal do Amazonas", [r'\bUFAM\b', r'FEDERAL DO AMAZONAS']),
    ("UFSM - Universidade Federal de Santa Maria", [r'\bUFSM\b', r'FEDERAL DE SANTA MARIA']),
    ("UFCG - Universidade Federal de Campina Grande", [r'\bUFCG\b', r'FEDERAL DE? CAMPINA GRANDE']),
    ("UNESP - Universidade Estadual Paulista", [r'\bUNESP\b', r'ESTADUAL PAULISTA']),
    ("IFSP - Instituto Federal de São Paulo", [r'\bIFSP\b']),
    ("UFRPE - Universidade Federal Rural de Pernambuco", [r'\bUFRPE\b', r'RURAL DE PERNAMBUCO']),
    ("UFPE - Universidade Federal de Pernambuco", [r'\bUFPE\b', r'^UNIVERSIDADE FEDERAL DE PERNAMBUCO$']),
    ("IFBA - Instituto Federal da Bahia", [r'\bIFBA\b', r'INSTITUTO FEDERAL.{0,10}BAHIA']),
    ("UFPB - Universidade Federal da Paraíba", [r'\bUFPB\b', r'FEDERAL DA PARA[IÍ]BA']),
    ("UEPB - Universidade Estadual da Paraíba", [r'\bUEPB\b', r'ESTADUAL DA PARA[IÍ]BA']),
    ("Universidade de Vassouras", [r'\bUNIVASSOURAS\b', r'\bUNIVASS\b', r'\bUV\b.{0,3}VASSOURAS', r'DE VASSOURAS']),
    ("UNIUBE - Universidade de Uberaba", [r'\bUNIUBE\b', r'DE UBERABA']),
    ("UFMG - Universidade Federal de Minas Gerais", [r'\bUFMG\b', r'FEDERAL DE MINAS GERAIS']),
    ("UFSP - Universidade Federal de São Paulo", [r'^UNIVERSIDADE FEDERAL DE S[ÃA]O PAULO$']),
    ("Petrobras", [r'\bPETROBRAS\b', r'\bCENPES\b']),
    ("Universidade Tiradentes", [r'\bUNIT\b.{0,3}TIRADENTES', r'UNIVERSIDADE TIRADENTES']),
    ("UFMA - Universidade Federal do Maranhão", [r'\bUFMA\b', r'FEDERAL DO ?MARANH[ÃA]O']),
    ("IFAL - Instituto Federal de Alagoas", [r'\bIFAL\b']),
    ("UFGD - Universidade Federal da Grande Dourados", [r'\bUFGD\b']),
    ("UESC - Universidade Estadual de Santa Cruz", [r'\bUESC\b', r'ESTADUAL DE SANTA CRUZ']),
    ("IFB - Instituto Federal de Brasília", [r'\bIFB\b']),
]


def canonicalizar_instituicao(valor: str) -> str:
    if valor in ("NAN", "NONE", "-", "N/A", "", "NÃO RESPONDEU", "NAO RESPONDEU"):
        return "Não respondeu"
    for canonico, padroes in ALIASES_INSTITUICAO:
        for padrao in padroes:
            if re.search(padrao, valor):
                return canonico
    return valor.title()


# ==========================================================
# INSTITUIÇÃO -> ESTADO / REGIÃO
# ==========================================================
INSTITUICAO_LOCALIZACAO = {
    "UNIFESSPA - Universidade Federal do Sul e Sudeste do Pará": ("PA", "Norte"),
    "UFPA - Universidade Federal do Pará": ("PA", "Norte"),
    "UFRRJ - Universidade Federal Rural do Rio de Janeiro": ("RJ", "Sudeste"),
    "UFRJ - Universidade Federal do Rio de Janeiro": ("RJ", "Sudeste"),
    "UFU - Universidade Federal de Uberlândia": ("MG", "Sudeste"),
    "UFS - Universidade Federal de Sergipe": ("SE", "Nordeste"),
    "UFAL - Universidade Federal de Alagoas": ("AL", "Nordeste"),
    "IFTM - Instituto Federal do Triângulo Mineiro": ("MG", "Sudeste"),
    "UFTM - Universidade Federal do Triângulo Mineiro": ("MG", "Sudeste"),
    "IFES - Instituto Federal do Espírito Santo": ("ES", "Sudeste"),
    "UFES - Universidade Federal do Espírito Santo": ("ES", "Sudeste"),
    "UTFPR - Universidade Tecnológica Federal do Paraná": ("PR", "Sul"),
    "UFV - Universidade Federal de Viçosa": ("MG", "Sudeste"),
    "UFLA - Universidade Federal de Lavras": ("MG", "Sudeste"),
    "UFSCAR - Universidade Federal de São Carlos": ("SP", "Sudeste"),
    "UNIPAMPA - Universidade Federal do Pampa": ("RS", "Sul"),
    "UFMT - Universidade Federal de Mato Grosso": ("MT", "Centro-Oeste"),
    "UENF - Universidade Estadual do Norte Fluminense": ("RJ", "Sudeste"),
    "UEM - Universidade Estadual de Maringá": ("PR", "Sul"),
    "UNICAMP - Universidade Estadual de Campinas": ("SP", "Sudeste"),
    "UEG - Universidade Estadual de Goiás": ("GO", "Centro-Oeste"),
    "UFG - Universidade Federal de Goiás": ("GO", "Centro-Oeste"),
    "USP - Universidade de São Paulo": ("SP", "Sudeste"),
    "UFRN - Universidade Federal do Rio Grande do Norte": ("RN", "Nordeste"),
    "IFRN - Instituto Federal do Rio Grande do Norte": ("RN", "Nordeste"),
    "UFAM - Universidade Federal do Amazonas": ("AM", "Norte"),
    "UFSM - Universidade Federal de Santa Maria": ("RS", "Sul"),
    "UFCG - Universidade Federal de Campina Grande": ("PB", "Nordeste"),
    "UNESP - Universidade Estadual Paulista": ("SP", "Sudeste"),
    "IFSP - Instituto Federal de São Paulo": ("SP", "Sudeste"),
    "UFRPE - Universidade Federal Rural de Pernambuco": ("PE", "Nordeste"),
    "UFPE - Universidade Federal de Pernambuco": ("PE", "Nordeste"),
    "IFBA - Instituto Federal da Bahia": ("BA", "Nordeste"),
    "UFPB - Universidade Federal da Paraíba": ("PB", "Nordeste"),
    "UEPB - Universidade Estadual da Paraíba": ("PB", "Nordeste"),
    "Universidade de Vassouras": ("RJ", "Sudeste"),
    "UNIUBE - Universidade de Uberaba": ("MG", "Sudeste"),
    "UFMG - Universidade Federal de Minas Gerais": ("MG", "Sudeste"),
    "UFSP - Universidade Federal de São Paulo": ("SP", "Sudeste"),
    "Petrobras": ("RJ", "Sudeste"),
    "Universidade Tiradentes": ("SE", "Nordeste"),
    "UFMA - Universidade Federal do Maranhão": ("MA", "Nordeste"),
    "IFAL - Instituto Federal de Alagoas": ("AL", "Nordeste"),
    "UFGD - Universidade Federal da Grande Dourados": ("MS", "Centro-Oeste"),
    "UESC - Universidade Estadual de Santa Cruz": ("BA", "Nordeste"),
    "IFB - Instituto Federal de Brasília": ("DF", "Centro-Oeste"),
}


def localizar_instituicao(nome_canonico: str):
    return INSTITUICAO_LOCALIZACAO.get(nome_canonico, ("Não identificado", "Não identificado"))


# ==========================================================
# DEDUPLICAÇÃO DE PARTICIPANTES
# ==========================================================
def _normalizar_nome(nome: str) -> str:
    nome = str(nome).strip().upper()
    nome = ''.join(c for c in unicodedata.normalize('NFD', nome) if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', nome)


def _escolher_linha(grupo: pd.DataFrame) -> pd.Series:
    grupo = grupo.copy()
    grupo['_prio'] = (grupo['Inscrição'] == 'Aprovado').astype(int)
    grupo['_completude'] = grupo.notna().sum(axis=1)
    grupo = grupo.sort_values(['_prio', '_completude'], ascending=[False, False])
    return grupo.iloc[0].drop(labels=['_prio', '_completude'])


def deduplicar_participantes(df: pd.DataFrame):
    if "Nome" not in df.columns:
        return df, df.iloc[0:0]

    df = df.copy()
    df['_chave_nome'] = df['Nome'].apply(_normalizar_nome)
    duplicados = df[df['_chave_nome'].duplicated(keep=False)].sort_values('_chave_nome').drop(columns=['_chave_nome'])
    dedup = df.groupby('_chave_nome', group_keys=False).apply(_escolher_linha)
    dedup = dedup.drop(columns=['_chave_nome'], errors='ignore').reset_index(drop=True)
    return dedup, duplicados


# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================
st.set_page_config(
    page_title="Dashboard ENEMP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1e3a8a, #2563eb, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-title { color: #64748b; font-size: 1rem; margin-top: -10px; margin-bottom: 25px; }
    .metric-card {
        background: #ffffff; border-radius: 14px; padding: 18px 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06); border-left: 6px solid #2563eb;
    }
    .metric-card h4 { margin: 0; color: #475569; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-card p { margin: 6px 0 0 0; font-size: 2rem; font-weight: 700; color: #1e293b; }
    div[data-testid="stMetric"] { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px; }
</style>
""", unsafe_allow_html=True)


def card(titulo, valor, cor="#2563eb"):
    st.markdown(f"""
        <div class="metric-card" style="border-left-color:{cor};">
            <h4>{titulo}</h4>
            <p>{valor}</p>
        </div>
    """, unsafe_allow_html=True)


@st.cache_data(show_spinner="Carregando dados...")
def carregar_dados(caminho_ou_arquivo):
    return pd.read_excel(caminho_ou_arquivo)


# ==========================================================
# MÉTRICAS — PARTICIPANTES
# ==========================================================
def analisar_instituicoes(df: pd.DataFrame, col="Instituição") -> dict:
    if col not in df.columns or len(df) == 0:
        return {"contagem": pd.Series(dtype=int), "nao_informaram": 0, "informaram": 0,
                "distintas": 0, "top": pd.Series(dtype=int), "total": len(df)}

    inst_bruto = df[col].astype(str).str.strip().str.upper().str.replace(r"\s+", " ", regex=True)
    inst_canon = inst_bruto.apply(canonicalizar_instituicao)

    contagem = inst_canon.value_counts()
    nao_informaram = int(contagem.get("Não respondeu", 0))
    informaram = len(df) - nao_informaram
    distintas = contagem.drop("Não respondeu", errors="ignore").shape[0]
    top = contagem.drop("Não respondeu", errors="ignore").head(15)

    return {"contagem": contagem, "nao_informaram": nao_informaram, "informaram": informaram,
            "distintas": distintas, "top": top, "total": len(df)}


@st.cache_data
def calcular_metricas_participantes(dados: pd.DataFrame, cache_ver: int = CACHE_VERSION):
    if "Inscrição" not in dados.columns:
        st.error("A coluna 'Inscrição' não foi encontrada na planilha de participantes.")
        st.stop()

    dados_dedup, duplicados_detectados = deduplicar_participantes(dados)

    pendentes = dados_dedup[dados_dedup["Inscrição"] == "Pendente"].reset_index(drop=True)
    aprovados = dados_dedup[dados_dedup["Inscrição"] == "Aprovado"].reset_index(drop=True)

    formacao = aprovados["Formação acadêmica"] if "Formação acadêmica" in aprovados.columns else pd.Series(dtype=str)
    ensino_medio = aprovados[formacao == "Ensino médio completo"]
    graduados    = aprovados[formacao == "Graduação completa"]
    mestres      = aprovados[formacao == "Mestrado completo"]
    doutores     = aprovados[formacao == "Doutorado completo"]
    nao_resp     = aprovados[formacao.isna()]

    col_rev = "Possui disponibilidade para atuar como revisor (participantes com mestrado ou doutorado)?"
    revisores = aprovados[aprovados[col_rev].astype(str).str.contains("Sim", na=False)] if col_rev in aprovados.columns else pd.DataFrame()

    inst_todos = analisar_instituicoes(dados_dedup)
    inst_aprovados = analisar_instituicoes(aprovados)

    return {
        "dados_originais": dados, "dados_dedup": dados_dedup, "duplicados_detectados": duplicados_detectados,
        "inscricoes": len(pendentes) + len(aprovados), "pendentes": pendentes, "aprovados": aprovados,
        "ensino_medio": ensino_medio, "graduados": graduados, "mestres": mestres, "doutores": doutores,
        "nao_responderam": nao_resp, "revisores": revisores, "inst_todos": inst_todos, "inst_aprovados": inst_aprovados,
    }


def pagina_participantes(dados: pd.DataFrame):
    m = calcular_metricas_participantes(dados)

    qtd_duplicados = len(m["duplicados_detectados"])
    if qtd_duplicados > 0:
        st.warning(
            f"⚠️ Foram detectadas **{qtd_duplicados} linhas** pertencentes a pessoas com o mesmo nome "
            f"(inscrições repetidas). Elas foram unificadas nos indicadores abaixo — quando a pessoa tinha "
            f"uma inscrição 'Aprovado' entre as duplicatas, essa foi a mantida. Confira a aba "
            f"**'⚠️ Duplicados detectados'** mais abaixo, pois nomes iguais por coincidência (pessoas "
            f"diferentes) também apareceriam aqui."
        )

    st.subheader("📌 Indicadores Gerais")
    c1, c2, c3, c4 = st.columns(4)
    with c1: card("Total de Inscrições", m["inscricoes"], "#2563eb")
    with c2: card("Pendentes", len(m["pendentes"]), "#f59e0b")
    with c3: card("Aprovados", len(m["aprovados"]), "#16a34a")
    with c4: card("Aceitaram ser revisor", len(m["revisores"]), "#9333ea")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🎓 Formação Acadêmica (Aprovados)")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: card("Ensino Médio Completo", len(m["ensino_medio"]), "#0ea5e9")
    with c2: card("Graduação Completa", len(m["graduados"]), "#22c55e")
    with c3: card("Mestrado Completo", len(m["mestres"]), "#eab308")
    with c4: card("Doutorado Completo", len(m["doutores"]), "#ef4444")
    with c5: card("Não Responderam", len(m["nao_responderam"]), "#64748b")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🏫 Instituições dos Participantes")
    st.caption("Nomes de instituição unificados: siglas, nomes por extenso, campus e maiúsc./minúsc. contam juntos.")
    aba_todos, aba_aprov = st.tabs(["📋 Todos os Inscritos", "✅ Somente Aprovados"])

    def render_instituicoes(bloco, chave):
        c1, c2, c3 = st.columns(3)
        with c1: card("Instituições Distintas", bloco["distintas"], "#2563eb")
        with c2: card("Informaram a instituição", bloco["informaram"], "#16a34a")
        with c3: card("Não informaram", bloco["nao_informaram"], "#94a3b8")
        st.markdown("<br>", unsafe_allow_html=True)
        if len(bloco["top"]) > 0:
            df_top = bloco["top"].reset_index(); df_top.columns = ["Instituição", "Quantidade"]
            fig = px.bar(df_top.sort_values("Quantidade"), x="Quantidade", y="Instituição", orientation="h",
                         text="Quantidade", color="Quantidade", color_continuous_scale="Blues")
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False, coloraxis_showscale=False, xaxis_title="Nº de participantes",
                               yaxis_title="", height=500)
            st.plotly_chart(fig, use_container_width=True, key=f"grafico_inst_{chave}")
        with st.expander("📋 Ver contagem completa de todas as instituições"):
            df_all = bloco["contagem"].reset_index(); df_all.columns = ["Instituição", "Quantidade"]
            st.dataframe(df_all, use_container_width=True, height=400)

    with aba_todos: render_instituicoes(m["inst_todos"], "todos")
    with aba_aprov: render_instituicoes(m["inst_aprovados"], "aprovados")

    st.markdown("<br>", unsafe_allow_html=True)
    col_esq, col_dir = st.columns(2)
    with col_esq:
        st.subheader("📈 Status das Inscrições")
        df_status = pd.DataFrame({"Status": ["Aprovados", "Pendentes"], "Quantidade": [len(m["aprovados"]), len(m["pendentes"])]})
        fig_pie = px.pie(df_status, names="Status", values="Quantidade", color="Status",
                          color_discrete_map={"Aprovados": "#16a34a", "Pendentes": "#f59e0b"}, hole=0.5)
        fig_pie.update_traces(textinfo="percent+label", textfont_size=14)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_dir:
        st.subheader("📚 Distribuição por Formação")
        df_form = pd.DataFrame({
            "Formação": ["Ensino Médio Completo", "Graduação Completa", "Mestrado Completo", "Doutorado Completo", "Não respondeu"],
            "Quantidade": [len(m["ensino_medio"]), len(m["graduados"]), len(m["mestres"]), len(m["doutores"]), len(m["nao_responderam"])]
        })
        fig_bar = px.bar(df_form, x="Formação", y="Quantidade", color="Formação",
                          color_discrete_sequence=px.colors.qualitative.Bold, text="Quantidade")
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(showlegend=False, yaxis_title="Qtd.", xaxis_title="")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("🧑‍🏫 Disponibilidade como Revisor")
    nao_rev = len(m["aprovados"]) - len(m["revisores"])
    df_rev = pd.DataFrame({"Disponibilidade": ["Sim", "Não / Não respondeu"], "Quantidade": [len(m["revisores"]), nao_rev]})
    fig_rev = px.bar(df_rev, x="Disponibilidade", y="Quantidade", color="Disponibilidade",
                      color_discrete_map={"Sim": "#9333ea", "Não / Não respondeu": "#cbd5e1"}, text="Quantidade")
    fig_rev.update_traces(textposition="outside")
    fig_rev.update_layout(showlegend=False, yaxis_title="Qtd.")
    st.plotly_chart(fig_rev, use_container_width=True)

    st.subheader("🗂️ Explorar Dados")
    a1, a2, a3, a4, a5 = st.tabs(["✅ Aprovados", "⏳ Pendentes", "🧑‍🏫 Revisores", "📄 Todos (sem duplicados)", "⚠️ Duplicados detectados"])
    with a1: st.caption(f"Total: {len(m['aprovados'])}"); st.dataframe(m["aprovados"], use_container_width=True, height=400)
    with a2: st.caption(f"Total: {len(m['pendentes'])}"); st.dataframe(m["pendentes"], use_container_width=True, height=400)
    with a3: st.caption(f"Total: {len(m['revisores'])}"); st.dataframe(m["revisores"], use_container_width=True, height=400)
    with a4: st.caption(f"Total: {len(m['dados_dedup'])} (de {len(m['dados_originais'])} linhas originais)"); st.dataframe(m["dados_dedup"], use_container_width=True, height=400)
    with a5: st.caption(f"{len(m['duplicados_detectados'])} linhas — revise coincidências de nome"); st.dataframe(m["duplicados_detectados"], use_container_width=True, height=400)

    st.sidebar.markdown("---")
    st.sidebar.subheader("⬇️ Exportar Participantes")
    st.sidebar.download_button("Baixar Aprovados (CSV)", m["aprovados"].to_csv(index=False).encode("utf-8-sig"), "aprovados.csv", "text/csv")
    if len(m["revisores"]):
        st.sidebar.download_button("Baixar Revisores (CSV)", m["revisores"].to_csv(index=False).encode("utf-8-sig"), "revisores.csv", "text/csv")

    return m


# ==========================================================
# MÉTRICAS — TRABALHOS / RESULTADOS
# ==========================================================
def _normalizar_formato_apresentacao(valor) -> str:
    if pd.isna(valor):
        return ""
    texto = unicodedata.normalize("NFKD", str(valor)).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", texto.strip().upper())


def _explodir_formato_apresentacao(serie: pd.Series) -> pd.Series:
    itens = []
    for valor in serie.dropna():
        for parte in re.split(r"[;,]", str(valor)):
            parte = parte.strip()
            if parte:
                itens.append(parte)
    return pd.Series(itens)


def _trabalhos_por_formato(df: pd.DataFrame, formato: str) -> pd.DataFrame:
    if "Formato de apresentação desejado" not in df.columns:
        return df.iloc[0:0].copy()
    alvo = _normalizar_formato_apresentacao(formato)
    mask = df["Formato de apresentação desejado"].apply(
        lambda valor: alvo in {_normalizar_formato_apresentacao(p) for p in re.split(r"[;,]", str(valor))} if not pd.isna(valor) else False
    )
    return df.loc[mask].copy()


def _trabalhos_student(df: pd.DataFrame) -> pd.DataFrame:
    if "Categoria de student contest" not in df.columns:
        return df.iloc[0:0].copy()
    coluna = df["Categoria de student contest"].astype("string").str.strip()
    return df.loc[coluna.notna() & coluna.ne("")].copy()


def _colunas_trabalhos_para_exibicao(df: pd.DataFrame) -> list[str]:
    preferidas = [
        "Título", "Titulo", "Título do Trabalho", "Titulo do Trabalho",
        "Autores", "Autor(es)", "Autor",
        "Instituição (apresentador)", "Instituição",
        "Formato de apresentação desejado", "Categoria de student contest",
        "Área Temática", "Situação"
    ]
    presentes = [c for c in preferidas if c in df.columns]
    if presentes:
        return presentes
    return list(df.columns)


def _explodir_autores(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for _, linha in df.iterrows():
        autores = [a.strip() for a in str(linha.get("Autores", "")).split(",") if a.strip()]
        for autor in autores:
            linhas.append({
                "_autor_norm": _normalizar_nome(autor),
                "Autor": autor,
                "Número": linha.get("Número"),
                "Título": linha.get("Título"),
                "Situação": linha.get("Situação"),
            })
    return pd.DataFrame(linhas)


def analisar_autores_repetidos(df: pd.DataFrame) -> pd.DataFrame:
    if "Autores" not in df.columns:
        return pd.DataFrame(columns=["Autor", "Qtd. de Trabalhos", "Títulos"])

    ex = _explodir_autores(df)
    if ex.empty:
        return pd.DataFrame(columns=["Autor", "Qtd. de Trabalhos", "Títulos"])

    nome_exibicao = ex.groupby("_autor_norm")["Autor"].agg(lambda s: s.value_counts().idxmax())

    agregado = ex.groupby("_autor_norm").agg(
        qtd_trabalhos=("Número", "nunique"),
        titulos=("Título", lambda s: "; ".join(sorted(set(str(t) for t in s))))
    )
    agregado["Autor"] = nome_exibicao
    agregado = agregado[agregado["qtd_trabalhos"] > 1].sort_values("qtd_trabalhos", ascending=False)
    agregado = agregado.reset_index(drop=True)[["Autor", "qtd_trabalhos", "titulos"]]
    agregado.columns = ["Autor", "Qtd. de Trabalhos", "Títulos"]
    return agregado


def analisar_autor_principal(df: pd.DataFrame) -> pd.DataFrame:
    if "Autores" not in df.columns:
        return pd.DataFrame(columns=["Autor Principal", "Qtd. de Trabalhos", "Títulos"])

    linhas = []
    for _, linha in df.iterrows():
        autores = [a.strip() for a in str(linha.get("Autores", "")).split(",") if a.strip()]
        if not autores:
            continue
        primeiro = autores[0]
        linhas.append({
            "_autor_norm": _normalizar_nome(primeiro),
            "Autor": primeiro,
            "Número": linha.get("Número"),
            "Título": linha.get("Título"),
        })
    ex = pd.DataFrame(linhas)
    if ex.empty:
        return pd.DataFrame(columns=["Autor Principal", "Qtd. de Trabalhos", "Títulos"])

    nome_exibicao = ex.groupby("_autor_norm")["Autor"].agg(lambda s: s.value_counts().idxmax())
    agregado = ex.groupby("_autor_norm").agg(
        qtd_trabalhos=("Número", "nunique"),
        titulos=("Título", lambda s: "; ".join(sorted(set(str(t) for t in s))))
    )
    agregado["Autor"] = nome_exibicao
    agregado = agregado.sort_values("qtd_trabalhos", ascending=False).reset_index(drop=True)
    agregado = agregado[["Autor", "qtd_trabalhos", "titulos"]]
    agregado.columns = ["Autor Principal", "Qtd. de Trabalhos", "Títulos
