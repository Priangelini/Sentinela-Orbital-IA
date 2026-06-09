# Arquitetura da Solução - Sentinela Orbital IA

O Sentinela Orbital IA utiliza uma arquitetura modular, multimodal e orientada a agentes para monitoramento e prevenção de incêndios florestais em municípios prioritários da Amazônia e do Pantanal.

A solução integra dados orbitais, sensoriamento climático, visão computacional, modelos preditivos, sistemas multiagentes e uma estação embarcada para apoiar a tomada de decisão em tempo real.

## 1. Camada de Dados

* Open-Meteo (dados climáticos)
* NASA FIRMS (focos de calor)
* Sentinel-2 / Google Earth Engine (imagens orbitais)
* NDVI (índice de vegetação)

---

## 2. Camada de Persistência

* `data/raw`: dados brutos coletados
* `data/processed`: dados tratados e consolidados
* `docs/imagens`: imagens orbitais e resultados de análise
* `docs/base_conhecimento`: documentos para RAG
* `src/models`: artefatos e modelos utilizados pelo sistema

---

## 3. Camada de Inteligência Artificial

* XGBoost: Predição contínua de risco (score de 0.0 a 1.0)
* YOLOv8: Detecção visual complementar em imagens orbitais
* BLIP: Interpretação semântica complementar de imagens
* OpenAI: Geração de relatórios executivos
* RAG: Recuperação de protocolos e diretrizes

---

## 4. Camada Multiagente

* Orquestrador: Coordena o fluxo entre agentes
* Agente Climático: Analisa condições ambientais
* Agente Visual: Processa imagens com BLIP
* Agente YOLO: Executa detecção visual complementar
* Agente de Risco: Executa o modelo XGBoost e classifica o risco
* Agente RAG: Consulta a base de conhecimento
* Agente Relatório: Gera o relatório executivo

---

## 5. Camada de Governança e Ética

* Base de conhecimento com protocolos oficiais
* Rastreabilidade dos dados e decisões
* Proteção de credenciais via variáveis de ambiente
* Human-in-the-Loop via botão físico no ESP32
* Transparência nos resultados do modelo

---

## 6. Camada de Interface

### Dashboard Web (Streamlit)

* Mapa geográfico dos municípios monitorados
* Indicadores de risco
* Relatório executivo gerado por IA
* Contexto recuperado pelo RAG
* Estado da estação ESP32
* Visualização dos resultados dos agentes

### Evolução da Arquitetura

A arquitetura foi projetada para permitir futura integração com:

* Aplicações móveis
* Serviços em nuvem
* Novas fontes de dados ambientais
* Novos agentes especializados

---

## 7. Camada Embarcada (ESP32)

* LCD para exibição de risco
* LEDs de sinalização (verde, amarelo e vermelho)
* Buzzer para alertas sonoros
* Botão para confirmação humana (Human-in-the-Loop)

A estação embarcada representa um ponto local de monitoramento e validação humana em campo, reforçando a confiabilidade operacional da solução.

---

## Fluxo Geral da Solução

1. O usuário seleciona um município monitorado.
2. O sistema coleta e consolida dados ambientais.
3. O modelo XGBoost realiza a predição de risco.
4. O BLIP interpreta semanticamente as imagens orbitais.
5. O YOLO executa a análise visual complementar.
6. O RAG recupera protocolos e diretrizes da base de conhecimento.
7. O Orquestrador consolida os resultados dos agentes.
8. O OpenAI gera o relatório executivo.
9. O Dashboard apresenta os resultados ao usuário.
10. A estação ESP32 representa a camada operacional local de alerta e validação humana.

---

## Tecnologias Utilizadas

* Python
* Streamlit
* XGBoost
* OpenAI
* YOLOv8
* BLIP
* RAG
* NASA FIRMS
* Open-Meteo
* Google Earth Engine
* Sentinel-2
* ESP32
* Wokwi
* GitHub
