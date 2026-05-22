# Radar Climático — Plataforma Inteligente de Previsão de Secas e Incêndios

O **Radar Climático** é uma plataforma inteligente voltada para o monitoramento ambiental e previsão preditiva de **secas** e **incêndios**, utilizando **Machine Learning**, dados meteorológicos e atualização em tempo real via **WebSocket**.

A solução foi criada com foco inicial na cidade de **Salvador - BA**, mas projetada pensando em escalar futuramente para propriedades rurais no Sertão, permitindo previsões ambientais geolocalizadas e notificações automáticas.

---

# Visão do Projeto

O Radar Climático busca transformar dados climáticos complexos em informações acessíveis para auxiliar usuários na tomada de decisão ambiental.

A plataforma utiliza modelos de Machine Learning treinados para prever:

- 🌧️ **Chance de chuva**
- 🌵 **Risco de seca**
- 🔥 **Chance de queimadas**




O principal objetivo do projeto é permitir uma atuação mais preventiva diante de eventos climáticos extremos, reduzindo impactos ambientais e auxiliando comunidades, produtores rurais e gestores públicos.

---

# Arquitetura do Sistema

A plataforma foi construída utilizando uma arquitetura desacoplada baseada em eventos e comunicação em tempo real.

## Fluxo de Dados

```txt
Open-Meteo
        ↓
Coleta de dados meteorológicos
        ↓
Feature Engineering
(tratamento dos dados para o modelo)
        ↓
Modelos de Machine Learning (.pkl)
        ↓
API FastAPI
        ↓
WebSocket
        ↓
Frontend React
        ↓
Atualização visual em tempo real
```

## Funcionamento

1. O sistema consulta dados meteorológicos da região via **Open-Meteo**.
2. Os dados são tratados e transformados nas mesmas features utilizadas no treinamento dos modelos.
3. Os modelos de Machine Learning realizam as previsões.
4. A API publica os resultados automaticamente via **WebSocket**.
5. O frontend recebe os dados em tempo real e atualiza o dashboard automaticamente.

---

# Tecnologias Utilizadas

## Backend

- Python 3.12
- FastAPI
- WebSocket
- Pandas
- NumPy
- Scikit-Learn
- LightGBM
- Joblib

## Frontend

- React
- Vite
- CSS3

## Infraestrutura

- Docker
- Docker Compose

---
# Como Rodar com Docker

## Pré-requisitos

Antes de executar o projeto, é necessário possuir:

- Docker Desktop instalado
- Docker Compose habilitado

---

## Clonar o Projeto

```bash
git clone URL_DO_REPOSITORIO

cd radar-climatico
```

---

## Executar a Aplicação

Na raiz do projeto:

```bash
docker compose up --build
```

O sistema irá subir automaticamente:

### API

```txt
http://localhost:8000
```

### Frontend

```txt
http://localhost:5173
```

---

## WebSocket

Endpoint utilizado:

```txt
ws://localhost:8000/ws/predictions
```

---

# Escalabilidade Futura

O Radar Climático foi arquitetado pensando em expansão.

## Integração com INMET

O ideal será integrar futuramente APIs e bases oficiais do **INMET**, utilizando dados meteorológicos observados diretamente das estações locais do governo.

Isso permitirá:

- Maior precisão regional
- Dados observados reais
- Melhor validação dos modelos

## Notificações Inteligentes

Fluxo futuro:

```txt
Banco de previsões
        ↓
IA simplifica mensagem
        ↓
Text-to-Speech
        ↓
WhatsApp API
        ↓
Usuário recebe texto + áudio
```

Exemplo:

> "Atenção: há risco elevado de queimadas na sua região nas próximas horas. Evite atividades com fogo e monitore áreas secas."
