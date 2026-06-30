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

# Inicialização do Banco de Dados com a coluna 'Nº' manual e vazia por padrão
if 'df_perdidos' not in st.session_state:
    st.session_state['df_perdidos'] = pd.DataFrame(columns=['Nº', 'Nome do Cliente', 'Valor Mensal (R$)', 'Motivo da Perda'])

# Estilização visual em CSS
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght=400;500;600;700&display=swap');
        
        html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, button, select, input {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }
        
        .main-header { background-color: #1E4620; color: white; padding: 20px; border-radius: 8px; margin-bottom: 15px; display: flex; align-items: center; }
        .header-text { display: flex; flex-direction: column; }
        .main-header h1 { margin: 0; font-size: 24px; color: white; line-height: 1.2; font-weight: 700; }
        .main-header p { margin: 5px 0 0 0; font-size: 14px; opacity: 0.9; }
        
        .metric-card { background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #1E4620; }
        .metric-card.blue { border-left-color: #0275d8; }
        .metric-card.gold { border-left-color: #f0ad4e; }
        .metric-card.red { border-left-color: #c5221f; }
        .metric-title { font-size: 11px; color: #666; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; }
        .metric-value { font-size: 22px; font-weight: 700; color: #111; margin-top: 5px; word-wrap: break-word; }
        .metric-sub { font-size: 11px; color: #28a745; margin-top: 4px; font-weight: 600; }
        
        .mini-card-container { display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }
        .mini-card { flex: 1; min-width: 100px; background-color: #f8f9fa; padding: 10px; border-radius: 6px; border: 1px solid #e9ecef; text-align: center; }
        .mini-card-title { font-size: 11px; color: #6c757d; text-transform: uppercase; font-weight: 700; }
        .mini-card-value { font-size: 14px; font-weight: 700; color: #212529; margin-top: 2px; word-wrap: break-word; }
        
        .status-box { padding: 15px; border-radius: 6px; margin-bottom: 15px; font-size: 13px; font-weight: 500; line-height: 1.5; word-wrap: break-word; }
        .status-up { background-color: #e6f4ea; color: #137333; border-left: 5px solid #137333; }
        .status-down { background-color: #fce8e6; color: #c5221f; border-left: 5px solid #c5221f; }
        .status-new { background-color: #e8f0fe; color: #1a73e8; border-left: 5px solid #1a73e8; }
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
        if hasattr(st, "rerun"): st.rerun()
        else: st.experimental_rerun()

if st.session_state['foto_b64']:
    avatar_html = f'<img src="data:image/png;base64,{st.session_state["foto_b64"]}" style="width:70px; height:70px; border-radius:50%; object-fit: cover; border: 2px solid white; margin-right:20px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">'
else:
    avatar_html = '<div style="min-width:70px; max-width:70px; height:70px; background-color: rgba(255,255,255,0.2); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:32px; margin-right:20px;">👤</div>'

usuario_email = "Consultor Comercial"
if hasattr(st, "user") and hasattr(st.user, "email") and st.user.email:
    usuario_email = st.user.email
elif hasattr(st, "experimental_user") and hasattr(st.experimental_user, "email") and st.experimental_user.email:
    usuario_email = st.experimental_user.email

st.markdown(f"""
    <div class="main-header">
        {avatar_html}
        <div class="header-text">
            <h1>📊 Painel de Performance Comercial LTL — Tragetta</h1>
            <p><b>Painel de Análise Universal</b> | KAO: {usuario_email}</p>
        </div>
    </div>
""", unsafe_allow_html=True)

if 'slide_atual' not in st.session_state:
    st.session_state['slide_atual'] = 1

if arquivo_publicado is not None:
    try:
        df = pd.read_excel(arquivo_publicado)
        
        df_clean = df[df['Grupo Cliente'].notna() & (df['Grupo Cliente'] != 'Total')].copy()
        df_clean['Mês atual'] = df_clean['Mês atual'].fillna(0).astype(float)
        df_clean['Ano Passado'] = df_clean['Ano Passado'].fillna(0).astype(float)
        df_clean['Ano Retrasado'] = df_clean['Ano Retrasado'].fillna(0).astype(float)

        df_clean['É Cliente Novo'] = (df_clean['Mês atual'] > 0) & (df_clean['Ano Passado'] == 0)
        df_novos = df_clean[df_clean['É Cliente Novo']]
        total_clientes_novos = df_novos.shape[0]
        faturamento_novos = df_novos['Mês atual'].sum()

        faturamento_total = df_clean['Mês atual'].sum()
        faturamento_passado_total = df_clean['Ano Passado'].sum()
        faturamento_antigos = max(0.0, faturamento_total - faturamento_novos)
        
        if faturamento_passado_total > 0:
            crescimento_global = ((faturamento_total - faturamento_passado_total) / faturamento_passado_total) * 100
            sub_texto_crescimento = f"▲ Crescimento de {crescimento_global:.1f}% vs Ano Passado" if crescimento_global >= 0 else f"▼ Queda de {abs(crescimento_global):.1f}% vs Ano Passado"
        else:
            sub_texto_crescimento = "▲ Sem dados de histórico comparativo"

        st.markdown('---')
        nav_col1, nav_col2, nav_col3 = st.columns([1, 3, 1])
        
        with nav_col1:
            if st.button("◀ Voltar Slide", use_container_width=True):
                if st.session_state['slide_atual'] > 1:
                    st.session_state['slide_atual'] -= 1
                    if hasattr(st, "rerun"): st.rerun()
                    else: st.experimental_rerun()
                    
        with nav_col2:
            opcoes_slides = {
                1: "Slide 1: Visão Geral e Composição de Receita",
                2: "Slide 2: Foco no Cliente e Diagnóstico de Performance",
                3: "Slide 3: Relatórios Consolidados da Carteira",
                4: "Slide 4: Auditoria de Contas Perdidas (Churn Manual)"
            }
            selecao = st.selectbox(
                "Navegação Direta:", 
                options=[1, 2, 3, 4], 
                format_func=lambda x: opcoes_slides[x],
                index=st.session_state['slide_atual'] - 1,
                label_visibility="collapsed"
            )
            if selecao != st.session_state['slide_atual']:
                st.session_state['slide_atual'] = selecao
                if hasattr(st, "rerun"): st.rerun()
                else: st.experimental_rerun()
                
        with nav_col3:
            if st.button("Avançar Slide ▶", use_container_width=True):
                if st.session_state['slide_atual'] < 4:
                    st.session_state['slide_atual'] += 1
                    if hasattr(st, "rerun"): st.rerun()
                    else: st.experimental_rerun()

        st.markdown(f"<div style='text-align: center; font-weight: bold; margin-bottom: 20px; color: #1E4620;'>Exibindo Módulo {st.session_state['slide_atual']} de 4</div>", unsafe_allow_html=True)

        # Slide 1
        if st.session_state['slide_atual'] == 1:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card"><div class="metric-title">Faturamento Mês Atual</div><div class="metric-value">R$ {faturamento_total:,.2f}</div><div class="metric-sub">{sub_texto_crescimento}</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card blue"><div class="metric-title">Novos Clientes Conquistados</div><div class="metric-value">{total_clientes_novos} Novos</div><div class="metric-sub" style="color: #0275d8;">Clientes sem histórico no ano passado</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card gold"><div class="metric-title">Receita de Clientes Novos</div><div class="metric-value">R$ {faturamento_novos:,.2f}</div><div class="metric-sub" style="color: #f0ad4e;">Impacto comercial das novas contas</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📊 Composição da Receita Atual (Novos vs. Antigos)")
            col_pizza, col_info_pizza = st.columns([4, 3])
            with col_pizza:
                fig_pizza = go.Figure(data=[go.Pie(labels=['Clientes Antigos', 'Clientes Novos'], values=[faturamento_antigos, faturamento_novos], hole=.45, marker=dict(colors=['#1E4620', '#0275d8']), textinfo='percent')])
                fig_pizza.update_layout(margin=dict(l=30, r=30, t=20, b=20), height=280, showlegend=True)
                st.plotly_chart(fig_pizza, use_container_width=True)

        # Slide 2
        elif st.session_state['slide_atual'] == 2:
            st.subheader("🔍 Foco no Cliente")
            lista_clientes = sorted(df_clean['Grupo Cliente'].unique())
            cliente_selecionado = st.selectbox("Selecione o Cliente:", lista_clientes)
            if cliente_selecionado:
                dados_cliente = df_clean[df_clean['Grupo Cliente'] == cliente_selecionado].iloc[0]
                st.write(f"Análise de faturamento para {cliente_selecionado}")

        # Slide 3
        elif st.session_state['slide_atual'] == 3:
            st.subheader("📋 Relatórios Consolidados de Carteira")
            st.dataframe(df_clean[['Grupo Cliente', 'Ano Retrasado', 'Ano Passado', 'Mês atual']], use_container_width=True, hide_index=True)

        # Slide 4: CORRIGIDO COM COLUNA 'Nº' MANUAL E EM PORTUGUÊS
        elif st.session_state['slide_atual'] == 4:
            st.subheader("❌ Auditoria Comercial de Clientes Perdidos (Churn)")
            
            df_validos = st.session_state['df_perdidos'].dropna(subset=['Nome do Cliente'])
            df_validos = df_validos[df_validos['Nome do Cliente'].astype(str).str.strip() != ""]
            
            total_perdidos_count = df_validos.shape[0]
            faturamento_total_perdido = df_validos['Valor Mensal (R$)'].fillna(0).sum()
            
            col_esq, col_dir = st.columns([3, 4])
            with col_esq:
                st.markdown(f"""
                    <div class="metric-card red" style="margin-bottom: 12px;">
                        <div class="metric-title">Total de Contas Perdidas</div>
                        <div class="metric-value">{total_perdidos_count} Clientes</div>
                    </div>
                    <div class="metric-card red">
                        <div class="metric-title">Faturamento Mensal Total Perdido</div>
                        <div class="metric-value">R$ {faturamento_total_perdido:,.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
                
            with col_dir:
                fig_churn = go.Figure(data=[go.Pie(labels=['Receita Ativa Base', 'Receita Perdida'], values=[faturamento_total, faturamento_total_perdido], hole=.40, marker=dict(colors=['#1E4620', '#c5221f']))])
                fig_churn.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=165)
                st.plotly_chart(fig_churn, use_container_width=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("💡 **Como usar:** Clique em **'Add row'** (Adicionar linha). Agora você pode preencher a coluna **Nº** manualmente com a sua própria sequência!")
            
            # Tabela Editável Ajustada
            tabela_editavel = st.data_editor(
                st.session_state['df_perdidos'],
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,  # Oculta o índice cinza automático do sistema do Streamlit
                key="editor_perdidos", # Garante a estabilidade da digitação sem travamento
                column_config={
                    "Nº": st.column_config.TextColumn("Nº", help="Digite sua numeração manual aqui", width="small"),
                    "Nome do Cliente": st.column_config.TextColumn("Nome do Cliente", required=True),
                    "Valor Mensal (R$)": st.column_config.NumberColumn("Valor Mensal (R$)", format="R$ %.2f", min_value=0.0, default=0.0),
                    "Motivo da Perda": st.column_config.TextColumn("Motivo da Perda")
                }
            )
            
            # Sincroniza as alterações de volta para o session_state de forma passiva
            st.session_state['df_perdidos'] = tabela_editavel

    except Exception as e:
        st.error(f"Erro na leitura do ficheiro: {e}")
else:
    st.info("💡 Abra a barra lateral esquerda e carregue o seu ficheiro Excel comercial para ativar o painel.")
