# Diretrizes Oficiais de Modelagem ArchiMate 3.2 para o Archi

Este documento define as regras do metamodelo ArchiMate 3.2 que garantem que o modelo exportado seja 100% válido e compatível para abertura no software **Archi**.

---

## 1. Camadas Oficiais do ArchiMate

O modelo do Banco BV organiza os elementos em 3 camadas principais:

### 1.1 Camada de Negócio (Business Layer) - Amarela (#ffffcc)
- **Papel:** Representa atores, papéis, processos e serviços de negócio corporativos.
- **Elementos Comuns:** `BusinessActor` (Colaborador, Cliente PJ), `BusinessProcess` (Simulação de Financiamento), `BusinessService`.

### 1.2 Camada de Aplicação (Application Layer) - Azul Claro (#ccffff)
- **Papel:** Descreve os sistemas, componentes de software, APIs e BFFs que suportam as operações de negócio.
- **Elementos Comuns:**
  - `ApplicationComponent`: Frontends (`ng`, `streamlit`), Backends (`sboot`, `pyweb`), Batch (`sbatch`, `dataflowbatch`), Agentes (`genaigke`).
  - `ApplicationInterface`: Interfaces REST, endpoints gRPC, WebSockets.
  - `ApplicationService`: Serviços expostos pelas aplicações.

### 1.3 Camada de Tecnologia (Technology Layer) - Verde Claro (#ccffcc)
- **Papel:** Infraestrutura de execução, bancos de dados, storages, barramentos de mensageria e nós computacionais.
- **Elementos Comuns:**
  - `SystemSoftware`: Pub/Sub, Bancos de Dados (PostgreSQL, Cloud SQL), GCS.
  - `Node`: Clusters GKE, Servidores Virtuais Compute Engine.
  - `Artifact`: Arquivos, esquemas ou tabelas de dados.

---

## 2. Tipos de Relacionamentos Permitidos

Para evitar conexões inválidas no metamodelo:

1. **`Serving` (Atendimento):** Um elemento provê funcionalidade a outro.
   - *Exemplo:* `pyweb-bff` atende (`Serving`) o componente `ng-portal`.
   - *Exemplo:* `sboot-api` atende (`Serving`) o `pyweb-bff`.
2. **`Access` (Acesso a Dados):** Uma aplicação lê ou grava em uma base de dados ou storage.
   - *Exemplo:* `sboot-api` acessa (`Access`, leitura/escrita) o banco `PostgreSQL`.
   - *Exemplo:* `sbatch-carga` grava (`Access`) no bucket `gcs-docs`.
3. **`Flow` (Fluxo de Informação / Eventos):** Troca de mensagens ou dados entre componentes.
   - *Exemplo:* `sboot-api` envia fluxo (`Flow`) para o tópico `pubsub-eventos`.
4. **`Realization` (Realização):** Um componente de software realiza um serviço de aplicação.
5. **`Composition` / `Aggregation`:** Um sistema maior agrupa módulos subordinados.

---

## 3. Padrão de Exportação XML do The Open Group
- O arquivo deve seguir a especificação XML Schema do **The Open Group ArchiMate Model Exchange File Format (v3.2)**.
- Cada elemento possui um identificador único `id="id-..."`, `name`, `xsi:type`.
- Cada relacionamento possui `id="rel-..."`, `source="id-..."`, `target="id-..."`, `xsi:type`.
- O Archi importa o arquivo `.archimate` ou `.xml` diretamente sem perda de conexões.
