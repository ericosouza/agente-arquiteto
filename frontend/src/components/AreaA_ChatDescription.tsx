import React, { useState, useRef, useEffect } from 'react'
import {
  Send,
  Sparkles,
  MessageSquare,
  Bot,
  User,
  Compass,
  Cpu,
  CheckCircle2,
  Mic,
  MicOff,
} from 'lucide-react'
import type { ChatMessage, PersonaType, PrerequisitesInfo } from '../types/archimate'

interface AreaAProps {
  messages: ChatMessage[]
  isLoading: boolean
  hasProposal: boolean
  persona: PersonaType
  onPersonaChange: (p: PersonaType) => void
  activeMode: 'brainstorm' | 'direct'
  onModeChange: (m: 'brainstorm' | 'direct') => void
  onSendMessage: (text: string) => void
  onTriggerModeling?: () => void
  isReadyForModeling?: boolean
  prerequisites?: PrerequisitesInfo | null
}

const EXAMPLE_PROMPT =
  'Sigla: SESG\nFeature: Cálculo e monitoramento de risco ambiental com Spring Boot, Angular, PubSub e GCS\nARQCOR: ARQ-2026'

export const AreaA_ChatDescription: React.FC<AreaAProps> = ({
  messages,
  isLoading,
  hasProposal,
  persona,
  onPersonaChange,
  activeMode,
  onModeChange,
  onSendMessage,
  onTriggerModeling,
  isReadyForModeling = false,
  prerequisites,
}) => {
  const [inputText, setInputText] = useState('')
  const [isListening, setIsListening] = useState(false)
  const recognitionRef = useRef<any>(null)
  const baseTextRef = useRef<string>('')

  // Limpeza de recursos do microfone ao desmontar o componente
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort()
        } catch {}
      }
    }
  }, [])

  const toggleListening = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

    if (!SpeechRecognition) {
      alert(
        'O reconhecimento de voz pelo microfone (Web Speech API) não está disponível neste navegador. Recomendamos utilizar o Google Chrome ou Microsoft Edge.'
      )
      return
    }

    if (isListening) {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop()
        } catch {}
      }
      setIsListening(false)
      return
    }

    try {
      baseTextRef.current = inputText
      const recognition = new SpeechRecognition()
      recognition.lang = 'pt-BR'
      recognition.continuous = true
      recognition.interimResults = true
      recognition.maxAlternatives = 1

      recognition.onstart = () => {
        setIsListening(true)
      }

      recognition.onresult = (event: any) => {
        let accumulated = ''
        for (let i = 0; i < event.results.length; i++) {
          accumulated += event.results[i][0].transcript + ' '
        }
        const trimmed = accumulated.trim()
        if (trimmed) {
          const base = baseTextRef.current
          const separator = base && !base.endsWith(' ') && !base.endsWith('\n') ? ' ' : ''
          setInputText((base ? base + separator : '') + trimmed)
        }
      }

      recognition.onerror = (event: any) => {
        console.warn('Evento de erro no reconhecimento de voz:', event.error)
        if (event.error === 'not-allowed') {
          alert('Acesso ao microfone negado. Permita a permissão de microfone nas configurações do seu navegador.')
        }
        setIsListening(false)
      }

      recognition.onend = () => {
        setIsListening(false)
      }

      recognitionRef.current = recognition
      recognition.start()
    } catch (err) {
      console.error('Falha ao acionar microfone:', err)
      setIsListening(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputText.trim() || isLoading) return

    // Encerra gravação se estiver ativa ao enviar
    if (isListening && recognitionRef.current) {
      try {
        recognitionRef.current.stop()
      } catch {}
      setIsListening(false)
    }

    onSendMessage(inputText.trim())
    setInputText('')
  }

  const handleUseExample = () => {
    setInputText(EXAMPLE_PROMPT)
  }

  const personaLabel =
    persona === 'arquiteto' ? 'Arquiteto de Software BV' : 'Engenheiro de Software BV'

  return (
    <div className="card area-a-card">
      <div className="card-header" style={{ flexDirection: 'column', alignItems: 'stretch', gap: '8px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div className="card-title">
            <MessageSquare className="text-primary" size={18} />
            <span>Área A — Interação com Persona & RAG</span>
          </div>

          {!hasProposal && (
            <button
              type="button"
              onClick={handleUseExample}
              className="btn-link btn-xs"
              title="Preencher com exemplo padrão BV"
            >
              <Sparkles size={13} />
              <span>Usar Exemplo BV</span>
            </button>
          )}
        </div>

        {/* Barra de Ferramentas de Seleção de Persona */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap', paddingTop: '4px' }}>
          <span style={{ fontSize: '11px', color: '#888', fontWeight: 600 }}>PERSONA:</span>
          <button
            type="button"
            className={`chip-btn ${persona === 'arquiteto' ? 'active-persona' : ''}`}
            onClick={() => onPersonaChange('arquiteto')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 10px',
              borderRadius: '16px',
              border: persona === 'arquiteto' ? '1px solid #3b82f6' : '1px solid #444',
              backgroundColor: persona === 'arquiteto' ? '#1e3a8a' : '#222',
              color: persona === 'arquiteto' ? '#fff' : '#aaa',
              cursor: 'pointer',
              fontSize: '11px',
            }}
          >
            <Compass size={12} />
            <span>Arquiteto de Software</span>
          </button>

          <button
            type="button"
            className={`chip-btn ${persona === 'engenheiro' ? 'active-persona' : ''}`}
            onClick={() => onPersonaChange('engenheiro')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 10px',
              borderRadius: '16px',
              border: persona === 'engenheiro' ? '1px solid #10b981' : '1px solid #444',
              backgroundColor: persona === 'engenheiro' ? '#064e3b' : '#222',
              color: persona === 'engenheiro' ? '#fff' : '#aaa',
              cursor: 'pointer',
              fontSize: '11px',
            }}
          >
            <Cpu size={12} />
            <span>Engenheiro de Software</span>
          </button>
        </div>

        {/* Seletor de Modo */}
        {!hasProposal && (
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center', paddingTop: '2px', fontSize: '12px' }}>
            <span style={{ color: '#888', fontSize: '11px', fontWeight: 600 }}>MODO:</span>
            <label style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer', color: activeMode === 'brainstorm' ? '#93c5fd' : '#888' }}>
              <input
                type="radio"
                name="chatMode"
                value="brainstorm"
                checked={activeMode === 'brainstorm'}
                onChange={() => onModeChange('brainstorm')}
              />
              <span>💡 Brainstorming & RAG (Recomendado)</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer', color: activeMode === 'direct' ? '#93c5fd' : '#888' }}>
              <input
                type="radio"
                name="chatMode"
                value="direct"
                checked={activeMode === 'direct'}
                onChange={() => onModeChange('direct')}
              />
              <span>⚡ Modelagem Direta</span>
            </label>
          </div>
        )}

        {/* Badges de Progresso do Fluxograma */}
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', paddingTop: '4px' }}>
          <span style={{
            fontSize: '10.5px',
            padding: '2px 8px',
            borderRadius: '10px',
            backgroundColor: prerequisites?.sigla ? '#14532d' : '#27272a',
            color: prerequisites?.sigla ? '#86efac' : '#71717a',
            border: prerequisites?.sigla ? '1px solid #22c55e' : '1px solid #3f3f46'
          }}>
            {prerequisites?.sigla ? `✓ Sigla: ${prerequisites.sigla.toUpperCase()}` : '○ Sigla: Pendente'}
          </span>

          <span style={{
            fontSize: '10.5px',
            padding: '2px 8px',
            borderRadius: '10px',
            backgroundColor: prerequisites?.feature ? '#14532d' : '#27272a',
            color: prerequisites?.feature ? '#86efac' : '#71717a',
            border: prerequisites?.feature ? '1px solid #22c55e' : '1px solid #3f3f46'
          }}>
            {prerequisites?.feature ? '✓ Feature: OK' : '○ Feature: Pendente'}
          </span>

          <span style={{
            fontSize: '10.5px',
            padding: '2px 8px',
            borderRadius: '10px',
            backgroundColor: prerequisites?.arqcor ? '#14532d' : '#27272a',
            color: prerequisites?.arqcor ? '#86efac' : '#71717a',
            border: prerequisites?.arqcor ? '1px solid #22c55e' : '1px solid #3f3f46'
          }}>
            {prerequisites?.arqcor ? `✓ ARQCOR: ${prerequisites.arqcor}` : '○ ARQCOR: Pendente'}
          </span>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty-state">
            <Bot size={40} className="text-muted" />
            <p>
              Olá! Sou o seu <strong>{personaLabel}</strong>.
            </p>
            <p className="text-secondary text-sm">
              {activeMode === 'brainstorm'
                ? 'Estou pronto para debater ideias inovadoras de arquitetura, consultar a base de conhecimento de tecnologia do BV e estruturar sua solução sob medida.'
                : 'Descreva a necessidade do seu sistema informando Sigla (4 letras), Feature e ARQCOR para iniciarmos a modelagem oficial ArchiMate.'}
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`chat-bubble ${
                msg.role === 'user'
                  ? 'chat-bubble-user'
                  : msg.role === 'assistant'
                  ? 'chat-bubble-assistant'
                  : 'chat-bubble-system'
              }`}
            >
              <div className="chat-bubble-header">
                <div className="chat-bubble-author">
                  {msg.role === 'user' ? (
                    <User size={13} />
                  ) : msg.role === 'assistant' ? (
                    persona === 'engenheiro' ? <Cpu size={13} color="#10b981" /> : <Compass size={13} color="#60a5fa" />
                  ) : (
                    <Bot size={13} />
                  )}
                  <span>
                    {msg.role === 'user'
                      ? 'Você'
                      : msg.role === 'assistant'
                      ? personaLabel
                      : 'Sistema'}
                  </span>
                </div>
                {msg.timestamp && (
                  <span className="chat-bubble-time">{msg.timestamp}</span>
                )}
              </div>
              <div className="chat-bubble-content">
                {msg.content.split('\n').map((line, i) => (
                  <p key={i}>{line}</p>
                ))}
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="chat-bubble chat-bubble-assistant">
            <div className="chat-bubble-header">
              <div className="chat-bubble-author">
                <Bot size={13} />
                <span>{personaLabel} pensando...</span>
              </div>
            </div>
            <div className="chat-bubble-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Chamada para Ação: Pronto para Modelagem no modo Brainstorming */}
      {activeMode === 'brainstorm' && (isReadyForModeling || messages.length >= 2) && onTriggerModeling && !hasProposal && (
        <div style={{ padding: '8px 12px', background: '#1e3a8a22', borderTop: '1px solid #1e3a8a', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#93c5fd' }}>
            <CheckCircle2 size={16} color="#60a5fa" />
            <span>Refinamento alinhado? Pronto para gerar o modelo ArchiMate.</span>
          </div>
          <button
            type="button"
            onClick={onTriggerModeling}
            className="btn-primary"
            style={{ padding: '4px 12px', fontSize: '12px' }}
            disabled={isLoading}
          >
            Prosseguir para Modelagem (Ok)
          </button>
        </div>
      )}

      <form onSubmit={handleSubmit} className="chat-input-form">
        {/* Indicador visual de gravação de voz ativa */}
        {isListening && (
          <div className="voice-recording-indicator">
            <span className="recording-dot" />
            <span>Gravando áudio (pt-BR)... Fale agora para preencher o campo.</span>
          </div>
        )}

        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={
            hasProposal
              ? 'Deseja alterar o desenho? Ex: "Adicione um pubsub", "Troque o front para streamlit", "Adicione um sbatch"...'
              : activeMode === 'brainstorm'
              ? 'Debata com a Persona: faça perguntas de arquitetura, peça alternativas ou confirme com "Ok, pode modelar"...'
              : 'Informe: Sigla (4 letras), Feature e ARQCOR e descreva a necessidade do sistema...'
          }
          className={`chat-textarea ${isListening ? 'chat-textarea-listening' : ''}`}
          rows={3}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSubmit(e)
            }
          }}
          disabled={isLoading}
        />
        <div className="chat-form-footer">
          <span className="form-hint">
            Pressione <strong>Enter</strong> para enviar ou <strong>Shift+Enter</strong> para quebrar linha
          </span>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            {/* Botão de Microfone / Gravação por Voz */}
            <button
              type="button"
              onClick={toggleListening}
              className={`btn-mic ${isListening ? 'listening' : ''}`}
              title={isListening ? 'Clique para parar a gravação de voz' : 'Falar por voz (Ditado em Português)'}
              disabled={isLoading}
            >
              {isListening ? <MicOff size={15} /> : <Mic size={15} />}
              <span>{isListening ? 'Ouvindo...' : 'Falar'}</span>
            </button>

            {/* Botão de Envio de Mensagem */}
            <button
              type="submit"
              disabled={!inputText.trim() || isLoading}
              className="btn-primary"
            >
              <Send size={15} />
              <span>
                {hasProposal
                  ? 'Ajustar Arquitetura'
                  : activeMode === 'brainstorm'
                  ? 'Brainstorm com Persona'
                  : 'Analisar e Propor'}
              </span>
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
