import React, { useState } from 'react'
import { Send, Sparkles, MessageSquare, Bot, User } from 'lucide-react'
import type { ChatMessage } from '../types/archimate'

interface AreaAProps {
  messages: ChatMessage[]
  isLoading: boolean
  hasProposal: boolean
  onSendMessage: (text: string) => void
}

const EXAMPLE_PROMPT =
  'Quero desenvolver um sistema web para cadastro, consulta, alteração e exclusão de produtos. O sistema deve permitir que usuários pesquisem produtos por nome, categoria e preço.'

export const AreaA_ChatDescription: React.FC<AreaAProps> = ({
  messages,
  isLoading,
  hasProposal,
  onSendMessage,
}) => {
  const [inputText, setInputText] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputText.trim() || isLoading) return
    onSendMessage(inputText.trim())
    setInputText('')
  }

  const handleUseExample = () => {
    setInputText(EXAMPLE_PROMPT)
  }

  return (
    <div className="card area-a-card">
      <div className="card-header">
        <div className="card-title">
          <MessageSquare className="text-primary" size={18} />
          <span>Área A — Descrição da Arquitetura & Chat</span>
        </div>
        {!hasProposal && (
          <button
            type="button"
            onClick={handleUseExample}
            className="btn-link btn-xs"
            title="Preencher com o exemplo padrão de cadastro de produtos"
          >
            <Sparkles size={13} />
            <span>Usar Exemplo de Produtos</span>
          </button>
        )}
      </div>

      <div className="chat-messages-container">
        {messages.length === 0 ? (
          <div className="chat-empty-state">
            <Bot size={36} className="text-muted" />
            <h4>Olá! Sou o seu Arquiteto de Software ArchiMate.</h4>
            <p>
              Descreva em linguagem natural o sistema que deseja construir. Analisarei os
              componentes, camadas, integrações e gerarei um modelo oficial ArchiMate 3.2.
            </p>
            <div className="chat-suggestions">
              <span className="suggestion-label">Exemplos rápidos:</span>
              <button
                className="chip-btn"
                onClick={() => onSendMessage(EXAMPLE_PROMPT)}
                disabled={isLoading}
              >
                📦 Cadastro de Produtos (CRUD e Busca)
              </button>
              <button
                className="chip-btn"
                onClick={() =>
                  onSendMessage(
                    'Sistema de e-commerce com catálogo de produtos, carrinho, processamento de pagamentos com fila assíncrona RabbitMQ e banco PostgreSQL.'
                  )
                }
                disabled={isLoading}
              >
                🛒 E-commerce com Mensageria
              </button>
            </div>
          </div>
        ) : (
          <div className="chat-history">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`chat-bubble-wrapper ${
                  msg.role === 'user' ? 'bubble-user' : 'bubble-assistant'
                }`}
              >
                <div className="bubble-avatar">
                  {msg.role === 'user' ? <User size={15} /> : <Bot size={15} />}
                </div>
                <div className="bubble-content">
                  <div className="bubble-header">
                    <span className="bubble-author">
                      {msg.role === 'user' ? 'Você' : 'Arquiteto de Soluções'}
                    </span>
                    <span className="bubble-time">{msg.timestamp}</span>
                  </div>
                  <div className="bubble-text">{msg.content}</div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="chat-bubble-wrapper bubble-assistant">
                <div className="bubble-avatar">
                  <Bot size={15} />
                </div>
                <div className="bubble-content bubble-loading">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span className="loading-text">
                    Arquiteto analisando requisitos e estruturando proposta ArchiMate...
                  </span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={
            hasProposal
              ? 'Deseja alterar algo? Ex: "Mude o banco para MySQL", "Adicione Redis", "Troque React por Angular"...'
              : 'Descreva seu sistema (ex: "Quero desenvolver um sistema web para cadastro de produtos com busca...")'
          }
          className="chat-textarea"
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
          <button
            type="submit"
            disabled={!inputText.trim() || isLoading}
            className="btn-primary"
          >
            <Send size={15} />
            <span>{hasProposal ? 'Ajustar Arquitetura' : 'Analisar e Propor'}</span>
          </button>
        </div>
      </form>
    </div>
  )
}
