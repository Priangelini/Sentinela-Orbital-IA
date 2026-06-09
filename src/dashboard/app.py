"""
Dashboard Web - Sentinela Orbital IA
"""

from datetime import datetime
from pathlib import Path
import sys

import pandas as pd
import streamlit as st
from PIL import Image


BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

from src.agents.orquestrador import executar_orquestrador


ARQUIVO_MUNICIPIOS = BASE_DIR / "data" / "external" / "municipios_monitorados.csv"


st.set_page_config(
    page_title="Sentinela Orbital IA",
    page_icon="🔥",
    layout="wide"
)


@st.cache_data
def carregar_municipios():
    df = pd.read_csv(ARQUIVO_MUNICIPIOS)
    df["rotulo"] = df["municipio"] + " - " + df["estado"]
    return df


def nome_estado(sigla):
    estados = {
        "AM": "Amazonas",
        "PA": "Pará",
        "RO": "Rondônia",
        "MS": "Mato Grosso do Sul",
        "MT": "Mato Grosso"
    }

    return estados.get(str(sigla).upper(), sigla)


def badge_risco(risco):
    risco = str(risco).lower()

    if risco == "alto":
        return "🔥 ALTO"

    if risco == "medio":
        return "⚠️ MÉDIO"

    if risco == "baixo":
        return "✅ BAIXO"

    return "Indisponível"


def definir_estado_esp32(classe_risco):
    risco = str(classe_risco).lower()

    if risco == "alto":
        return {
            "led": "🔴 LED vermelho",
            "buzzer": "Ativo",
            "lcd": "Risco: ALTO",
            "acao": "Alerta local intensivo",
            "status": "Alerta crítico enviado"
        }

    if risco == "medio":
        return {
            "led": "🟡 LED amarelo",
            "buzzer": "Inativo",
            "lcd": "Risco: MEDIO",
            "acao": "Monitoramento reforçado",
            "status": "Alerta preventivo enviado"
        }

    if risco == "baixo":
        return {
            "led": "🟢 LED verde",
            "buzzer": "Inativo",
            "lcd": "Risco: BAIXO",
            "acao": "Monitoramento normal",
            "status": "Condição estável enviada"
        }

    return {
        "led": "Indisponível",
        "buzzer": "Indisponível",
        "lcd": "Risco indisponível",
        "acao": "Sem ação definida",
        "status": "Sem comunicação"
    }


def exibir_imagem(caminho, legenda):
    if caminho and Path(caminho).exists():
        imagem = Image.open(caminho)
        st.image(imagem, caption=legenda, use_container_width=True)
    else:
        st.warning("Imagem não disponível.")


