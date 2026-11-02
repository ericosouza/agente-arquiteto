# Padrões Oficiais de Nomenclatura de Componentes · Banco BV

Este documento especifica a sintaxe estrita que deve ser seguida para nomear todos os componentes gerados na modelagem de arquitetura.

---

## 1. Regra para Componentes Backend (`sboot` e `pyweb`)

Os microsserviços e componentes de backend possuem uma classificação funcional (`tipo`) obrigatória:

$$\text{Nome} = \text{[sigla-tech]}-\text{[sigla-sistema]}-\text{[modulo]}-\text{[tipo]}-\text{[dominio]}$$

### Parâmetros:
- **`[sigla-tech]`**: `sboot` (Spring Boot Java) ou `pyweb` (Python Backend).
- **`[sigla-sistema]`**: A Sigla corporativa do sistema em letras minúsculas (ex: `sesg`, `pjcr`, `cart`, `auto`).
- **`[modulo]`**: O módulo ou macro-funcionalidade (ex: `api`, `srv`, `core`, `bff`).
- **`[tipo]`**: O papel arquitetural do backend:
  - `atom`: Serviço Atômico (opera diretamente sobre os dados do domínio, regras de negócio isoladas).
  - `orch`: Orquestrador (agrega múltiplos serviços ou coordena fluxos de negócio).
  - `bff`: Backend For Frontend (otimizado para atender um canal específico, como web ou mobile).
  - `agent`: Agente Inteligente / Processamento cognitivo.
- **`[dominio]`**: O subdomínio funcional em até 2 palavras separadas por hífen (ex: `credito`, `calculo-risco`, `analise-fraude`).

### Exemplos Válidos:
- `sboot-pjcr-api-atom-simulacao`
- `pyweb-sesg-bff-portal-canal`
- `sboot-cart-srv-orch-fatura`

---

## 2. Regra para Demais Tecnologias do Catálogo

Para as demais tecnologias (`ng`, `streamlit`, `sbatch`, `dataflowbatch`, `gcs`, `pubsub`, `genaigke`), o nome segue a fórmula reduzida de 4 partes:

$$\text{Nome} = \text{[sigla-tech]}-\text{[sigla-sistema]}-\text{[modulo]}-\text{[dominio]}$$

### Exemplos Válidos:
- **Frontend Angular 20:** `ng-sesg-portal-canal`
- **Frontend Streamlit:** `streamlit-auto-painel-analitico`
- **Processamento Batch:** `sbatch-pjcr-carga-contratos`
- **Dataflow:** `dataflowbatch-cart-etl-transacoes`
- **Armazenamento GCS:** `gcs-sesg-docs-comprovantes`
- **Mensageria Pub/Sub:** `pubsub-pjcr-eventos-proposta`
- **Agente GenAI GKE:** `genaigke-sesg-agente-ambiental`

---

## 3. Diretrizes de Sanitização e Validação
- Todos os caracteres devem ser minúsculos (`lowercase`).
- Não utilizar acentos, espaços ou caracteres especiais (apenas letras, números e hífens `-`).
- A `[sigla-sistema]` deve corresponder estritamente à Sigla informada no pré-requisito corporativo.
