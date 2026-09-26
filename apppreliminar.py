import re
import unicodedata
from difflib import SequenceMatcher
import streamlit as st
import pandas as pd
import plotly.express as px

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
# ----------------------------------------------------------
# Não existe coluna de estado/região nas planilhas: mapeamos
# a partir do nome canônico da instituição (mesmo dicionário
# de aliases acima). Instituições fora dessa lista aparecem
# como "Não identificado".
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
# DEDUPLICAÇÃO DE PARTICIPANTES (mesma pessoa inscrita 2x)
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
    """Retorna (df_sem_duplicados, df_duplicados_detectados)."""
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
def calcular_metricas_participantes(dados: pd.DataFrame):
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
    """Normaliza o texto do formato para facilitar filtros (Pôster/Oral)."""
    if pd.isna(valor):
        return ""
    texto = unicodedata.normalize("NFKD", str(valor)).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", texto.strip().upper())


def _explodir_formato_apresentacao(serie: pd.Series) -> pd.Series:
    """'Oral; Pôster' -> conta 1 para 'Oral' e 1 para 'Pôster' (multi-seleção)."""
    itens = []
    for valor in serie.dropna():
        for parte in re.split(r"[;,]", str(valor)):
            parte = parte.strip()
            if parte:
                itens.append(parte)
    return pd.Series(itens)


def _trabalhos_por_formato(df: pd.DataFrame, formato: str) -> pd.DataFrame:
    """Retorna os trabalhos cujo formato de apresentação contém o formato solicitado."""
    if "Formato de apresentação desejado" not in df.columns:
        return df.iloc[0:0].copy()
    alvo = _normalizar_formato_apresentacao(formato)
    mask = df["Formato de apresentação desejado"].apply(
        lambda valor: alvo in {_normalizar_formato_apresentacao(p) for p in re.split(r"[;,]", str(valor))} if not pd.isna(valor) else False
    )
    return df.loc[mask].copy()


