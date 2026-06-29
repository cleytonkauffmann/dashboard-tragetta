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

# Estilização visual em CSS (Verde Corporativo)
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
        .status-box { padding: 18px; border-radius: 6px; margin-bottom: 15px; font-size: 14px; font-weight: 500; line-height: 1.5; }
        .status-up { background-color: #e6f4ea; color: #137333; border-left: 5px solid #137333; }
        button[data-baseweb="tab"] { color: #666666 !important; font-size: 16px !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #1E4620 !important; font-weight: bold !important; }
        div[data-baseweb="tab-highlight"] { background-color: #1E4620 !important; }
    </style>
""", unsafe_allow_html=True)

# Interface de Carga na Barra Lateral
st.sidebar.header("📥 Carga de Dados")
arquivo_publicado = st.sidebar.file_uploader("Arraste o seu arquivo Excel do Power BI (.xlsx):", type=["xlsx"])

# Cabeçalho Principal Estilizado
st.markdown(f"""
    <div class="main-header">
        <div style="min-width:70px; max-width:70px; height:70px; background-color: rgba(255,255,255,0.2); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:32px; margin-right:20px;">📊</div>
        <div class="header-text">
            <h1>📊 Painel de Performance Comercial LTL — Tragetta</h1>
            <p><b>Painel de Análise Tematizado</b> | Tratamento de Dados Automatizado</p>
        </div>
    </div>
""", unsafe_allow_html=True)

if arquivo_publicado is not None:
    try:
        # Lendo o arquivo padrão do Power BI
        df = pd.read_excel(arquivo_publicado)
        
        # Filtrando linhas inválidas ou totais gerais na coluna de Grupo Cliente se existirem
        df_clean = df[df['Grupo Cliente'].notna()].copy()
        df_clean['Receita'] = df_clean['Receita'].fillna(0).astype(float)
        df_clean['Peso Real'] = df_clean['Peso Real'].fillna(0).astype(float)
        df_clean['Qtd CTE'] = df_clean['Qtd CTE'].fillna(0).astype(int)
        
        # Agrupando por Grupo de Cliente para evitar duplicados no seletor principal
        df_grupo = df_clean.groupby('Grupo Cliente').agg({
            'Receita': 'sum',
            'Peso Real': 'sum',
            'Qtd CTE': 'sum'
        }).reset_index()

        # Métricas Globais Dinâmicas
        faturamento_total = df_grupo['Receita'].sum()
        peso_total = df_grupo['Peso Real'].sum()
        total_cte = df_grupo['Qtd CTE'].sum()

        # Exibição dos Blocos de Métricas Principais
        c1, c2, c3 = st.columns(3)
        with c1: 
            st.markdown(f'<div class="metric-card"><div class="metric-title">Receita Total Portfólio</div><div class="metric-value">R$ {faturamento_total:,.2f}</div><div class="metric-sub">Soma de toda a base carregada</div></div>', unsafe_allow_html=True)
        with c2: 
            st.markdown(f'<div class="metric-card blue"><div class="metric-title">Peso Real Total</div><div class="metric-value">{peso_total:,.2f} KG</div><div class="metric-sub" style="color: #0275d8;">Volume total transportado</div></div>', unsafe_allow_html=True)
        with c3: 
            st.markdown(f'<div class="metric-card gold"><div class="metric-title">Quantidade de CTe\'s</div><div class="metric-value">{total_cte:,} Notas</div><div class="metric-sub" style="color: #f0ad4e;">Total de emissões geradas</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Filtro Individual por Cliente
        st.subheader("🔍 Auditoria e Diagnóstico por Grupo de Cliente")
        lista_clientes = sorted(df_grupo['Grupo Cliente'].unique())
        cliente_selecionado = st.selectbox("Selecione o Grupo de Cliente para Auditar:", lista_clientes)

        if cliente_selecionado:
            dados_cliente = df_grupo[df_grupo['Grupo Cliente'] == cliente_selecionado].iloc[0]
            atual_rec = dados_cliente['Receita']
            atual_peso = dados_cliente['Peso Real']
            atual_cte = dados_cliente['Qtd CTE']
            
            col_dados, col_grafico = st.columns([2, 3])
            
            with col_dados:
                st.markdown(f"### Diagnóstico do Grupo: **{cliente_selecionado}**")
                st.markdown(f'<div class="status-box status-up">📈 <b>ANÁLISE DE VOLUMETRIA</b><br>Cliente ativo processado com sucesso a partir dos dados do Power BI.</div>', unsafe_allow_html=True)
                
                st.write(f"**Receita Total:** R$ {atual_rec:,.2f}")
                st.write(f"**Peso Movimentado:** {atual_peso:,.2f} KG")
                st.write(f"**Emissões (CTe):** {atual_cte} unidades")

            with col_grafico:
                # Gráfico Simples de Representatividade da Receita do cliente selecionado vs Resto da Base
                labels = [cliente_selecionado, 'Outros Clientes']
                valores = [atual_rec, max(0, faturamento_total - atual_rec)]
                
                fig = go.Figure(data=[go.Pie(labels=labels, values=valores, hole=.4, marker_colors=['#1E4620', '#E5E5E5'])])
                fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=240, showlegend=True)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        st.markdown("<br><hr>", unsafe_allow_html=True)
        
        # Abas Inferiores de Listagem Completa
        st.subheader("📋 Relatórios Consolidados de Carteira")
        
        df_ranking = df_grupo.sort_values(by='Receita', ascending=False)
        df_ranking.columns = ['Grupo Cliente', 'Faturamento Total', 'Peso Real (KG)', 'Qtd de CTe']
        st.dataframe(df_ranking.style.format({'Faturamento Total': 'R$ {:,.2f}', 'Peso Real (KG)': '{:,.2f}'}), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro na leitura estrutural do arquivo. Garanta que as colunas originais do Power BI não foram renomeadas. Detalhe do erro: {e}")
else:
    st.info("💡 Abra a barra lateral esquerda e coloque o arquivo 'data (44).xlsx' padrão do Power BI para carregar a performance automaticamente.")
