# Padrões de Integração e Pipeline de Dados · Banco BV

Este documento orienta como a Persona de Arquitetura/Engenharia deve traçar o pipeline de dados e conexões entre componentes.

---

## 1. Padrões de Comunicação

### 1.1 Comunicação Síncrona (REST / HTTPS / gRPC)
- **Quando Usar:** Consultas em tempo real, simulações instantâneas, operações de leitura e autenticação de usuários.
- **Protocolo:** HTTPS / JSON ou gRPC sobre HTTP/2.
- **Exemplo de Pipeline:**
  $$\text{Usuário} \longrightarrow \text{ng-portal} \xrightarrow{\text{HTTPS/REST}} \text{pyweb-bff} \xrightarrow{\text{HTTPS/REST}} \text{sboot-api-atom}$$

### 1.2 Comunicação Assíncrona Orientada a Eventos (Pub/Sub)
- **Quando Usar:** Notificações de mudança de estado, aprovações de crédito em segundo plano, auditoria, envio de webhooks e esteiras desacopladas.
- **Mecanismo:** Tópicos e assinaturas no Google Cloud Pub/Sub.
- **Exemplo de Pipeline:**
  $$\text{sboot-api-atom} \xrightarrow{\text{Publica Evento}} \text{pubsub-eventos} \xrightarrow{\text{Consome}} \text{sboot-servico-notificacao}$$

### 1.3 Pipeline de Processamento em Lote / Streaming (Dataflow & Spring Batch)
- **Quando Usar:** Cargas noturnas de conciliação, importação de bases de birôs de crédito, geração massiva de relatórios regulatórios.
- **Exemplo de Pipeline:**
  $$\text{gcs-arquivos-entrada} \longrightarrow \text{dataflowbatch-etl} \longrightarrow \text{PostgreSQL / BigQuery}$$

---

## 2. Requisitos de Resiliência e Segurança Bancária
- **Timeout e Retries:** Toda integração síncrona deve prever timeout curto (máx 3 a 5 segundos) e idempotência em retries.
- **Isolamento de Redes:** Apenas o canal web e o BFF podem ter acesso externo; componentes atômicos operam em rede privada interna.
- **Auditoria de Eventos:** Eventos sensíveis de aprovação ou transação monetária devem publicar evento em tópico de auditoria imutável.
