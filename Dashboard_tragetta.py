import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import base64

# Configuração da Página do Streamlit
st.set_page_config(
    page_title="Dashboard Executivo Tragetta LTL",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização visual em CSS profissional (Verde Corporativo)
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

# Interface de Carga na Barra Lateral para os Colegas
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

# Cabeçalho Principal Estilizado
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
        df = pd.read_excel(arquivo_publicado)
        df_clean = df[df['Grupo Cliente'] != 'Total'].copy()
        df_clean['Mês atual'] = df_clean['Mês atual'].fillna(0).astype(float)
        df_clean['Ano Passado'] = df_clean['Ano Passado'].fillna(0).astype(float)
        df_clean['Ano Retrasado'] = df_clean['Ano Retrasado'].fillna(0).astype(float)
        
        df_retencao = df_clean[df_clean['Ano Passado'] > 0].copy()
        df_novos = df_clean[df_clean['Ano Passado'] == 0].copy()

        # Métricas Globais Dinâmicas
        faturamento_total = df_clean['Mês atual'].sum()
        faturamento_passado = df_clean['Ano Passado'].sum()
        crescimento_global = ((faturamento_total - faturamento_passado) / faturamento_passado * 100) if faturamento_passado > 0 else 0
        receita_novos = df_novos['Mês atual'].sum()
        qtd_novos = len(df_novos)

        # Exibição dos Blocos
        c1, c2, c3 = st.columns(3)
        with c1: 
            st.markdown(f'<div class="metric-card"><div class="metric-title">Faturamento Total Atual</div><div class="metric-value">R$ {faturamento_total:,.2f}</div><div class="metric-sub">▲ {crescimento_global:+.2f}% vs Ano Passado</div></div>', unsafe_allow_html=True)
        with c2: 
            st.markdown(f'<div class="metric-card blue"><div class="metric-title">Receita de Clientes Novos</div><div class="metric-value">R$ {receita_novos:,.2f}</div><div class="metric-sub" style="color: #0275d8;">Volume Incremental Gerado</div></div>', unsafe_allow_html=True)
        with c3: 
            st.markdown(f'<div class="metric-card gold"><div class="metric-title">Total de Clientes Novos</div><div class="metric-value">{qtd_novos} Clientes</div><div class="metric-sub" style="color: #f0ad4e;">Novas Ativações na Carteira</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Filtro Individual por Cliente
        st.subheader("🔍 Foco no Cliente (Análise Executiva e Gráfico Histórico)")
        lista_clientes = sorted(df_clean['Grupo Cliente'].unique())
        cliente_selecionado = st.selectbox("Selecione o Cliente para Auditoria de Performance:", lista_clientes)

        if cliente_selecionado:
            dados_cliente = df_clean[df_clean['Grupo Cliente'] == cliente_selecionado].iloc[0]
            atual = dados_cliente['Mês atual']
            passado = dados_cliente['Ano Passado']
            retrasado = dados_cliente['Ano Retrasado']
            
            col_dados, col_grafico = st.columns([2, 3])
            
            with col_dados:
                st.markdown(f"### Diagnóstico: **{cliente_selecionado}**")
                
                if passado == 0:
                    st.markdown(f'<div class="status-box status-new">🎯 <b>CONTA NOVA CONQUISTADA</b><br>Cliente ativado recentemente na carteira.<br><b>Faturamento Gerado:</b> R$ {atual:,.2f}</div>', unsafe_allow_html=True)
                elif atual >= passado:
                    crescimento_porcento = ((atual - passado) / passado) * 100 if passado > 0 else 0
                    st.markdown(f'<div class="status-box status-up">📈 <b>CONTA EM EVOLUÇÃO (UPSELL)</b><br>Desempenho comercial positivo comparado ao ano anterior.<br><b>Crescimento real:</b> +R$ {(atual - passado):,.2f} (<b>+{crescimento_porcento:.2f}%</b>)</div>', unsafe_allow_html=True)
                else:
                    queda_porcento = ((passado - atual) / passado) * 100 if passado > 0 else 0
                    st.markdown(f'<div class="status-box status-down">⚠️ <b>CONTA EM RETENÇÃO / QUEDA</b><br>Necessita de plano de ação para recuperação de volume.<br><b>Diferença Negativa:</b> -R$ {(passado - atual):,.2f} (<b>-{queda_porcento:.2f}%</b>)</div>', unsafe_allow_html=True)
                    
                st.markdown(f"""
                    <div class="mini-card-container">
                        <div class="mini-card"><div class="mini-card-title">Ano Retrasado</div><div class="mini-card-value">R$ {retrasado:,.2f}</div></div>
                        <div class="mini-card"><div class="mini-card-title">Ano Passado</div><div class="mini-card-value">R$ {passado:,.2f}</div></div>
                        <div class="mini-card" style="border-bottom: 3px solid #1E4620;"><div class="mini-card-title" style="color: #1E4620;">Período Atual</div><div class="mini-card-value" style="color: #1E4620;">R$ {atual:,.2f}</div></div>
                    </div>
                """, unsafe_allow_html=True)

            with col_grafico:
                anos_labels = ['Ano Retrasado', 'Ano Passado', 'Período Atual']
                valores_historicos = [retrasado, passado, atual]
                cores_barras = ['#A2B9A4', '#5C845E', '#1E4620'] 
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=anos_labels, y=valores_historicos,
                    text=[f"R$ {v:,.2f}" if v > 0 else "" for v in valores_historicos],
                    textposition='auto', marker_color=cores_barras, name="Faturamento"
                ))
                
                fig.update_layout(
                    margin=dict(l=40, r=20, t=40, b=20), height=280, plot_bgcolor='white', showlegend=False,
                    yaxis=dict(showgrid=True, gridcolor='#F1F1F1', tickformat=",.0f"),
                    xaxis=dict(tickfont=dict(color="#333"))
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        st.markdown("<br><hr>", unsafe_allow_html=True)
        
        # Abas Inferiores de Listagem
        st.subheader("📋 Relatórios Consolidados de Carteira")
        aba1, aba2 = st.tabs(["Faturamento de Cada Cliente (Base)", "Painel Separado: Novos Clientes"])

        with aba1:
            df_ret_disp = df_retencao[['Grupo Cliente', 'Mês atual', 'Ano Passado', 'Ano Retrasado']].copy()
            df_ret_disp.columns = ['Grupo Cliente', 'Faturamento Atual', 'Ano Passado', 'Ano Retrasado']
            st.dataframe(df_ret_disp.style.format({'Faturamento Atual': 'R$ {:,.2f}', 'Ano Passado': 'R$ {:,.2f}', 'Ano Retrasado': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        with aba2:
            st.markdown(f"""
                <div style='background-color: #e8f0fe; padding: 15px; border-radius: 6px; margin-bottom: 15px;'>
                    <h3 style='margin:0; color: #1e4620; font-size:16px;'>🎯 Totalizadores de Expansão Comercial</h3>
                    <p style='margin:5px 0 0 0; font-size:14px; color:#333;'>Contas Novas Ativadas: <b>{qtd_novos}</b> | Total Incremental: <b>R$ {receita_novos:,.2f}</b></p>
                </div>
            """, unsafe_allow_html=True)
            df_novos_disp = df_novos[['Grupo Cliente', 'Mês atual']].sort_values(by='Mês atual', ascending=False).copy()
            df_novos_disp.columns = ['Nova Conta Conquistada', 'Faturamento Acumulado']
            st.dataframe(df_novos_disp.style.format({'Faturamento Acumulado': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Erro na leitura do ficheiro. Garanta que as colunas são: 'Grupo Cliente', 'Mês atual', 'Ano Passado' e 'Ano Retrasado'. Detalhe: {e}")
else:
    st.info("💡 Abra a barra lateral esquerda e carregue o seu ficheiro Excel comercial para ativar o painel.")
