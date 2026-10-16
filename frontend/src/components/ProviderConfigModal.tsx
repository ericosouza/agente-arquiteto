import React from 'react'
import { X, Cpu, CheckCircle2, ShieldCheck } from 'lucide-react'
import type { SystemInfo } from '../types/archimate'

interface ProviderConfigModalProps {
  systemInfo: SystemInfo | null
  onClose: () => void
}

export const ProviderConfigModal: React.FC<ProviderConfigModalProps> = ({
  systemInfo,
  onClose,
}) => {
  const providers = systemInfo?.providers || {}
  const active = systemInfo?.activeProvider || 'builtin'

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <div className="modal-header">
          <div className="modal-title-row">
            <Cpu size={20} className="text-primary" />
            <h4>Configuração dos Provedores de IA</h4>
          </div>
          <button onClick={onClose} className="btn-icon">
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          <div className="alert-box alert-info">
            <ShieldCheck size={18} />
            <div>
              <strong>Segurança e Baixo Custo:</strong> As chaves de API nunca são expostas no
              navegador. Elas residem com segurança no arquivo <code>.env</code> do backend.
            </div>
          </div>

          <div className="providers-list">
            {/* Built-in Expert Engine */}
            <div
              className={`provider-item ${
                active === 'builtin' ? 'provider-active-card' : ''
              }`}
            >
              <div className="provider-item-header">
                <div className="provider-name-block">
                  <strong>Motor Especialista Embutido (Offline)</strong>
                  <span className="badge-free">100% Gratuito & Ilimitado</span>
                </div>
                {active === 'builtin' && (
                  <span className="badge-active">
                    <CheckCircle2 size={13} /> Ativo Agora
                  </span>
                )}
              </div>
              <p className="provider-desc">
                Motor determinístico com regras e raciocínio de soluções de arquitetura de software
                (monolito vs microsserviços, escolhas de camadas, ArchiMate 3.2). Não requer chaves de
                API ou internet.
              </p>
            </div>

            {/* Google Gemini */}
            <div
              className={`provider-item ${
                active === 'gemini' ? 'provider-active-card' : ''
              }`}
            >
              <div className="provider-item-header">
                <div className="provider-name-block">
                  <strong>Google Gemini API</strong>
                  <span className="badge-cloud">Nuvem</span>
                </div>
                {active === 'gemini' ? (
                  <span className="badge-active">
                    <CheckCircle2 size={13} /> Ativo Agora
                  </span>
                ) : (
                  <span className="badge-inactive">
                    {providers.gemini?.configured ? 'Configurado' : 'Não Configurado'}
                  </span>
                )}
              </div>
              <p className="provider-desc">
                {providers.gemini?.instructions || 'Configure GEMINI_API_KEY no arquivo .env'}
              </p>
              <div className="env-sample-code">
                <code>GEMINI_API_KEY=sua_chave_do_google_aistudio</code>
              </div>
            </div>

            {/* OpenAI */}
            <div
              className={`provider-item ${
                active === 'openai' ? 'provider-active-card' : ''
              }`}
            >
              <div className="provider-item-header">
                <div className="provider-name-block">
                  <strong>OpenAI (GPT-4o / GPT-4o-mini)</strong>
                  <span className="badge-cloud">Nuvem</span>
                </div>
                {active === 'openai' ? (
                  <span className="badge-active">
                    <CheckCircle2 size={13} /> Ativo Agora
                  </span>
                ) : (
                  <span className="badge-inactive">
                    {providers.openai?.configured ? 'Configurado' : 'Não Configurado'}
                  </span>
                )}
              </div>
              <p className="provider-desc">
                {providers.openai?.instructions || 'Configure OPENAI_API_KEY no arquivo .env'}
              </p>
              <div className="env-sample-code">
                <code>OPENAI_API_KEY=sk-...</code>
              </div>
            </div>

            {/* Ollama Local */}
            <div
              className={`provider-item ${
                active === 'ollama' ? 'provider-active-card' : ''
              }`}
            >
              <div className="provider-item-header">
                <div className="provider-name-block">
                  <strong>Ollama (Execução 100% Local)</strong>
                  <span className="badge-free">Gratuito / Local</span>
                </div>
                {active === 'ollama' && (
                  <span className="badge-active">
                    <CheckCircle2 size={13} /> Ativo Agora
                  </span>
                )}
              </div>
              <p className="provider-desc">
                Executa modelos abertos (Llama 3.2, Mistral, Qwen) diretamente no seu computador sem enviar dados para a nuvem.
              </p>
              <div className="env-sample-code">
                <code>LLM_PROVIDER=ollama</code>
                <br />
                <code>OLLAMA_MODEL=llama3.2</code>
              </div>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button onClick={onClose} className="btn-primary">
            Entendido
          </button>
        </div>
      </div>
    </div>
  )
}