def _trabalhos_student(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna os trabalhos com categoria de Student Contest preenchida."""
    if "Categoria de student contest" not in df.columns:
        return df.iloc[0:0].copy()
    coluna = df["Categoria de student contest"].astype("string").str.strip()
    return df.loc[coluna.notna() & coluna.ne("")].copy()


def _colunas_trabalhos_para_exibicao(df: pd.DataFrame) -> list[str]:
    """Seleciona as colunas mais úteis para a lista interativa de trabalhos."""
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
    """Separa a coluna 'Autores' (nomes separados por vírgula) em uma linha por
    autor x trabalho. Usa o mesmo tipo de normalização (maiúsc./acento/espaço)
    da deduplicação de participantes, para não contar 'José Silva' e 'Jose Silva'
    como pessoas diferentes."""
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
    """Retorna uma linha por autor distinto (nome normalizado) que aparece em
    mais de um trabalho, com a quantidade de trabalhos e os títulos."""
    if "Autores" not in df.columns:
        return pd.DataFrame(columns=["Autor", "Qtd. de Trabalhos", "Títulos"])

    ex = _explodir_autores(df)
    if ex.empty:
        return pd.DataFrame(columns=["Autor", "Qtd. de Trabalhos", "Títulos"])

    # nome de exibição = variante mais frequente daquele nome normalizado
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
    """Considera só o PRIMEIRO nome listado em 'Autores' de cada trabalho —
    geralmente o autor principal (aluno/pesquisador que de fato desenvolveu o
    trabalho), diferente da lista de coautores (que costuma incluir
    orientadores/coordenadores repetidos em vários trabalhos do grupo).
    Retorna uma linha por autor principal distinto, com a quantidade de
    trabalhos em que aparece como primeiro autor."""
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
    agregado.columns = ["Autor Principal", "Qtd. de Trabalhos", "Títulos"]
    return agregado


def _normalizar_titulo(titulo: str) -> str:
    """Normaliza títulos para comparação entre versões do mesmo trabalho.

    Além de acentos/pontuação, corrige algumas grafias químicas recorrentes.
    A normalização bilíngue é feita separadamente em _tokens_titulo_bilingue().
    """
    titulo = str(titulo).strip().upper()
    titulo = ''.join(
        c for c in unicodedata.normalize('NFD', titulo)
        if unicodedata.category(c) != 'Mn'
    )

    # Grafia recorrente na base: AIMCM-48 x AlMCM-48.
    titulo = re.sub(r'\bAI(?=MCM\s*-?\s*\d+)', 'AL', titulo)

    titulo = re.sub(r'[^A-Z0-9\s]', ' ', titulo)
    return re.sub(r'\s+', ' ', titulo).strip()


# Termos acadêmicos que aparecem frequentemente em títulos bilíngues da base.
# O objetivo não é traduzir o título para exibição, mas colocar palavras
# equivalentes em um mesmo espaço de comparação.
TRADUCAO_TITULO = {
    # estruturas acadêmicas
    "ANALISE": "ANALYSIS", "ANALYSIS": "ANALYSIS",
    "COMPARATIVA": "COMPARATIVE", "COMPARATIVE": "COMPARATIVE",
    "AVALIACAO": "EVALUATION", "EVALUATION": "EVALUATION",
    "ESTUDO": "STUDY", "STUDY": "STUDY",
    "EFEITO": "EFFECT", "EFEITOS": "EFFECTS", "EFFECT": "EFFECT", "EFFECTS": "EFFECTS",
    "MODELAGEM": "MODELING", "MODELAGEM": "MODELING", "MODELING": "MODELING",
    "DESENVOLVIMENTO": "DEVELOPMENT", "DEVELOPMENT": "DEVELOPMENT",
    "CARACTERIZACAO": "CHARACTERIZATION", "CHARACTERIZATION": "CHARACTERIZATION",
    "DETERMINACAO": "DETERMINATION", "DETERMINATION": "DETERMINATION",
    "INVESTIGACAO": "INVESTIGATION", "INVESTIGATION": "INVESTIGATION",
    "APLICACAO": "APPLICATION", "APPLICATION": "APPLICATION",
    "UTILIZACAO": "USE", "USO": "USE", "USE": "USE",
    "DESCRICAO": "DESCRIPTION", "DESCRIPTION": "DESCRIPTION",

    # fenômeno / processo
    "DINAMICA": "DYNAMICS", "DYNAMICS": "DYNAMICS",
    "SEDIMENTACAO": "SEDIMENTATION", "SEDIMENTATION": "SEDIMENTATION",
    "SEDIMENTACAO": "SEDIMENTATION",
    "PARTICULA": "PARTICLE", "PARTICULAS": "PARTICLES",
    "PARTICLE": "PARTICLE", "PARTICLES": "PARTICLES",
    "FLUIDO": "FLUID", "FLUIDOS": "FLUIDS", "FLUID": "FLUID", "FLUIDS": "FLUIDS",
    "NEWTONIANOS": "NEWTONIAN", "NEWTONIANO": "NEWTONIAN", "NEWTONIAN": "NEWTONIAN",
    "NAO": "NON", "NON": "NON",
    "DIFERENTES": "DIFFERENT", "DIFFERENTES": "DIFFERENT", "DIFFERENT": "DIFFERENT",
    "CONDICOES": "CONDITIONS", "CONDITION": "CONDITIONS", "CONDITIONS": "CONDITIONS",
    "TERMICA": "THERMAL", "TERMICAS": "THERMAL", "TERMICO": "THERMAL", "THERMAL": "THERMAL",
    "PRESSAO": "PRESSURE", "PRESSURE": "PRESSURE",
    "TEMPERATURA": "TEMPERATURE", "TEMPERATURE": "TEMPERATURE",
    "SOB": "UNDER", "UNDER": "UNDER",
    "DIFERENTES": "DIFFERENT", "DIFFERENT": "DIFFERENT",

    # materiais / técnicas
    "CALCITA": "CALCITE", "CALCITE": "CALCITE",
    "AGUA": "WATER", "WATER": "WATER",
    "TRATAMENTO": "TREATMENT", "TREATMENT": "TREATMENT",
    "REJEITO": "TAILINGS", "TAILINGS": "TAILINGS",
    "FOSFATICO": "PHOSPHATE", "PHOSPHATE": "PHOSPHATE",
    "MODIFICADO": "MODIFIED", "MODIFIED": "MODIFIED",
    "DIFERENTES": "DIFFERENT", "DIFFERENT": "DIFFERENT",

    # palavras funcionais que ajudam a equivalência, mas têm pouco peso
    "COM": "WITH", "WITH": "WITH",
    "EM": "IN", "IN": "IN",
    "DE": "OF", "OF": "OF",
    "E": "AND", "AND": "AND",
    "NO": "IN", "NA": "IN", "DOS": "OF", "DAS": "OF",
    "A": "THE", "O": "THE", "OS": "THE", "AS": "THE",
    "THE": "THE",
    "PARA": "FOR", "FOR": "FOR",
    "SOBRE": "ON", "ON": "ON",
}

# Palavras de estrutura muito comuns têm pouco poder discriminatório.
_STOPWORDS_TITULO = {
    "THE", "OF", "AND", "IN", "ON", "WITH", "FOR", "TO", "A", "AN", "UNDER",
}


def _tokens_titulo_bilingue(titulo: str) -> list[str]:
    """Converte tokens PT/EN equivalentes para uma representação comum."""
    normalizado = _normalizar_titulo(titulo)
    tokens = []
    for token in normalizado.split():
        canon = TRADUCAO_TITULO.get(token, token)
        # Reduz plurais simples para melhorar equivalência PT/EN.
        if canon.endswith('S') and len(canon) > 5:
            canon = canon[:-1]
        if canon not in _STOPWORDS_TITULO:
            tokens.append(canon)
    return tokens


def _assinatura_titulo_bilingue(titulo: str) -> str:
    return ' '.join(sorted(_tokens_titulo_bilingue(titulo)))


def _autor_principal_normalizado(linha: pd.Series) -> str:
    autores = str(linha.get("Autores", "")).strip()
    primeiro_autor = autores.split(",")[0].strip() if autores else ""
    return _normalizar_nome(primeiro_autor)


def _similaridade_titulos(t1: str, t2: str) -> float:
    """Similaridade híbrida para títulos iguais, quase iguais ou bilíngues."""
    if not t1 or not t2:
        return 0.0
    if t1 == t2:
        return 1.0

    # Similaridade textual direta para pequenas diferenças de digitação.
    direta = SequenceMatcher(None, t1, t2).ratio()

    # Similaridade por tokens traduzidos PT/EN.
    tok1 = set(_tokens_titulo_bilingue(t1))
    tok2 = set(_tokens_titulo_bilingue(t2))
    if not tok1 or not tok2:
        return direta
    jaccard = len(tok1 & tok2) / len(tok1 | tok2)

    # Cobertura: útil quando uma versão possui pequenas palavras adicionais.
    cobertura = len(tok1 & tok2) / min(len(tok1), len(tok2))

    # A equivalência bilíngue exige bastante conteúdo em comum, não apenas
    # palavras genéricas como "analysis", "effects" ou "study".
    conteudo_comum = tok1 & tok2
    informativas = conteudo_comum - {"ANALYSIS", "COMPARATIVE", "EVALUATION", "STUDY", "EFFECT", "EFFECTS"}
    cobertura_informativa = (
        len(informativas) / max(1, min(len(tok1 - _STOPWORDS_TITULO), len(tok2 - _STOPWORDS_TITULO)))
    )

    return max(direta, jaccard * 0.85 + cobertura * 0.15, cobertura_informativa * 0.90)


def _mesmo_trabalho(linha_a: pd.Series, linha_b: pd.Series) -> bool:
    """Decide se duas linhas representam o mesmo trabalho.

    Exige o mesmo primeiro autor. Para o título, aceita igualdade normalizada,
    pequenas diferenças textuais ou equivalência bilíngue PT/EN com alta
    sobreposição de termos informativos.
    """
    autor_a = _autor_principal_normalizado(linha_a)
    autor_b = _autor_principal_normalizado(linha_b)
    if not autor_a or autor_a != autor_b:
        return False

    titulo_a = _normalizar_titulo(linha_a.get("Título", ""))
    titulo_b = _normalizar_titulo(linha_b.get("Título", ""))
    if not titulo_a or not titulo_b:
        return False

    if titulo_a == titulo_b:
        return True

    direta = SequenceMatcher(None, titulo_a, titulo_b).ratio()
    tok_a = set(_tokens_titulo_bilingue(titulo_a))
    tok_b = set(_tokens_titulo_bilingue(titulo_b))
    comum = tok_a & tok_b
    uniao = tok_a | tok_b
    jaccard = len(comum) / len(uniao) if uniao else 0.0

    informativas = comum - {"ANALYSIS", "COMPARATIVE", "EVALUATION", "STUDY", "EFFECT", "EFFECTS"}
    min_informativas = max(1, min(len(tok_a - _STOPWORDS_TITULO), len(tok_b - _STOPWORDS_TITULO)))
    cobertura_informativa = len(informativas) / min_informativas

    # Pequenas diferenças de grafia.
    if direta >= 0.94:
        return True

    # Versões PT/EN: requer forte correspondência de termos informativos.
    # Evita que apenas o tema geral seja suficiente para fundir trabalhos.
    if cobertura_informativa >= 0.80 and jaccard >= 0.55:
        return True

    return False


def _chave_trabalho(linha: pd.Series) -> str:
    """Chave para títulos que ficam idênticos após normalização."""
    titulo = _normalizar_titulo(linha.get("Título", ""))
    autor = _autor_principal_normalizado(linha)
    return f"{titulo}|||{autor}"


def deduplicar_trabalhos(df: pd.DataFrame):
    """Une versões do mesmo trabalho, inclusive versões PT/EN.

    A comparação ocorre somente entre registros do mesmo primeiro autor.
    Primeiro usa igualdade da chave normalizada; depois procura equivalência
    textual ou bilíngue. Assim, um resumo em português e seu trabalho completo
    em inglês podem ser um único trabalho, enquanto dois trabalhos apenas
    relacionados pelo assunto permanecem separados.
    """
    if df.empty or "Título" not in df.columns:
        return df.copy(), df.iloc[0:0].copy()

    temp = df.copy().reset_index(drop=True)
    temp["_titulo_norm"] = temp["Título"].apply(_normalizar_titulo)
    temp["_autor_principal_norm"] = temp.apply(_autor_principal_normalizado, axis=1)

    candidatos = temp[
        temp["_titulo_norm"].ne("") & temp["_autor_principal_norm"].ne("")
    ].copy()
    sem_chave = temp[
        temp["_titulo_norm"].eq("") | temp["_autor_principal_norm"].eq("")
    ].copy()

    if candidatos.empty:
        limpo = temp.drop(columns=["_titulo_norm", "_autor_principal_norm"], errors="ignore")
        return limpo, temp.iloc[0:0].drop(columns=["_titulo_norm", "_autor_principal_norm"], errors="ignore")

    n = len(candidatos)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    # Agrupamento exato após normalização.
    grupos_chave = {}
    for pos, (_, row) in enumerate(candidatos.iterrows()):
        chave = f"{row['_titulo_norm']}|||{row['_autor_principal_norm']}"
        grupos_chave.setdefault(chave, []).append(pos)
    for indices in grupos_chave.values():
        for pos in indices[1:]:
            union(indices[0], pos)

    # Comparação PT/EN e pequenas variações, sempre dentro do mesmo autor.
    for _, grupo in candidatos.groupby("_autor_principal_norm", sort=False):
        indices = list(grupo.index)
        for i in range(len(indices)):
            pos_i = candidatos.index.get_loc(indices[i])
            for j in range(i + 1, len(indices)):
                pos_j = candidatos.index.get_loc(indices[j])
                if _mesmo_trabalho(candidatos.loc[indices[i]], candidatos.loc[indices[j]]):
                    union(pos_i, pos_j)

    candidatos["_grupo_trabalho"] = [find(i) for i in range(n)]

    def escolher_linha(grupo):
        g = grupo.copy()
        g["_prio_modalidade"] = (
            g["modalidade"].astype(str)
            .str.contains("Trabalho Completo", case=False, na=False)
            .astype(int)
            if "modalidade" in g.columns else 0
        )
        g["_prio_situacao"] = (
            g["Situação"].astype(str).eq("Aprovado").astype(int)
            if "Situação" in g.columns else 0
        )
        g["_completude"] = g.notna().sum(axis=1)
        g = g.sort_values(
            ["_prio_modalidade", "_prio_situacao", "_completude"],
            ascending=[False, False, False]
        )
        return g.iloc[0]

    grupos = candidatos.groupby("_grupo_trabalho", sort=False)
    unicos = grupos.apply(escolher_linha).reset_index(drop=True)

    tamanhos = grupos.size()
    grupos_duplicados = set(tamanhos[tamanhos > 1].index)
    duplicados = candidatos[candidatos["_grupo_trabalho"].isin(grupos_duplicados)].copy()

    unicos = pd.concat([unicos, sem_chave], ignore_index=True)
    colunas_aux = ["_titulo_norm", "_autor_principal_norm", "_grupo_trabalho"]
    unicos = unicos.drop(columns=colunas_aux, errors="ignore")
    duplicados = duplicados.drop(columns=colunas_aux, errors="ignore")

    return unicos.reset_index(drop=True), duplicados.reset_index(drop=True)


@st.cache_data
def calcular_metricas_resultados(dados_resultados: pd.DataFrame, dados_participantes_dedup: pd.DataFrame | None):
    df_original = dados_resultados.copy()

    # ---- deduplicação de versões do mesmo trabalho ----
    # Resumo + Trabalho Completo do mesmo trabalho passam a contar como 1 trabalho.
    df, trabalhos_duplicados = deduplicar_trabalhos(df_original)

    # ---- cruzamento com participantes via e-mail do apresentador ----
    if dados_participantes_dedup is not None and "E-mail" in dados_participantes_dedup.columns:
        part = dados_participantes_dedup.copy()
        part["_email"] = part["E-mail"].astype(str).str.strip().str.lower()
        df["_email"] = df["Email dos apresentadores"].astype(str).str.strip().str.lower()
        df = df.merge(
            part[["_email", "Instituição", "Formação acadêmica"]].rename(
                columns={"Instituição": "_inst_participante", "Formação acadêmica": "_formacao_participante"}
            ),
            on="_email", how="left"
        )
    else:
        df["_inst_participante"] = pd.NA
        df["_formacao_participante"] = pd.NA

    # ---- modalidade: resumo x trabalho completo ----
    modalidade = df["modalidade"].astype(str)
    resumos = df[modalidade.str.contains("Resumo", na=False)]
    completos = df[modalidade.str.contains("Trabalho Completo", na=False)]

    # ---- situação / aceite ----
    aceitos = df[df["Situação"] == "Aprovado"] if "Situação" in df.columns else pd.DataFrame()
    situacao_contagem = df["Situação"].value_counts(dropna=False) if "Situação" in df.columns else pd.Series(dtype=int)

    # ---- instituição: prioriza a coluna do próprio resultado, completa com a do participante ----
    if "Instituição (apresentador)" in df.columns:
        inst_final = df["Instituição (apresentador)"].fillna(df["_inst_participante"])
    else:
        inst_final = df["_inst_participante"]
    inst_final = inst_final.fillna("Não respondeu")
    inst_norm = inst_final.astype(str).str.strip().str.upper().str.replace(r"\s+", " ", regex=True)
    inst_canon = inst_norm.apply(canonicalizar_instituicao)
    inst_contagem = inst_canon.value_counts()
    inst_nao_identificado = int(inst_contagem.get("Não respondeu", 0)) + int(inst_contagem.get("Nan", 0))
    inst_top = inst_contagem.drop(["Não respondeu", "Nan"], errors="ignore").head(15)

    # ---- região / estado (a partir da instituição canonicalizada) ----
    localizacoes = inst_canon.apply(localizar_instituicao)
    estados = localizacoes.apply(lambda x: x[0])
    regioes = localizacoes.apply(lambda x: x[1])
    estado_contagem = estados[estados != "Não identificado"].value_counts()
    regiao_contagem = regioes[regioes != "Não identificado"].value_counts()

    # ---- formação do inscrito (via cruzamento com participantes) ----
    formacao_final = df["_formacao_participante"]
    grad = int((formacao_final == "Graduação completa").sum())
    mestrado = int((formacao_final == "Mestrado completo").sum())
    doutorado = int((formacao_final == "Doutorado completo").sum())
    ensino_medio = int((formacao_final == "Ensino médio completo").sum())
    formacao_nao_encontrada = int(formacao_final.isna().sum())

    # ---- student contest: categoria ----
    if "Categoria de student contest" in df.columns:
        student_col = df["Categoria de student contest"].astype("string").str.strip()
        student_contest_qtd = int(student_col.notna().sum() - student_col.eq("").sum())
        student_contest_cat = df.loc[student_col.notna() & student_col.ne(""), "Categoria de student contest"].value_counts()
    else:
        student_contest_qtd = 0
        student_contest_cat = pd.Series(dtype=int)

    # ---- formato de apresentação (pôster / oral) ----
    if "Formato de apresentação desejado" in df.columns:
        formatos_explodidos = _explodir_formato_apresentacao(df["Formato de apresentação desejado"])
        formato_contagem = formatos_explodidos.value_counts()
    else:
        formato_contagem = pd.Series(dtype=int)

    trabalhos_poster = _trabalhos_por_formato(df, "Pôster")
    trabalhos_oral = _trabalhos_por_formato(df, "Oral")
    trabalhos_student = _trabalhos_student(df)

    poster_qtd = len(trabalhos_poster)
    oral_qtd = len(trabalhos_oral)

    # ---- área temática ----
    area_tematica_contagem = df["Área Temática"].value_counts(dropna=False) if "Área Temática" in df.columns else pd.Series(dtype=int)

    # ---- autores com mais de um trabalho (coautores, incl. orientadores) ----
    autores_repetidos = analisar_autores_repetidos(df)
    autores_distintos = _explodir_autores(df)["_autor_norm"].nunique() if "Autores" in df.columns else 0

    # ---- autor principal (primeiro nome listado em 'Autores') ----
    autor_principal_todos = analisar_autor_principal(df)
    autores_principais_distintos = len(autor_principal_todos)
    autor_principal_repetido = autor_principal_todos[autor_principal_todos["Qtd. de Trabalhos"] > 1].reset_index(drop=True)

    return {
        "dados": df,
        "dados_originais": df_original,
        "trabalhos_duplicados": trabalhos_duplicados,
        "total_inscritos": len(df),
        "total_registros_originais": len(df_original),
        "total_duplicados_trabalho": len(trabalhos_duplicados),
        "resumos": resumos, "completos": completos,
        "aceitos": aceitos, "situacao_contagem": situacao_contagem,
        "inst_contagem": inst_contagem, "inst_top": inst_top, "inst_nao_identificado": inst_nao_identificado,
        "estado_contagem": estado_contagem, "regiao_contagem": regiao_contagem,
        "grad": grad, "mestrado": mestrado, "doutorado": doutorado,
        "ensino_medio": ensino_medio, "formacao_nao_encontrada": formacao_nao_encontrada,
        "student_contest_cat": student_contest_cat,
        "student_contest_qtd": student_contest_qtd,
        "formato_contagem": formato_contagem,
        "poster_qtd": poster_qtd,
        "oral_qtd": oral_qtd,
        "trabalhos_poster": trabalhos_poster,
        "trabalhos_oral": trabalhos_oral,
        "trabalhos_student": trabalhos_student,
        "area_tematica_contagem": area_tematica_contagem,
        "autores_repetidos": autores_repetidos,
        "autores_distintos": autores_distintos,
        "autores_principais_distintos": autores_principais_distintos,
        "autor_principal_repetido": autor_principal_repetido,
        "tem_cruzamento": dados_participantes_dedup is not None,
    }


def pagina_resultados(dados_resultados: pd.DataFrame, dados_participantes_dedup: pd.DataFrame | None, qtd_revisores: int | None):
    r = calcular_metricas_resultados(dados_resultados, dados_participantes_dedup)

    if not r["tem_cruzamento"]:
        st.info(
            "ℹ️ Envie também a planilha de **Participantes** na barra lateral para habilitar o cruzamento "
            "por e-mail (usado para completar Instituição, Formação do inscrito e Nº de revisores)."
        )

    if r["total_duplicados_trabalho"] > 0:
        st.info(
            f"🔄 **{r['total_duplicados_trabalho']} registros foram identificados como "
            f"versões duplicadas de trabalhos** (por exemplo, Resumo + Trabalho Completo). "
            f"Eles foram contabilizados como **um único trabalho** nos indicadores. "
            f"A versão de Trabalho Completo tem prioridade na representação."
        )

    st.subheader("📌 Indicadores Gerais")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: card("Trabalhos Únicos", r["total_inscritos"], "#2563eb")
    with c2:
        card("Pôster", r["poster_qtd"], "#0ea5e9")
        if st.button("📋 Ver trabalhos Pôster", key="abrir_trabalhos_poster", use_container_width=True):
            st.session_state["lista_trabalhos_aberta"] = "poster"
    with c3:
        card("Oral", r["oral_qtd"], "#f97316")
        if st.button("📋 Ver trabalhos Oral", key="abrir_trabalhos_oral", use_container_width=True):
            st.session_state["lista_trabalhos_aberta"] = "oral"
    with c4:
        card("Student", r["student_contest_qtd"], "#9333ea")
        if st.button("📋 Ver trabalhos Student", key="abrir_trabalhos_student", use_container_width=True):
            st.session_state["lista_trabalhos_aberta"] = "student"
    with c5: card("Trabalhos Aceitos", len(r["aceitos"]), "#16a34a")

    st.caption(
        "Clique em **Ver trabalhos** para abrir a lista correspondente. "
        "Os trabalhos são os mesmos considerados nos indicadores após a deduplicação."
    )

    tipo_aberto = st.session_state.get("lista_trabalhos_aberta")
    mapas_trabalhos = {
        "poster": ("📋 Trabalhos — Pôster", r["trabalhos_poster"]),
        "oral": ("📋 Trabalhos — Oral", r["trabalhos_oral"]),
        "student": ("📋 Trabalhos — Student Contest", r["trabalhos_student"]),
    }
    if tipo_aberto in mapas_trabalhos:
        titulo_lista, df_lista = mapas_trabalhos[tipo_aberto]
        with st.container(border=True):
            cab1, cab2 = st.columns([5, 1])
            with cab1:
                st.subheader(titulo_lista)
                st.caption(f"{len(df_lista)} trabalho(s)")
            with cab2:
                if st.button("✖ Fechar", key="fechar_lista_trabalhos", use_container_width=True):
                    st.session_state["lista_trabalhos_aberta"] = None
                    st.rerun()
            if len(df_lista) > 0:
                colunas_lista = _colunas_trabalhos_para_exibicao(df_lista)
                st.dataframe(
                    df_lista[colunas_lista].reset_index(drop=True),
                    use_container_width=True,
                    hide_index=True,
                    height=min(650, 120 + len(df_lista) * 42),
                )
            else:
                st.info("Nenhum trabalho encontrado para este indicador.")

    with st.expander("Ver detalhamento completo da Situação"):
        df_sit = r["situacao_contagem"].reset_index(); df_sit.columns = ["Situação", "Quantidade"]
        st.dataframe(df_sit, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🎓 Formação do Inscrito")
    st.caption("Obtida cruzando o e-mail do apresentador com a planilha de Participantes.")
    c1, c2, c3, c4 = st.columns(4)
    with c1: card("Graduação", r["grad"], "#22c55e")
    with c2: card("Mestrado", r["mestrado"], "#eab308")
    with c3: card("Doutorado", r["doutorado"], "#ef4444")
    with c4: card("Não encontrado / outro", r["ensino_medio"] + r["formacao_nao_encontrada"], "#94a3b8")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🏫 Instituições")
    c1, c2 = st.columns(2)
    with c1: card("Instituições Distintas", r["inst_contagem"].drop(["Não respondeu", "Nan"], errors="ignore").shape[0], "#2563eb")
    with c2: card("Não identificado", r["inst_nao_identificado"], "#94a3b8")
    if len(r["inst_top"]) > 0:
        df_top = r["inst_top"].reset_index(); df_top.columns = ["Instituição", "Quantidade"]
        fig = px.bar(df_top.sort_values("Quantidade"), x="Quantidade", y="Instituição", orientation="h",
                     text="Quantidade", color="Quantidade", color_continuous_scale="Blues")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, coloraxis_showscale=False, xaxis_title="Nº de trabalhos", yaxis_title="", height=500)
        st.plotly_chart(fig, use_container_width=True)
    with st.expander("📋 Ver contagem completa de todas as instituições"):
        df_all = r["inst_contagem"].reset_index(); df_all.columns = ["Instituição", "Quantidade"]
        st.dataframe(df_all, use_container_width=True, height=400)

    st.markdown("<br>", unsafe_allow_html=True)
    col_esq, col_dir = st.columns(2)
    with col_esq:
        st.subheader("🗺️ Regiões")
        if len(r["regiao_contagem"]) > 0:
            df_reg = r["regiao_contagem"].reset_index(); df_reg.columns = ["Região", "Quantidade"]
            fig = px.pie(df_reg, names="Região", values="Quantidade", hole=0.5)
            fig.update_traces(textinfo="percent", textposition="inside")
            fig.update_layout(legend_title_text="Região")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("Sem instituições identificadas o suficiente para estimar região.")
    with col_dir:
        st.subheader("📍 Estados")
        if len(r["estado_contagem"]) > 0:
            df_est = r["estado_contagem"].reset_index(); df_est.columns = ["Estado", "Quantidade"]
            fig = px.bar(df_est.sort_values("Quantidade"), x="Quantidade", y="Estado", orientation="h",
                         text="Quantidade", color="Quantidade", color_continuous_scale="Teal")
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("Sem instituições identificadas o suficiente para estimar estado.")

    st.markdown("<br>", unsafe_allow_html=True)
    col_esq, col_dir = st.columns(2)
    with col_esq:
        st.subheader("🏆 Student Contest — Categoria")
        if len(r["student_contest_cat"]) > 0:
            df_sc = r["student_contest_cat"].reset_index(); df_sc.columns = ["Categoria", "Quantidade"]
            fig = px.bar(df_sc, x="Categoria", y="Quantidade", color="Categoria", text="Quantidade",
                         color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False, yaxis_title="Qtd.", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("Nenhuma submissão marcada como Student Contest.")
    with col_dir:
        st.subheader("🎤 Formato de Apresentação")
        if len(r["formato_contagem"]) > 0:
            df_fmt = r["formato_contagem"].reset_index(); df_fmt.columns = ["Formato", "Quantidade"]
            fig = px.bar(df_fmt, x="Formato", y="Quantidade", color="Formato", text="Quantidade",
                         color_discrete_map={"Pôster": "#0ea5e9", "Oral": "#f97316"})
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False, yaxis_title="Qtd.", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Trabalhos com formato 'Oral; Pôster' contam nas duas colunas.")
        else:
            st.caption("Coluna de formato de apresentação não encontrada.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🔬 Área Temática")
    if len(r["area_tematica_contagem"]) > 0:
        df_area = r["area_tematica_contagem"].reset_index(); df_area.columns = ["Área Temática", "Quantidade"]
        fig = px.bar(df_area.sort_values("Quantidade"), x="Quantidade", y="Área Temática", orientation="h",
                     text="Quantidade", color="Quantidade", color_continuous_scale="Purples")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, coloraxis_showscale=False, xaxis_title="Nº de trabalhos", yaxis_title="", height=450)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("Coluna 'Área Temática' não encontrada.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("✍️ Autores com mais de um trabalho")
    st.caption(
        f"{r['autores_distintos']} autores distintos ao todo (considerando todos os coautores, não só o "
        f"apresentador) · **{len(r['autores_repetidos'])} deles aparecem em mais de um trabalho**. "
        f"Nomes são unificados ignorando maiúsc./minúsc. e acentos — pode haver alguma coincidência de "
        f"nomes homônimos, revise se for usar para algo crítico."
    )
    if len(r["autores_repetidos"]) > 0:
        top_autores = r["autores_repetidos"].head(20)
        fig = px.bar(top_autores.sort_values("Qtd. de Trabalhos"), x="Qtd. de Trabalhos", y="Autor", orientation="h",
                     text="Qtd. de Trabalhos", color="Qtd. de Trabalhos", color_continuous_scale="Oranges")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, coloraxis_showscale=False, yaxis_title="", height=600)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander(f"📋 Ver todos os {len(r['autores_repetidos'])} autores com mais de um trabalho"):
            st.dataframe(r["autores_repetidos"], use_container_width=True, height=400)
        st.download_button(
            "⬇️ Baixar lista de autores com mais de um trabalho (CSV)",
            r["autores_repetidos"].to_csv(index=False).encode("utf-8-sig"),
            "autores_mais_de_um_trabalho.csv", "text/csv"
        )
    else:
        st.caption("Nenhum autor com mais de um trabalho encontrado.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("👤 Autor Principal")
    st.caption(
        "Considera só o **primeiro nome** listado em 'Autores' de cada trabalho — geralmente quem de fato "
        "desenvolveu a pesquisa. É diferente da análise acima, que inclui todos os coautores e por isso "
        "puxa muito orientador/coordenador que assina vários trabalhos do grupo."
    )
    qtd_principal_repetido = len(r["autor_principal_repetido"])
    c1, c2 = st.columns(2)
    with c1: card("Autores Principais Distintos", r["autores_principais_distintos"], "#2563eb")
    with c2: card("Com mais de 1 trabalho como autor principal", qtd_principal_repetido, "#f97316")

    if qtd_principal_repetido > 0:
        top_principal = r["autor_principal_repetido"].head(20)
        fig = px.bar(top_principal.sort_values("Qtd. de Trabalhos"), x="Qtd. de Trabalhos", y="Autor Principal",
                     orientation="h", text="Qtd. de Trabalhos", color="Qtd. de Trabalhos", color_continuous_scale="Blues")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, coloraxis_showscale=False, yaxis_title="", height=600)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander(f"📋 Ver todos os {qtd_principal_repetido} autores principais com mais de um trabalho"):
            st.dataframe(r["autor_principal_repetido"], use_container_width=True, height=400)
        st.download_button(
            "⬇️ Baixar lista de autores principais com mais de um trabalho (CSV)",
            r["autor_principal_repetido"].to_csv(index=False).encode("utf-8-sig"),
            "autor_principal_mais_de_um_trabalho.csv", "text/csv"
        )
    else:
        st.caption("Nenhum autor principal com mais de um trabalho encontrado.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🗂️ Explorar Dados")
    b1, b2, b3, b4 = st.tabs([
        "📄 Todos os trabalhos únicos",
        "✅ Aceitos",
        "📝 Resumos / 📘 Completos",
        "🔄 Duplicidades detectadas"
    ])
    with b1: st.dataframe(r["dados"], use_container_width=True, height=400)
    with b2: st.dataframe(r["aceitos"], use_container_width=True, height=400)
    with b3:
        cc1, cc2 = st.columns(2)
        with cc1: st.caption(f"Resumos: {len(r['resumos'])}"); st.dataframe(r["resumos"], use_container_width=True, height=350)
        with cc2: st.caption(f"Trabalhos completos: {len(r['completos'])}"); st.dataframe(r["completos"], use_container_width=True, height=350)
    with b4:
        st.caption(
            f"{r['total_duplicados_trabalho']} registros pertencentes a trabalhos "
            f"que aparecem em mais de uma modalidade."
        )
        if len(r["trabalhos_duplicados"]) > 0:
            st.dataframe(r["trabalhos_duplicados"], use_container_width=True, height=400)
        else:
            st.caption("Nenhuma duplicidade de trabalho detectada.")

    st.sidebar.markdown("---")
    st.sidebar.subheader("⬇️ Exportar Resultados")
    st.sidebar.download_button("Baixar Aceitos (CSV)", r["aceitos"].to_csv(index=False).encode("utf-8-sig"), "trabalhos_aceitos.csv", "text/csv")


# ==========================================================
# SIDEBAR — FONTE DOS DADOS (DUAS PLANILHAS)
# ==========================================================
st.sidebar.title("⚙️ Configurações")
st.sidebar.markdown("**1. Planilha de Participantes**")
arquivo_participantes = st.sidebar.file_uploader("ListaParticipante (.xlsx)", type=["xlsx", "xls"], key="up_part")
st.sidebar.markdown("**2. Planilha de Resultados / Trabalhos**")
arquivo_resultados = st.sidebar.file_uploader("ListaResultado (.xlsx)", type=["xlsx", "xls"], key="up_res")

st.markdown('<p class="main-title">📊 Dashboard ENEMP</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Participantes, formação acadêmica, instituições e trabalhos submetidos</p>', unsafe_allow_html=True)
st.markdown("""
<div style="
    background: linear-gradient(90deg, #eff6ff, #dbeafe);
    border-left: 5px solid #2563eb;
    border-radius: 10px;
    padding: 14px 20px;
    margin-bottom: 20px;
    color: #1e3a8a;
    font-size: 0.95rem;
">
    <strong>ℹ️ Aviso:</strong> Este dashboard foi criado por <strong>MelquinhoSedeque</strong>.
    Os dados carregados não são armazenados em servidor: Não altere o código no GitHub.
</div>
""", unsafe_allow_html=True)
if arquivo_participantes is None and arquivo_resultados is None:
    st.info("👈 Envie ao menos uma das planilhas na barra lateral para começar (Participantes e/ou Resultados).")
    st.stop()

dados_participantes = carregar_dados(arquivo_participantes) if arquivo_participantes is not None else None
dados_resultados = carregar_dados(arquivo_resultados) if arquivo_resultados is not None else None

abas_labels = []
if dados_participantes is not None: abas_labels.append("👥 Participantes")
if dados_resultados is not None: abas_labels.append("📄 Trabalhos / Resultados")

abas = st.tabs(abas_labels)
idx = 0
m_participantes = None

if dados_participantes is not None:
    with abas[idx]:
        m_participantes = pagina_participantes(dados_participantes)
    idx += 1

if dados_resultados is not None:
    with abas[idx]:
        dedup_part = m_participantes["dados_dedup"] if m_participantes is not None else None
        qtd_rev = len(m_participantes["revisores"]) if m_participantes is not None else None
        pagina_resultados(dados_resultados, dedup_part, qtd_rev)

st.sidebar.markdown("---")
st.sidebar.caption("MelquinhoSedeque")
