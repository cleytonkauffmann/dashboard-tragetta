import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64

# Configuração da Página do Streamlit
st.set_page_config(
    page_title="Dashboard Executivo Tragetta LTL",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização visual em CSS original (Verde Corporativo) - SEU LAYOUT ANTIGO INTEGRO
st.markdown("""
    <style>
        .main-header { background-color: #1E4620; color: white; padding: 20px; border-radius: 8px; margin-bottom: 10px; display: flex; align-items: center; }
        .header-text { display: flex; flex-direction: column; }
        .main-header h1 { margin: 0; font-size: 24px; color: white; line-height: 1.2; }
        .main-header p { margin: 5px 0 0 0; font-size: 14px; opacity: 0.9; }
        .metric-card { background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #1E4620; }
        .metric-card.blue { border-left-color: #0275d8; }
        .metric-card.gold { border-left-color: #f0ad4e; }
        .metric-title { font-size: 12px; color: #666; text-transform: uppercase; font-weight: bold; }
        .metric-value { font-size: 22px; font-weight: bold; color: #111; margin-top: 5px; }
        .metric-sub { font-size: 11px; color: #28a745; margin-top: 4px; font-weight: 500; }
        .mini-card-container { display: flex; gap: 10px; margin-top: 15px; }
        .mini-card { flex: 1; background-color: #f8f9fa; padding: 10px; border-radius: 6px; border: 1px solid #e9ecef; text-align: center; }
        .mini-card-title { font-size: 11px; color: #6c757d; text-transform: uppercase; font-weight: bold; }
        .mini-card-value { font-size: 15px; font-weight: bold; color: #212529; margin-top: 2px; }
        .status-box { padding: 18px; border-radius: 6px; margin-bottom: 15px; font-size: 14px; font-weight: 500; line-height: 1.5; }
        .status-up { background-color: #e6f4ea; color: #137333; border-left: 5px solid #137333; }
        .status-down { background-color: #fce8e6; color: #c5221f; border-left: 5px solid #c5221f; }
        .status-new { background-color: #e8f0fe; color: #1a73e8; border-left: 5px solid #1a73e8; }
        button[data-baseweb="tab"] { color: #666666 !important; font-size: 16px !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #1E4620 !important; font-weight: bold !important; }
        div[data-baseweb="tab-highlight"] { background-color: #1E4620 !important; }
        .stTabs [data-baseweb="tab-highlight"] { background-color: #1E4620 !important; }
    </style>
""", unsafe_allow_html=True)

# Interface de Carga na Barra Lateral
st.sidebar.header("📥 Carga de Dados")
arquivo_publicado = st.sidebar.file_uploader("Arraste o seu arquivo Excel (.xlsx):", type=["xlsx"])

# Controlo de Foto de Perfil na Sessão
if 'foto_b64' not in st.session_state:
    st.session_state['foto_b64'] = None

st.sidebar.markdown("---")
config_foto = st.sidebar.checkbox("⚙️ Configurar Minha Foto")
if config_foto:
    nova_foto = st.sidebar.file_uploader("Sua foto de perfil:", type=["png", "jpg", "jpeg"])
    if nova_foto is not None:
        st.session_state['foto_b64'] = base64.b64encode(nova_foto.read()).decode()
        st.rerun()

if st.session_state['foto_b64']:
    avatar_html = f'<img src="data:image/png;base64,{st.session_state["foto_b64"]}" style="width:70px; height:70px; border-radius:50%; object-fit: cover; border: 2px solid white; margin-right:20px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">'
else:
    avatar_html = '<div style="min-width:70px; max-width:70px; height:70px; background-color: rgba(255,255,255,0.2); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:32px; margin-right:20px;">👤</div>'

# Cabeçalho Principal Estilizado Original
st.markdown(f"""
    <div class="main-header">
        {avatar_html}
        <div class="header-text">
            <h1>📊 Painel de Performance Comercial LTL — Tragetta</h1>
            <p><b>Painel de Análise Universal</b> | KAO: {st.experimental_user.email if hasattr(st, "experimental_user") else "Consultor Comercial"}</p>
        </div>
    </div>
""", unsafe_allow_html=True)

if arquivo_publicado is not None:
    try:
        # Lendo os dados brutos
        df = pd.read_excel(arquivo_publicado)
        
        # Filtra linhas de Totais e limpa nulos de acordo com o Power BI
        df_clean = df[df['Grupo Cliente'].notna() & (df['Grupo Cliente'] != 'Total')].copy()
        
        # Mapeando os dados da planilha nova para as variáveis do layout antigo
        df_clean['Mês atual'] = df_clean['Receita'].fillna(0).astype(float)
        df_clean['Ano Passado'] = df_clean['Vlr Mercadoria'].fillna(0).astype(float) # Usando Valor Mercadoria no lugar histórico para não quebrar
        df_clean['Ano Retrasado'] = df_clean['Peso Real'].fillna(0).astype(float) # Usando Peso no lugar para preencher o layout antigo

        # Métricas Globais Dinâmicas (Mantendo os 3 cards superiores idênticos)
        faturamento_total = df_clean['Mês atual'].sum()
        peso_total = df_clean['Peso Real'].sum() if 'Peso Real' in df_clean.columns else 0
        total_cte = df_clean['Qtd CTE'].sum() if 'Qtd CTE' in df_clean.columns else 0

        # Exibição dos Blocos (Layout Antigo Exato)
        c1, c2, c3 = st.columns(3)
        with c1: 
            st.markdown(f'<div class="metric-card"><div class="metric-title">Faturamento Total Atual</div><div class="metric-value">R$ {faturamento_total:,.2f}</div><div class="metric-sub">▲ Dados Atualizados com Sucesso</div></div>', unsafe_allow_html=True)
        with c2: 
            st.markdown(f'<div class="metric-card blue"><div class="metric-title">Volume Total Movimentado</div><div class="metric-value">{peso_total:,.2f} KG</div><div class="metric-sub" style="color: #0275d8;">Métrica de Carga LTL</div></div>', unsafe_allow_html=True)
        with c3: 
            st.markdown(f'<div class="metric-card gold"><div class="metric-title">Total de Conhecimentos (CTe)</div><div class="metric-value">{int(total_cte)} Emissões</div><div class="metric-sub" style="color: #f0ad4e;">Quantidade de Operações</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Filtro Individual por Cliente (Layout Antigo Exato)
        st.subheader("🔍 Foco no Cliente (Análise Executiva e Gráfico Histórico)")
        lista_clientes = sorted(df_clean['Grupo Cliente'].unique())
        cliente_selecionado = st.selectbox("Selecione o Cliente para Auditoria de Performance:", lista_clientes)

        if cliente_selecionado:
            dados_cliente = df_clean[df_clean['Grupo Cliente'] == cliente_selecion0].iloc[0] if not df_clean[df_clean['Grupo Cliente'] == cliente_selecionado].empty else df_clean.iloc[0]
            dados_cliente = df_clean[df_clean['Grupo Cliente'] == cliente_selecionado].iloc[0]
            
            atual = dados_cliente['Mês atual']
            vlr_merc = dados_cliente['Vlr Mercadoria']
            peso_cli = dados_cliente['Peso Real']
            cte_cli = dados_cliente['Qtd CTE']
            
            col_dados, col_grafico = st.columns([2, 3])
            
            with col_dados:
                st.markdown(f"### Diagnóstico: **{cliente_selecionado}**")
                st.markdown(f'<div class="status-box status-up">📈 <b>CONTA ATIVA PROCESSADA</b><br>Volume comercial extraído diretamente do relatório padrão.</div>', unsafe_allow_html=True)
                    
                st.markdown(f"""
                    <div class="mini-card-container">
                        <div class="mini-card"><div class="mini-card-title">Qtd CTe</div><div class="mini-card-value">{int(cte_cli)}</div></div>
                        <div class="mini-card"><div class="mini-card-title">Peso Real (KG)</div><div class="mini-card-value">{peso_cli:,.1f}</div></div>
                        <div class="mini-card" style="border-bottom: 3px solid #1E4620;"><div class="mini-card-title" style="color: #1E4620;">Receita Atual</div><div class="mini-card-value" style="color: #1E4620;">R$ {atual:,.2f}</div></div>
                    </div>
                """, unsafe_allow_html=True)

            with col_grafico:
                # Gráfico mantendo a estrutura visual de barras antiga
                anos_labels = ['Vlr Mercadoria', 'Peso Real (KG)', 'Receita Corrente']
                valores_historicos = [vlr_merc, peso_cli, atual]
                cores_barras = ['#A2B9A4', '#5C845E', '#1E4620'] 
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=anos_labels, y=valores_historicos,
                    text=[f"{v:,.2f}" for v in valores_historicos],
                    textposition='auto', marker_color=cores_barras, name="Indicadores"
                ))
                
                fig.update_layout(
                    margin=dict(l=40, r=20, t=40, b=20), height=280, plot_bgcolor='white', showlegend=False,
                    yaxis=dict(showgrid=True, gridcolor='#F1F1F1', tickformat=",.0f"),
                    xaxis=dict(tickfont=dict(color="#333"))
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        st.markdown("<br><hr>", unsafe_allow_html=True)
        
        # Abas Inferiores de Listagem (Layout Antigo Exato)
        st.subheader("📋 Relatórios Consolidados de Carteira")
        aba1, aba2 = st.tabs(["Faturamento de Cada Cliente (Base)", "Visão Geral de Operações"])

        with aba1:
            df_ret_disp = df_clean[['Grupo Cliente', 'Mês atual', 'Vlr Mercadoria', 'Peso Real']].copy()
            df_ret_disp.columns = ['Grupo Cliente', 'Receita Atual', 'Valor Mercadoria', 'Peso Real (KG)']
            st.dataframe(df_ret_disp.style.format({'Receita Atual': 'R$ {:,.2f}', 'Valor Mercadoria': 'R$ {:,.2f}', 'Peso Real (KG)': '{:,.2f}'}), use_container_width=True, hide_index=True)

        with aba2:
            df_novos_disp = df_clean[['Grupo Cliente', 'Qtd CTE', 'Volume']].sort_values(by='Qtd CTE', ascending=False).copy()
            df_novos_disp.columns = ['Grupo Cliente', 'Quantidade de CTe', 'Volume de Volumes']
            st.dataframe(df_novos_disp, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro na leitura do ficheiro. Detalhe: {e}")
else:
    st.info("💡 Abra a barra lateral esquerda e carregue o seu ficheiro Excel comercial para ativar o painel.")
