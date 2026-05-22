# Calor.SSA

## Sumário

1. [Proposta](#1-proposta)
2. [Arquitetura](#2-arquitetura)
   - [2.1. Requisitos e Dependências](#21-requisitos-e-dependências)
3. [Passo a Passo de Execução](#3-passo-a-passo-de-execução)
   - [3.1. Passo 1: Instalação das Dependências](#31-passo-1-instalação-das-dependências)
   - [3.2. Passo 2: Processamento e Treinamento do Modelo (Notebook)](#32-passo-2-processamento-e-treinamento-do-modelo-notebook)
   - [3.3. Passo 3: Execução do Dashboard (Streamlit)](#33-passo-3-execução-do-dashboard-streamlit)

---

## 1. Proposta

O **Calor.SSA** é um sistema de monitoramento preditivo e simulação de intervenções urbanas voltado para mitigar os impactos das ilhas de calor crônicas no município de Salvador, Bahia. A solução foi desenhada especificamente para atender demandas de governo (**B2G**), integrando-se conceitualmente ao fluxo operacional da Defesa Civil de Salvador (**Codesal**) e dos Agentes Comunitários de Saúde (**ACS**).

Enquanto a infraestrutura pública atual possui sistemas eficientes para o alerta de chuvas e deslizamentos de terra, o calor extremo permanece como um risco invisível que sobrecarrega a rede de saúde pública (SUS) com internações evitáveis decorrentes de desidratação, crises respiratórias e cardiovasculares. O **Calor.SSA** preenche essa lacuna ao transformar dados brutos climáticos e de cobertura do solo em alertas acionáveis, permitindo que a gestão municipal antecipe ondas de calor, distribua insumos de hidratação preventivamente e planeje intervenções de infraestrutura verde.

---

## 2. Arquitetura

O ecossistema do projeto foi construído sobre uma abordagem espaço-temporal simplificada para o formato de MVP (Produto Mínimo Viável), dividida em camadas principais:

1. **Camada Preditiva (Backend de IA):** Baseia-se em um algoritmo de machine learning **XGBoost**, treinado com dados meteorológicos históricos da estação automatizada **A401 (Salvador) do INMET** abrangendo o período de 2015 a 2021. O modelo é responsável por inferir a temperatura base do ar a partir de variáveis climáticas estáveis (radiação solar, umidade, vento e precipitação).
2. **Camada de Microclima e Ajuste Urbano:** Uma camada matemática que atua diretamente sobre o output do XGBoost. Ela calcula o *Fator de Ilha de Calor* usando dados históricos de cobertura do solo oriundos da plataforma **MapBiomas (Coleção 10.1)**. A proporção entre áreas urbanizadas impermeabilizadas (asfalto, telhados, concreto) e formações florestais ajusta dinamicamente o valor base para determinar o **Índice de Calor (Heat Index)**.
3. **Camada de Explicabilidade (SHAP):** Integração com a biblioteca **SHAP (SHapley Additive exPlanations)**. Através de gráficos do tipo *waterfall*, o sistema expõe explicitamente o peso que cada variável climática teve na composição final da temperatura prevista, oferecendo auditabilidade para o gestor público.
4. **Interface Visual (Frontend):** Painel interativo construído em **Streamlit**. O painel conta com um simulador de impacto ambiental (onde o usuário ajusta manualmente a quantidade de área verde para observar a redução do risco térmico) e um mapa tridimensional interativo renderizado via **PyDeck**, exibindo dados regionalizados simulados em bairros críticos.

### 2.1. Requisitos e Dependências

O ambiente deve possuir o interpretador Python (versão 3.10 ou superior) instalado. As dependências necessárias estão mapeadas no arquivo `requirements.txt`:

* `pandas`
* `numpy`
* `scikit-learn`
* `xgboost`
* `shap`
* `ipykernel`
* `geopandas`
* `openpyxl`
* `streamlit`
* `joblib`
* `matplotlib`
* `pydeck`

---

## 3. Passo a Passo de Execução

### 3.1. Passo 1: Instalação das Dependências

Abra o terminal na pasta raiz do projeto e execute o comando abaixo para instalar todas as bibliotecas listadas no arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### 3.2. Passo 2: Processamento e Treinamento do Modelo (Notebook)

Certifique-se de que o arquivo de dados climáticos e as tabelas do MapBiomas estejam na pasta apropriada conforme os caminhos definidos no código (ex: `../resources/`).

Abra o arquivo `data_processing.ipynb` no VS Code ou em um ambiente Jupyter de sua preferência.

Selecione o kernel correto do Python onde os pacotes foram instalados.

Clique em **Run All** (*Executar Tudo*) para rodar o fluxo completo de transformação de dados e treinamento do modelo.

Ao final da execução, confirme a geração do arquivo binário:

```text
modelo_xgboost_calor.pkl
```

O arquivo deve estar localizado no mesmo diretório do script principal da aplicação (`app.py`).

---

### 3.3. Passo 3: Execução do Dashboard (Streamlit)

No terminal, certifique-se de estar na mesma pasta onde estão localizados:

* `app.py`
* `modelo_xgboost_calor.pkl`

Inicie o servidor local da interface executando o comando:

```bash
streamlit run app.py
```

O terminal exibirá os endereços de acesso local. O aplicativo deverá abrir automaticamente no navegador padrão através do endereço:

```text
http://localhost:8501
```