# Catálogo Oficial de Tecnologias de Arquitetura · Banco BV

Este documento define os padrões e tecnologias corporativas homologadas para arquiteturas de software e sistemas no Banco BV.

---

## 1. Camada de Canal / Frontend (Channel Layer)

### 1.1 Angular 20 (`ng`)
- **Sigla Oficial:** `ng`
- **Nome:** Frontend Angular 20
- **Camada ArchiMate:** `Channel` / `Application`
- **Tipo ArchiMate:** `ApplicationComponent`
- **Quando Usar:** Aplicações web ricas, portais corporativos voltados para clientes ou colaboradores com alta complexidade de interação, SPAs empresariais com governança de componentes de design system.
- **Alternativa Homologada:** `streamlit` (para dashboards e baixa complexidade).
- **Padrão de Nome do Componente:** `ng-[sigla-sistema]-[modulo]-[dominio]` (ex: `ng-sesg-portal-canal`).

### 1.2 Streamlit (`streamlit`)
- **Sigla Oficial:** `streamlit`
- **Nome:** Streamlit Frontend
- **Camada ArchiMate:** `Channel` / `Application`
- **Tipo ArchiMate:** `ApplicationComponent`
- **Quando Usar:** Interfaces analíticas, dashboards de dados, protótipos rápidos de IA/Data Science e interfaces administrativas de baixa complexidade.
- **Alternativa Homologada:** `ng` (Angular 20).
- **Padrão de Nome do Componente:** `streamlit-[sigla-sistema]-[modulo]-[dominio]`.

---

## 2. Camada de Aplicação / Backend (Application Layer)

### 2.1 Spring Boot Java (`sboot`)
- **Sigla Oficial:** `sboot`
- **Nome:** Spring Boot Java
- **Camada ArchiMate:** `Application`
- **Tipo ArchiMate:** `ApplicationComponent`
- **Subtipo:** Backend com tipo explícito (`api`, `bff`, `atom`, `orch`).
- **Quando Usar:** Microsserviços core transacionais, sistemas de missão crítica, integrações com sistemas legados bancários, regras de negócio complexas com alta exigência de vazão e concorrência.
- **Alternativa Homologada:** `pyweb` (Python Backend).
- **Padrão de Nome:** `sboot-[sigla-sistema]-[modulo]-[tipo]-[dominio]` (ex: `sboot-pjcr-api-atom-credito`).

### 2.2 Python Backend (`pyweb`)
- **Sigla Oficial:** `pyweb`
- **Nome:** Backend Python (FastAPI / Flask)
- **Camada ArchiMate:** `Application`
- **Tipo ArchiMate:** `ApplicationComponent`
- **Subtipo:** Backend com tipo explícito (`api`, `bff`, `orch`, `agent`).
- **Quando Usar:** APIs ágeis REST, BFFs (*Backend For Frontend*), serviços de orquestração de IA Generativa, microsserviços integrados a modelos de Machine Learning e automações analíticas.
- **Alternativa Homologada:** `sboot` (Spring Boot Java).
- **Padrão de Nome:** `pyweb-[sigla-sistema]-[modulo]-[tipo]-[dominio]` (ex: `pyweb-pjcr-bff-credito`).

### 2.3 Spring Batch (`sbatch`)
- **Sigla Oficial:** `sbatch`
- **Nome:** Spring Batch
- **Camada ArchiMate:** `Application`
- **Tipo ArchiMate:** `ApplicationComponent`
- **Quando Usar:** Processamento em lote corporativo, fechamento diário, importação/exportação de arquivos transacionais e conciliações contábeis com checkpoints e controle de transação.
- **Alternativa Homologada:** `dataflowbatch` (Google Cloud Dataflow).
- **Padrão de Nome:** `sbatch-[sigla-sistema]-[modulo]-[dominio]`.

### 2.4 Google Cloud Dataflow (`dataflowbatch`)
- **Sigla Oficial:** `dataflowbatch`
- **Nome:** Google Cloud Dataflow (Apache Beam)
- **Camada ArchiMate:** `Application`
- **Tipo ArchiMate:** `ApplicationComponent`
- **Quando Usar:** Pipelines distribuídos de ETL em larga escala na nuvem, processamento massivo de eventos analíticos e agregações em tempo real ou em lote.
- **Alternativa Homologada:** `sbatch` (Spring Batch).
- **Padrão de Nome:** `dataflowbatch-[sigla-sistema]-[modulo]-[dominio]`.

### 2.5 GenAI no GKE (`genaigke`)
- **Sigla Oficial:** `genaigke`
- **Nome:** GenAI Agent no Google Kubernetes Engine
- **Camada ArchiMate:** `Application`
- **Tipo ArchiMate:** `ApplicationComponent`
- **Quando Usar:** Execução de agentes autônomos, modelos locais de IA, pipelines agênticos orquestrados com LangGraph/CrewAI e copilotos corporativos em contêineres escaláveis.
- **Padrão de Nome:** `genaigke-[sigla-sistema]-[modulo]-[dominio]`.

---

## 3. Camada de Infraestrutura, Armazenamento e Mensageria (Technology Layer)

### 3.1 Google Cloud Storage (`gcs`)
- **Sigla Oficial:** `gcs`
- **Nome:** Google Cloud Storage
- **Camada ArchiMate:** `Technology`
- **Tipo ArchiMate:** `SystemSoftware` / `Artifact`
- **Quando Usar:** Armazenamento seguro de objetos não estruturados (comprovantes bancários, PDFs de contratos, imagens de documentos, relatórios gerados).
- **Padrão de Nome:** `gcs-[sigla-sistema]-[modulo]-[dominio]`.

### 3.2 Google Cloud Pub/Sub (`pubsub`)
- **Sigla Oficial:** `pubsub`
- **Nome:** Google Cloud Pub/Sub
- **Camada ArchiMate:** `Technology`
- **Tipo ArchiMate:** `SystemSoftware`
- **Quando Usar:** Barramento de mensageria assíncrona orientada a eventos (*Event-Driven Architecture*), desacoplamento entre serviços transacionais, envio de notificações e esteiras de streaming.
- **Padrão de Nome:** `pubsub-[sigla-sistema]-[modulo]-[dominio]`.

### 3.3 Bancos de Dados Relacionais e NoSQL
- **Cloud SQL / PostgreSQL:** Para persistência relacional ACID de contratos, transações financeiras e dados mestres.
- **Cloud Firestore / MongoDB:** Para persistência flexível de documentos, propostas semi-estruturadas e históricos de chat.
- **Redis / Memorystore:** Para cache distribuído de baixa latência e sessões de usuários.
