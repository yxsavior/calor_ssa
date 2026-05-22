import streamlit as st
import pandas as pd
import joblib
import shap
import matplotlib.pyplot as plt
import pydeck as pdk

st.set_page_config(page_title="Calor.SSA", layout="wide")
st.title("Calor.SSA - Sistema de Alerta e Intervenção (MVP)")

@st.cache_resource
def load_model():
    return joblib.load('modelo_xgboost_calor.pkl')

modelo = load_model()

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Condições Climáticas Atuais")
    radiacao = st.number_input("Radiação Global (W/m2)", value=1000.0)
    precipitacao = st.number_input("Precipitação (mm)", value=0.0)
    vento = st.number_input("Velocidade do Vento (m/s)", value=0.5)
    umidade = st.number_input("Umidade Relativa (%)", value=60.0)

with col2:
    st.header("Simulador de Intervenção Urbana")
    st.markdown("Altere a cobertura para ver o impacto na sensação térmica do microclima.")
    floresta = st.slider("Formação Florestal (hectares)", min_value=1000.0, max_value=10000.0, value=1000.0)
    urbano = st.slider("Área Urbana Impermeabilizada (hectares)", min_value=10000.0, max_value=25000.0, value=25000.0)

# Preparar dados para o modelo
input_data = pd.DataFrame([[
    radiacao, precipitacao, vento, umidade, floresta, urbano
]], columns=[
    'RADIACAO_IMPUTED', 'PRECIPITACAO TOTAL HORARIO (mm)', 
    'VENTO, VELOCIDADE HORARIA (m/s)', 'UMIDADE RELATIVA DO AR, HORARIA (%)',
    'Forest Formation', 'Urban Area'
])

# 1. Predição da temperatura base (ar) pelo XGBoost
temp_base_ar = modelo.predict(input_data)[0]

# 2. Ajuste de Microclima: Penalidade térmica pela proporção de concreto vs vegetação
razao_urbana = urbano / (floresta + 1)
fator_ilha_calor = min(7.0, razao_urbana * 0.3) # Adiciona até 7°C em áreas densamente concretadas
temp_superficie_estimada = temp_base_ar + fator_ilha_calor

# 3. Cálculo do Heat Index (Sensação Térmica)
if temp_superficie_estimada > 26:
    heat_index = temp_superficie_estimada + (0.5555 * (umidade - 10)) * (temp_superficie_estimada / 30)
else:
    heat_index = temp_superficie_estimada

# Lógica de Agrupamento
if heat_index >= 38.0:
    risco = "Alerta Vermelho - Risco Extremo"
    cor = "red"
elif heat_index >= 33.0:
    risco = "Atenção - Risco Moderado"
    cor = "orange"
else:
    risco = "Normal - Baixo Risco"
    cor = "green"

st.divider()

st.subheader("Resultado do Algoritmo (Camada 1)")
st.markdown(f"**Temperatura do Ar (Base INMET):** {temp_base_ar:.1f} °C")
st.markdown(f"**Sensação Térmica do Setor (Heat Index):** {heat_index:.1f} °C")
st.markdown(f"**Classificação de Risco:** :{cor}[{risco}]")

st.subheader("Explicabilidade das Variáveis Climáticas (SHAP)")
if st.button("Gerar Explicação SHAP"):
    explainer = shap.Explainer(modelo)
    shap_values = explainer(input_data)
    
    fig, ax = plt.subplots(figsize=(8, 4))
    shap.plots.waterfall(shap_values[0], show=False)
    plt.tight_layout()
    st.pyplot(fig)

# Mock Geográfico
st.divider()
st.subheader("Visão Espacial: Mapa de Risco por Bairro (Demonstração)")
st.markdown("Visão do gestor: Como a previsão do modelo se distribui pela cidade.")

# 1. Criação de dados simulados (mock) para o mapa
dados_bairros = pd.DataFrame({
    'Bairro': ['Cajazeiras', 'Barra', 'Periperi'],
    'lat': [-12.8903, -13.0078, -12.8441],
    'lon': [-38.4061, -38.5306, -38.4735],
    'Area_Urbana_Perc': [85, 45, 75],
    'Area_Verde_Perc': [15, 55, 25],
})

# 2. Aplicar a mesma lógica matemática do MVP para cada bairro
def calcular_risco_bairro(row):
    razao = row['Area_Urbana_Perc'] / (row['Area_Verde_Perc'] + 1)
    fator = min(7.0, razao * 0.3)
    temp_superficie = temp_base_ar + fator # temp_base_ar já foi calculada pelo modelo lá em cima
    
    if temp_superficie > 26:
        heat_index = temp_superficie + (0.5555 * (umidade - 10)) * (temp_superficie / 30)
    else:
        heat_index = temp_superficie
        
    if heat_index >= 38.0:
        return heat_index, [255, 0, 0, 150] # Vermelho RGBA
    elif heat_index >= 33.0:
        return heat_index, [255, 165, 0, 150] # Laranja RGBA
    else:
        return heat_index, [0, 255, 0, 150] # Verde RGBA

# Aplicar função
resultados = dados_bairros.apply(calcular_risco_bairro, axis=1)
dados_bairros['Heat_Index'] = [res[0] for res in resultados]
dados_bairros['Cor'] = [res[1] for res in resultados]

# 3. Renderizar o mapa 3D usando PyDeck
layer = pdk.Layer(
    "ScatterplotLayer",
    dados_bairros,
    get_position=['lon', 'lat'],
    get_color='Cor',
    get_radius=1500,
    pickable=True
)

view_state = pdk.ViewState(
    latitude=-12.92, # Centro aproximado de Salvador
    longitude=-38.46,
    zoom=10,
    pitch=45
)

r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{Bairro}\nSensação Térmica: {Heat_Index}°C"})
st.pydeck_chart(r)

# 4. Tabela de Ação para a Codesal
st.markdown("**Lista de Ação Priorizada (Integração ACS)**")
st.dataframe(dados_bairros[['Bairro', 'Heat_Index']].sort_values(by='Heat_Index', ascending=False))