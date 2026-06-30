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

# Estilização visual em CSS (Verde Corporativo e Controles dos Slides)
st.markdown("""
    <style>
        .main-header { background-color: #1E4620; color: white; padding: 20px; border-radius: 8px; margin-bottom: 15px; display: flex; align-items: center; }
        .header-text { display: flex; flex-direction: column; }
        .main-header h1 { margin: 0; font-size: 24px; color: white; line-height: 1.2; }
        .main-header p { margin: 5px 0 0 0; font-size: 14px; opacity: 0.9; }
        
        /* Estilo da barra de navegação dos slides */
        .slide-nav-container { background-color: #f8f9fa; padding: 12px; border-radius: 8px; border: 1px solid #e9ecef; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .slide-indicator { font-size: 16px; font-weight: bold; color: #1E4620; text-transform: uppercase; }
        
        .metric-card { background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #1E4620; }
        .metric-card.blue { border-left-color: #0275d8; }
        .metric-card.gold { border-left-color: #f0ad4e; }
        .metric-title { font-size: 12px; color: #666; text-transform: uppercase; font-weight: bold; }
        .metric-value { font-size: 22px; font-weight: bold; color: #111; margin-top: 5px; word-wrap: break-word; }
        .metric-sub { font-size: 11px; color: #28a745; margin-top: 4px; font-weight: 500; }
        
        .mini-card-container { display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }
        .mini-card { flex: 1; min-width: 100px; background-color: #f8f9fa; padding: 10px; border-radius: 6px; border: 1px solid #e9ecef; text-align: center; }
        .mini-card-title { font-size: 11px; color: #6c757d; text-transform: uppercase; font-weight: bold; }
        .mini-card-value { font-size: 14px; font-weight: bold; color: #212529; margin-top: 2px; word-wrap: break-word; }
        
        .status-box { padding: 15px; border-radius: 6px; margin-bottom: 15px; font-size: 13px; font-weight: 500; line-height: 1.5; word-wrap: break-word; }
        .status-up { background-color: #e6f4ea; color: #137333; border-left: 5px solid #137333; }
        .status-down { background-color: #fce8e6; color: #c5221f; border-left: 5px solid #c5221f; }
        .status-new { background-color: #e8f0fe; color: #1a73e8; border-left: 5px solid #1a73e8; }
        
        button[data-baseweb="tab"] { color: #666666 !important; font-size: 16px !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #1E4620 !important; font-weight: bold !important; }
        div[data-baseweb="tab-highlight"] { background-color: #1E4620 !important; }
    </style>
""", unsafe_allow_html=True)

# Interface de Carga na Barra Lateral
st.sidebar.header("📥 Carga de Dados")
arquivo_publicado = st.sidebar.file_uploader("Arraste o seu arquivo Excel (.xlsx):", type=["xlsx"])

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

