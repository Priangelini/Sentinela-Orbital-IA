# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href="https://www.fiap.com.br/">
  <img src="../../../assets/logo-fiap.png" 
       alt="FIAP - Faculdade de Informática e Administração Paulista" 
       width="40%">
</a>
</p>

<br>

# Global Solution - Sentinela Orbital IA 

## Equipe de Desenvolvimento

## 👨‍🎓 Integrantes: 
- [Luana Porto Pereira Gomes](https://www.linkedin.com/in/luana-porto-pereira-gomes/)  
- [Luma Oliveira](https://www.linkedin.com/in/luma-x)  
- [Priscilla Oliveira](https://www.linkedin.com/in/priscilla-oliveira-023007333/)  
- [Paulo Bernardes](https://www.linkedin.com/in/paulobernardesqs)

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/in/sabrina-otoni-22525519b/">Nome do Tutor</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">Nome do Coordenador</a>


## 📜 Descrição

O **Sentinela Orbital IA** é um sistema multiagente inteligente projetado para detecção, previsão e priorização de incêndios florestais, integrando tecnologias da nova economia espacial com Inteligência Artificial avançada.

A solução combina **dados orbitais** (NASA FIRMS e INPE), **dados climáticos** (Open-Meteo), **sensores embarcados** (ESP32 simulados no Wokwi), **visão computacional** (YOLOv8), **modelos preditivos** (XGBoost), **sistemas multiagentes**, **RAG**, **IA Generativa** e **computação quântica** (QAOA) para priorização de recursos.

Os resultados são disponibilizados em um **Dashboard Web** (Streamlit) e em um **Aplicativo Mobile** (React Native), permitindo monitoramento em tempo real, alertas inteligentes e suporte à tomada de decisão por órgãos ambientais e equipes de combate a incêndios.

O projeto demonstra como tecnologias avançadas de IA e computação podem impulsionar a economia espacial e gerar impacto positivo direto na Terra, contribuindo para a prevenção de desastres ambientais e preservação de biomas brasileiros.


## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

- <b>data</b>: bases de dados utilizadas no projeto.

- <b>docs</b>: documentação, diagramas, arquitetura, relatórios e imagens.

- <b>src</b>: códigos-fonte da solução.

- <b>tests</b>: testes e validações.

- <b>README.md</b>: documentação principal do projeto

```
global-solution-1/
|
├── data/
│   ├── external/
│   ├── raw/
│   └── processed/
│
├── docs/
│   ├── arquitetura/
│   ├── diagramas/
│   ├── imagens/
│   └── relatorio/
│
├── src/
│   ├── agents/
│   ├── api/
│   ├── dashboard/
│   ├── esp32/
│   ├── ml/
│   ├── mobile/
│   ├── models/
│   │   ├── xgboost/
│   │   └── yolo/
│   ├── notebooks/
│   ├── quantum/
│   ├── rag/
│   ├── utils/
│   └── vision/
│
├── tests/
├── README.md
├── requirements.txt
├── .gitignore

```

## 📎 Links 

- <b>Git</b>: Repositório GitHub 

- <b>video</b>: Vídeo Demonstração


## 🔧 Como executar o código

### Pré-requisitos

- **Python**: 3.10 ou superior
- **Node.js**: 18 ou superior (para o aplicativo mobile)
- **Git**: Instalado
- **IDE recomendada**: Visual Studio Code
- **Bibliotecas principais**:
  - `streamlit`, `pandas`, `scikit-learn`, `xgboost`, `ultralytics` (YOLOv8)
  - `langchain`, `openai` (para agentes e RAG)
  - `qiskit` ou `pennylane` (simulação quântica)
- **Conta OpenAI** (para os Agentes e IA Generativa)
- **Conta AWS** (opcional - para S3)

### Passo a Passo de Execução

1. Clone o repositório:
   ```bash
   git clone [URL_DO_SEU_REPOSITORIO]
   cd sentinela-orbital-ia
   ```

2. Crie e ative o ambiente virtual (recomendado):

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / Mac:
source venv/bin/activate
```
3. Instale as dependências:`

```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
- Crie um arquivo .env na raiz do projeto com o seguinte conteúdo:

```bash
.env
OPENAI_API_KEY=sk-sua-chave-aqui
```

5. Execute o Dashboard Web (Streamlit):

```bash
cd src/dashboard
streamlit run app.py
```

6. Execute o Aplicativo Mobile (React Native):`

```bash
cd src/mobile
npm install
npm start
```

7. Simulação do ESP32:

- Acesse o link do projeto no Wokwi (disponível na pasta src/esp32/).

8. Notebooks de Exploração:

- Os notebooks estão disponíveis em src/notebooks/.


## 🗃 Histórico de lançamentos

* 0.5.0 - XX/XX/2024
    * 
* 0.4.0 - XX/XX/2024
    * 
* 0.3.0 - XX/XX/2024
    * 
* 0.2.0 - XX/XX/2024
    * 
* 0.1.0 - XX/XX/2024
    *

---

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/SabrinaOtoni/TEMPLATE-FIAP-GRAD-ON-IA">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">FIAP</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