def pagina_dashboard():
    municipios = carregar_municipios()
    lista_municipios = sorted(municipios["rotulo"].unique())

    with st.sidebar:
        st.header("🌎 Monitoramento")

        municipio_rotulo = st.selectbox(
            "Município monitorado",
            lista_municipios
        )

        linha_municipio = municipios[
            municipios["rotulo"] == municipio_rotulo
        ].iloc[0]

        municipio_nome = linha_municipio["municipio"]

        executar = st.button(
            "Executar análise",
            use_container_width=True
        )

        st.markdown("---")
        st.subheader("Módulos ativos")
        st.write("✅ Pipeline de dados")
        st.write("✅ XGBoost")
        st.write("✅ BLIP")
        st.write("✅ YOLO")
        st.write("✅ OpenAI")
        st.write("✅ RAG")
        st.write("✅ Multiagentes")
        st.write("✅ Geolocalização")
        st.write("✅ ESP32 / IoT")

    st.title("🔥 Sentinela Orbital IA")

    st.caption(
        "Sistema multimodal para monitoramento inteligente de risco de incêndios florestais"
    )

    st.caption(
        f"🕒 Última atualização da análise: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    )

    st.caption(
        "🚀 Versão 1.0 | Global Solution FIAP 2026"
    )

    st.caption(
        "📡 Monitoramento inteligente utilizando Open-Meteo, NASA FIRMS, Google Earth Engine, Sentinel-2, XGBoost, BLIP, YOLO, RAG, Multiagentes, OpenAI e estação ESP32."
    )

    st.info(
        "🌎 Cobertura atual: 9 municípios prioritários distribuídos entre Amazônia e Pantanal."
    )

    st.markdown(
        """
        O **Sentinela Orbital IA** é uma aplicação web inteligente para monitoramento
        de risco de incêndios florestais em regiões prioritárias da **Amazônia** e do **Pantanal**.

        O sistema monitora **9 municípios prioritários**, distribuídos em **5 estados brasileiros**,
        selecionados pelo histórico recente de focos de queimadas e pela relevância ambiental
        de seus territórios.

        A solução integra **dados climáticos reais**, **focos de calor**, **NDVI**,
        **imagens Sentinel-2**, **visão computacional**, **modelo preditivo XGBoost**,
        **sistema multiagente**, **YOLO**, **BLIP**, **RAG**, **ESP32** e
        **relatório executivo gerado por IA**.
        """
    )

    if not executar:
        st.info("Selecione um município e clique em **Executar análise**.")
        return

    with st.spinner("Executando sistema multiagente..."):
        resultado = executar_orquestrador(municipio_nome)

    rag = resultado.get("rag", {
        "status": "indisponivel",
        "contexto_recuperado": "Contexto RAG não disponível nesta execução."
    })

    esp32 = definir_estado_esp32(
        resultado["classe_prevista"]
    )

    st.success("Análise concluída!")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Município", resultado["municipio"])

    with col2:
        st.metric("Estado", nome_estado(resultado["estado"]))

    with col3:
        st.metric("Bioma", resultado["bioma"])

    with col4:
        st.metric("Risco XGBoost", badge_risco(resultado["classe_prevista"]))

    with col5:
        st.metric("Risco Visual", badge_risco(resultado["risco_visual"]))

    st.markdown("---")

    st.subheader("📍 Localização monitorada")

    df_mapa = pd.DataFrame({
        "lat": [float(linha_municipio["latitude"])],
        "lon": [float(linha_municipio["longitude"])]
    })

    st.map(df_mapa, zoom=7)

    st.markdown("---")

    col_prob, col_clima = st.columns([1, 1])

    with col_prob:
        st.subheader("📊 Probabilidades do XGBoost")

        df_prob = pd.DataFrame({
            "Classe": list(resultado["probabilidades"].keys()),
            "Probabilidade (%)": list(resultado["probabilidades"].values())
        })

        st.bar_chart(df_prob.set_index("Classe"))

    with col_clima:
        st.subheader("🌦️ Análise Climática")

        for alerta in resultado["analise_climatica"]:
            st.write(f"- {alerta}")

        st.markdown("### Recomendação base")
        st.write(resultado["recomendacao"])

    st.markdown("---")

    col_blip, col_yolo = st.columns(2)

    with col_blip:
        st.subheader("🛰️ Imagem Sentinel-2 analisada")

        legenda = (
            f"Período solicitado: {resultado['ano_mes_solicitado']} | "
            f"Imagem usada: {resultado['ano_mes_imagem']} | "
            f"Correspondência: {resultado['tipo_correspondencia_imagem']}"
        )

        exibir_imagem(resultado.get("imagem"), legenda)

        st.markdown("### 👁️ Interpretação BLIP")
        st.write(resultado["descricao_visual"])

        with st.expander("Descrição original BLIP"):
            st.write(resultado["descricao_original_blip"])

    with col_yolo:
        st.subheader("🎯 Detecção YOLO")

        yolo = resultado["yolo"]

        exibir_imagem(
            yolo.get("imagem_anotada"),
            f"YOLO - {yolo.get('modelo')}"
        )

        st.write(f"**Status:** {yolo.get('status')}")
        st.write(f"**Modelo:** {yolo.get('modelo')}")
        st.write(f"**Total de detecções:** {yolo.get('total_deteccoes')}")
        st.write(f"**Risco YOLO:** {badge_risco(yolo.get('risco_yolo'))}")

        if yolo.get("deteccoes"):
            st.markdown("#### Detecções")
            st.dataframe(pd.DataFrame(yolo["deteccoes"]), use_container_width=True)
        else:
            st.info("Nenhuma detecção encontrada pelo YOLO.")

        with st.expander("Observação técnica YOLO"):
            st.write(yolo.get("observacao"))

    st.markdown("---")

    st.subheader("📡 Estação Local ESP32")

    st.markdown(
        """
        A estação ESP32 representa um ponto físico de alerta em campo.
        Ela recebe a classificação de risco produzida pelo sistema multiagente
        e converte o resultado em sinalização local por **LCD**, **LEDs**, **buzzer**
        e botão de **confirmação humana de ocorrência**.
        """
    )

    col_esp1, col_esp2, col_esp3, col_esp4 = st.columns(4)

    with col_esp1:
        st.metric("Status da estação", "Online")

    with col_esp2:
        st.metric("Município enviado", f"{resultado['municipio']} - {resultado['estado']}")

    with col_esp3:
        st.metric("Risco enviado", badge_risco(resultado["classe_prevista"]))

    with col_esp4:
        st.metric("Modo", "Human-in-the-Loop")

    col_iot1, col_iot2 = st.columns(2)

    with col_iot1:
        st.markdown("### Saída física simulada")
        st.write(f"**LCD:** {resultado['municipio']} - {resultado['estado']} | {esp32['lcd']}")
        st.write(f"**LED ativo:** {esp32['led']}")
        st.write(f"**Buzzer:** {esp32['buzzer']}")
        st.write(f"**Ação local:** {esp32['acao']}")

    with col_iot2:
        st.markdown("### Validação humana")
        st.write("**Botão físico:** disponível")
        st.write("**Função:** confirmar ocorrência observada em campo")
        st.write("**Registro esperado:** OCORRÊNCIA CONFIRMADA")
        st.write(f"**Status da comunicação:** {esp32['status']}")

    with st.expander("📟 Log conceitual enviado para a estação ESP32"):
        st.code(
            f"""
Sentinela Orbital IA - Estacao ESP32
Municipio: {resultado['municipio']} - {resultado['estado']}
Bioma: {resultado['bioma']}
Risco recebido: {resultado['classe_prevista']}
LCD: {esp32['lcd']}
LED: {esp32['led']}
Buzzer: {esp32['buzzer']}
Fonte: Dashboard Web / Orquestrador Multiagente
Funcao: alerta local e validacao humana em campo
            """,
            language="text"
        )

    st.markdown("---")

    st.subheader("🧠 Relatório Executivo Gerado por IA")

    relatorio = resultado["agente_relatorio"]

    st.caption(
        f"Modelo: {relatorio['modelo']} | "
        f"Status: {relatorio['status']} | "
        f"RAG: {relatorio.get('rag_status', rag['status'])}"
    )

    if relatorio.get("erro"):
        st.warning(relatorio["erro"])

    st.markdown(resultado["relatorio_executivo"])

    st.markdown("---")

    st.subheader("📚 Base de Conhecimento (RAG)")

    col_rag1, col_rag2 = st.columns([1, 3])

    with col_rag1:
        status_rag = rag["status"]

        if status_rag == "sucesso":
            st.success("RAG Ativo")
        else:
            st.warning("RAG Indisponível")

    with col_rag2:
        st.caption(
            "O relatório executivo foi enriquecido utilizando documentos internos "
            "de protocolos operacionais, resposta a risco de incêndio e governança de IA."
        )

    with st.expander("📄 Contexto recuperado pelo Agente RAG"):
        st.text(rag["contexto_recuperado"])

    st.markdown("---")

    with st.expander("🧩 Detalhes técnicos da análise"):
        st.json({
            "sistema": resultado["sistema"],
            "status": resultado["status"],
            "data": resultado["data"],
            "periodo_solicitado": resultado["ano_mes_solicitado"],
            "periodo_imagem": resultado["ano_mes_imagem"],
            "correspondencia_imagem": resultado["tipo_correspondencia_imagem"],
            "classe_prevista": resultado["classe_prevista"],
            "risco_visual_blip": resultado["risco_visual"],
            "risco_yolo": resultado["yolo"]["risco_yolo"],
            "status_rag": rag["status"],
            "modelo_relatorio": resultado["agente_relatorio"]["modelo"],
            "esp32": {
                "status": "online",
                "municipio": f"{resultado['municipio']} - {resultado['estado']}",
                "risco_enviado": resultado["classe_prevista"],
                "lcd": esp32["lcd"],
                "led": esp32["led"],
                "buzzer": esp32["buzzer"],
                "modo": "Human-in-the-Loop"
            }
        })


def pagina_arquitetura():
    st.title("🧩 Arquitetura da Solução")

    st.markdown(
        """
        O **Sentinela Orbital IA** foi desenvolvido como uma arquitetura modular,
        multimodal e orientada a agentes para análise de risco de incêndios florestais.
        """
    )

    st.subheader("Fluxo operacional")

    st.code(
        """
Usuário seleciona município monitorado
        ↓
Open-Meteo coleta dados climáticos
        ↓
NASA FIRMS coleta focos de calor
        ↓
Google Earth Engine calcula NDVI
        ↓
Google Earth Engine gera imagens Sentinel-2
        ↓
XGBoost prevê risco de incêndio
        ↓
BLIP interpreta semanticamente a imagem orbital
        ↓
YOLO executa detecção visual complementar
        ↓
RAG recupera protocolos e governança
        ↓
Orquestrador consolida os agentes
        ↓
OpenAI gera relatório executivo
        ↓
Dashboard Web apresenta a análise
        ↓
ESP32 representa estação local de alerta e validação humana em campo
        """,
        language="text"
    )

    st.subheader("Componentes implementados")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            **Dados e Inteligência Artificial**
            - Open-Meteo
            - NASA FIRMS
            - Google Earth Engine
            - Sentinel-2
            - NDVI
            - XGBoost
            - BLIP
            - YOLO
            """
        )

    with col2:
        st.markdown(
            """
            **Agentes, Aplicação e IoT**
            - Agente de Risco
            - Agente Climático
            - Agente Visual BLIP
            - Agente YOLO
            - Agente RAG
            - Agente Relatório OpenAI
            - Dashboard Streamlit
            - ESP32 com LCD, LEDs, buzzer e botão
            """
        )

    st.subheader("Escopo operacional da solução")

    st.markdown(
        """
        O sistema monitora municípios selecionados com base no histórico recente de
        focos de queimadas e relevância ambiental nos biomas Amazônia e Pantanal.

        Essa abordagem concentra os recursos computacionais nas áreas de maior
        criticidade ambiental, aumentando a eficiência do monitoramento, da análise
        preditiva e da geração de alertas.
        """
    )


def pagina_governanca():
    st.title("🛡️ Governança, Confiabilidade e Uso Responsável")

    st.subheader("Governança de IA")

    st.markdown(
        """
        O Sentinela Orbital IA é um sistema de **apoio à decisão ambiental**.
        Ele consolida dados climáticos, orbitais e modelos de IA para apoiar
        ações de monitoramento, prevenção e resposta.

        A solução foi projetada para oferecer rastreabilidade, transparência e
        explicabilidade na análise gerada.
        """
    )

    st.subheader("Boas práticas adotadas")

    st.markdown(
        """
        - Uso de dados reais provenientes de fontes públicas e reconhecidas.
        - Separação entre coleta, processamento, modelo, agentes e interface web.
        - Proteção de credenciais em arquivo `.env`.
        - Não versionamento de chaves de API no GitHub.
        - Registro da origem dos dados utilizados.
        - Uso de RAG para recuperar protocolos internos e regras de governança.
        - Geração de relatório com indicação da base técnica considerada.
        - Uso de fallback local no Agente Relatório para manter continuidade operacional.
        - Identificação do período da imagem orbital utilizada na análise.
        - Estação ESP32 com validação humana em campo.
        """
    )

    st.subheader("Critérios de confiabilidade e interpretação")

    st.markdown(
        """
        Para manter a qualidade e a responsabilidade da análise, o sistema adota
        critérios explícitos de interpretação:

        - A previsão do XGBoost é tratada como indicador preditivo de risco, não como confirmação de ocorrência.
        - A imagem Sentinel-2 é utilizada como evidência visual complementar.
        - Quando não existe imagem disponível para o mês exato, o sistema utiliza a cena temporalmente mais próxima e informa essa correspondência.
        - O BLIP é utilizado para interpretação semântica da imagem orbital.
        - O YOLO é utilizado como detecção visual complementar, com filtro mínimo de confiança para reduzir falsos positivos.
        - O RAG recupera protocolos operacionais e orientações de governança para enriquecer o relatório.
        - O ESP32 representa uma estação local de alerta e validação humana.
        - A recomendação final é gerada pela fusão entre dados tabulares, análise climática, visão computacional, RAG, IoT e relatório generativo.
        """
    )

    st.subheader("Capacidades da solução")

    st.markdown(
        """
        O Sentinela Orbital IA implementa:

        - Monitoramento de 9 municípios prioritários.
        - Coleta de dados climáticos reais.
        - Integração com NASA FIRMS para análise de focos de calor.
        - Geração e processamento de imagens Sentinel-2.
        - Cálculo de indicadores ambientais e NDVI.
        - Predição de risco utilizando XGBoost.
        - Interpretação visual utilizando BLIP.
        - Detecção visual complementar utilizando YOLO.
        - Recuperação de contexto com RAG.
        - Arquitetura multiagente para orquestração da análise.
        - Geração automática de relatórios executivos utilizando OpenAI.
        - Dashboard Web para visualização e apoio à tomada de decisão.
        - Estação local ESP32 com LCD, LEDs, buzzer e confirmação humana.
        """
    )


with st.sidebar:
    pagina = st.radio(
        "Navegação",
        [
            "Dashboard",
            "Arquitetura",
            "Governança"
        ]
    )

if pagina == "Dashboard":
    pagina_dashboard()

elif pagina == "Arquitetura":
    pagina_arquitetura()

else:
    pagina_governanca()