st.markdown(f"""
    <div class="main-header">
        {avatar_html}
        <div class="header-text">
            <h1>📊 Painel de Performance Comercial LTL — Tragetta</h1>
            <p><b>Painel de Análise Universal</b> | KAO: {st.experimental_user.email if hasattr(st, "experimental_user") else "Consultor Comercial"}</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Inicialização do Controle de Slides no Session State
if 'slide_atual' not in st.session_state:
    st.session_state['slide_atual'] = 1

if arquivo_publicado is not None:
    try:
        df = pd.read_excel(arquivo_publicado)
        
        # Filtragem padrão de linhas vazias e totais
        df_clean = df[df['Grupo Cliente'].notna() & (df['Grupo Cliente'] != 'Total')].copy()
        
        df_clean['Mês atual'] = df_clean['Mês atual'].fillna(0).astype(float)
        df_clean['Ano Passado'] = df_clean['Ano Passado'].fillna(0).astype(float)
        df_clean['Ano Retrasado'] = df_clean['Ano Retrasado'].fillna(0).astype(float)

        # Identificação de Clientes Novos (Mês atual > 0 E Ano Passado == 0)
        df_clean['É Cliente Novo'] = (df_clean['Mês atual'] > 0) & (df_clean['Ano Passado'] == 0)
        df_novos = df_clean[df_clean['É Cliente Novo']]
        total_clientes_novos = df_novos.shape[0]
        faturamento_novos = df_novos['Mês atual'].sum()

        # Métricas Globais Dinâmicas
        faturamento_total = df_clean['Mês atual'].sum()
        faturamento_passado_total = df_clean['Ano Passado'].sum()
        faturamento_antigos = max(0.0, faturamento_total - faturamento_novos)
        
        # Crescimento Global
        if faturamento_passado_total > 0:
            crescimento_global = ((faturamento_total - faturamento_passado_total) / faturamento_passado_total) * 100
            sub_texto_crescimento = f"▲ Crescimento de {crescimento_global:.1f}% vs Ano Passado" if crescimento_global >= 0 else f"▼ Queda de {abs(crescimento_global):.1f}% vs Ano Passado"
        else:
            sub_texto_crescimento = "▲ Sem dados de histórico comparativo"

        # --- BARRA DE NAVEGAÇÃO DOS SLIDES COM BOTÕES ---
        st.markdown('---')
        nav_col1, nav_col2, nav_col3 = st.columns([1, 3, 1])
        
        with nav_col1:
            if st.button("◀ Voltar Slide", use_container_width=True):
                if st.session_state['slide_atual'] > 1:
                    st.session_state['slide_atual'] -= 1
                    st.rerun()
                    
        with nav_col2:
            opcoes_slides = {
                1: "Slide 1: Visão Geral e Composição de Receita",
                2: "Slide 2: Foco no Cliente e Diagnóstico de Performance",
                3: "Slide 3: Relatórios Consolidados da Carteira"
            }
            selecao = st.selectbox(
                "Navegação Direta:", 
                options=[1, 2, 3], 
                format_func=lambda x: opcoes_slides[x],
                index=st.session_state['slide_atual'] - 1,
                label_visibility="collapsed"
            )
            if selecao != st.session_state['slide_atual']:
                st.session_state['slide_atual'] = selecao
                st.rerun()
                
        with nav_col3:
            if st.button("Avançar Slide ▶", use_container_width=True):
                if st.session_state['slide_atual'] < 3:
                    st.session_state['slide_atual'] += 1
                    st.rerun()

        st.markdown(f"<div style='text-align: center; font-weight: bold; margin-bottom: 20px; color: #1E4620;'>Exibindo Módulo {st.session_state['slide_atual']} de 3</div>", unsafe_allow_html=True)

        # ==========================================
        # SLIDE 1: METRICAS GERAIS E PIZZA
        # ==========================================
        if st.session_state['slide_atual'] == 1:
            c1, c2, c3 = st.columns(3)
            with c1: 
                st.markdown(f'<div class="metric-card"><div class="metric-title">Faturamento Mês Atual</div><div class="metric-value">R$ {faturamento_total:,.2f}</div><div class="metric-sub">{sub_texto_crescimento}</div></div>', unsafe_allow_html=True)
            with c2: 
                st.markdown(f'<div class="metric-card blue"><div class="metric-title">Novos Clientes Conquistados</div><div class="metric-value">{total_clientes_novos} Novos</div><div class="metric-sub" style="color: #0275d8;">Clientes sem histórico no ano passado</div></div>', unsafe_allow_html=True)
            with c3: 
                st.markdown(f'<div class="metric-card gold"><div class="metric-title">Receita de Clientes Novos</div><div class="metric-value">R$ {faturamento_novos:,.2f}</div><div class="metric-sub" style="color: #f0ad4e;">Impacto comercial das novas contas</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📊 Composição da Receita Atual (Novos vs. Antigos)")
            
            col_pizza, col_info_pizza = st.columns([4, 3])
            with col_pizza:
                fig_pizza = go.Figure(data=[go.Pie(
                    labels=['Clientes Antigos', 'Clientes Novos'],
                    values=[faturamento_antigos, faturamento_novos],
                    hole=.45,
                    marker=dict(colors=['#1E4620', '#0275d8']), 
                    textinfo='percent',  
                    textposition='inside', 
                    textfont=dict(size=14, color='white', weight='bold'),
                    insidetextorientation='horizontal'
                )])
                fig_pizza.update_layout(
                    margin=dict(l=30, r=30, t=20, b=20), height=280, showlegend=True,  
                    legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
                    plot_bgcolor='white'
                )
                st.plotly_chart(fig_pizza, use_container_width=True, config={'displayModeBar': False})
                
            with col_info_pizza:
                perc_novos = (faturamento_novos / faturamento_total * 100) if faturamento_total > 0 else 0
                perc_antigos = (faturamento_antigos / faturamento_total * 100) if faturamento_total > 0 else 0
                
                st.markdown(f"""
                    <div style="margin-top: 10px;">
                        <p style="font-size: 14px; margin-bottom: 6px;">🟩 <b>Clientes Antigos:</b> {perc_antigos:.1f}% (<span style="font-family: monospace;">R$ {faturamento_antigos:,.2f}</span>)</p>
                        <p style="font-size: 14px; margin-bottom: 15px;">🟦 <b>Clientes Novos:</b> {perc_novos:.1f}% (<span style="font-family: monospace;">R$ {faturamento_novos:,.2f}</span>)</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if total_clientes_novos > 0:
                    st.markdown(f"""
                        <div class="status-box status-new">
                            🚀 <b>Resultado Comercial:</b> As novas contas representam <b>{perc_novos:.1f}%</b> do faturamento global do período.
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div class="status-box" style="background-color: #f8f9fa; color: #666; border-left: 5px solid #6c757d;">
                            💡 <b>Base Consolidada:</b> 100% da receita provém de clientes recorrentes do ano passado.
                        </div>
                    """, unsafe_allow_html=True)

        # ==========================================
        # SLIDE 2: FOCO NO CLIENTE
        # ==========================================
        elif st.session_state['slide_atual'] == 2:
            st.subheader("🔍 Foco no Cliente (Análise Executiva e Gráfico Histórico)")
            lista_clientes = sorted(df_clean['Grupo Cliente'].unique())
            cliente_selecionado = st.selectbox("Selecione o Cliente para Auditoria de Performance:", lista_clientes)

            if cliente_selecionado:
                dados_cliente = df_clean[df_clean['Grupo Cliente'] == cliente_selecionado].iloc[0]
                
                atual = dados_cliente['Mês atual']
                passado = dados_cliente['Ano Passado']
                retrasado = dados_cliente['Ano Retrasado']
                es_novo = dados_cliente['É Cliente Novo']
                
                if es_novo:
                    status_html = f'<div class="status-box status-new">⭐ <b>NOVA CONTA CONQUISTADA!</b><br>Este cliente é novo na carteira, trazendo R$ {atual:,.2f} de receita inédita neste período!</div>'
                elif passado > 0:
                    variacao = ((atual - passado) / passado) * 100
                    if variacao >= 0:
                        status_html = f'<div class="status-box status-up">📈 <b>DESEMPENHO EM ALTA ({variacao:.1f}%)</b><br>O cliente apresentou crescimento comparado ao ano passado.</div>'
                    else:
                        status_html = f'<div class="status-box status-down">📉 <b>ALERTA DE QUEDA ({variacao:.1f}%)</b><br>O faturamento atual está abaixo do ano passado.</div>'
                else:
                    status_html = '<div class="status-box status-up">📈 <b>CONTA ATIVA</b><br>Cliente operando normalmente no período corrente.</div>'

                col_dados, col_grafico = st.columns([2, 3])
                
                with col_dados:
                    st.markdown(f"### Diagnóstico: **{cliente_selecionado}**")
                    st.markdown(status_html, unsafe_allow_html=True)
                        
                    st.markdown(f"""
                        <div class="mini-card-container">
                            <div class="mini-card"><div class="mini-card-title">Ano Retrasado</div><div class="mini-card-value">R$ {retrasado:,.2f}</div></div>
                            <div class="mini-card"><div class="mini-card-title">Ano Passado</div><div class="mini-card-value">R$ {passado:,.2f}</div></div>
                            <div class="mini-card" style="border-bottom: 3px solid #1E4620;"><div class="mini-card-title" style="color: #1E4620;">Mês Atual</div><div class="mini-card-value" style="color: #1E4620;">R$ {atual:,.2f}</div></div>
                        </div>
                    """, unsafe_allow_html=True)

                with col_grafico:
                    anos_labels = ['Ano Retrasado', 'Ano Passado', 'Mês Atual']
                    valores_historicos = [retrasado, passado, atual]
                    cores_barras = ['#A2B9A4', '#5C845E', '#1E4620'] 
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=anos_labels, y=valores_historicos,
                        text=[f"R$ {v:,.2f}" for v in valores_historicos],
                        textposition='auto', marker_color=cores_barras, name="Faturamento"
                    ))
                    
                    fig.update_layout(
                        margin=dict(l=50, r=30, t=50, b=30), height=280, plot_bgcolor='white', showlegend=False,
                        yaxis=dict(showgrid=True, gridcolor='#F1F1F1', tickformat=",.0f", automargin=True),
                        xaxis=dict(tickfont=dict(color="#333"), automargin=True)
                    )
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # ==========================================
        # SLIDE 3: RELATÓRIOS CONSOLIDADOS (COM % DENTRO DA TABELA)
        # ==========================================
        elif st.session_state['slide_atual'] == 3:
            st.subheader("📋 Relatórios Consolidados de Carteira")
            aba1, aba2 = st.tabs(["Faturamento Geral da Carteira", "Apenas Clientes Novos Conquistados"])

            with aba1:
                # Copia e prepara as colunas base
                df_ret_disp = df_clean[['Grupo Cliente', 'Ano Retrasado', 'Ano Passado', 'Mês atual']].copy()
                df_ret_disp.columns = ['Grupo Cliente', 'Ano Retrasado', 'Ano Passado', 'Mês Atual']
                
                # Função interna para evitar divisões por zero com segurança
                def calc_pct(atual, anterior):
                    if anterior > 0:
                        return ((atual - anterior) / anterior) * 100
                    return 0.0

                # Geração das colunas de variação percentual
                df_ret_disp['% Vs Retrasado'] = df_ret_disp.apply(lambda r: calc_pct(r['Ano Passado'], r['Ano Retrasado']), axis=1)
                df_ret_disp['% Vs Passado'] = df_ret_disp.apply(lambda r: calc_pct(r['Mês Atual'], r['Ano Passado']), axis=1)
                
                # Reorganização das colunas para colocar a porcentagem logo ao lado do seu período
                ordem_colunas = [
                    'Grupo Cliente', 
                    'Ano Retrasado', 
                    'Ano Passado', '% Vs Retrasado', 
                    'Mês Atual', '% Vs Passado'
                ]
                df_ret_disp = df_ret_disp[ordem_colunas]
                
                # Exibição profissional com formatação monetária e percentual (+ ou -)
                st.dataframe(
                    df_ret_disp.style.format({
                        'Ano Retrasado': 'R$ {:,.2f}',
                        'Ano Passado': 'R$ {:,.2f}',
                        '% Vs Retrasado': '{:+.1f}%',
                        'Mês Atual': 'R$ {:,.2f}',
                        '% Vs Passado': '{:+.1f}%'
                    }), 
                    use_container_width=True, 
                    hide_index=True
                )

            with aba2:
                if total_clientes_novos > 0:
                    df_novos_disp = df_novos[['Grupo Cliente', 'Mês atual']].copy()
                    df_novos_disp.columns = ['Nome do Novo Cliente', 'Faturamento Gerado']
                    st.dataframe(df_novos_disp.style.format({'Faturamento Gerado': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum cliente novo detectado nesta planilha (todos os clientes ativos possuem histórico no ano passado).")

    except Exception as e:
        st.error(f"Erro na leitura do ficheiro. Detalhe: {e}")
else:
    st.info("💡 Abra a barra lateral esquerda e carregue o seu ficheiro Excel comercial para ativar o painel.")
