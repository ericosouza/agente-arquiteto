# ==========================================================
# Agente Arquiteto de Software - Frontend (React 19 + Vite 6 + Nginx)
# ==========================================================

# Estágio 1: Build da aplicação React/TypeScript
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Estágio 2: Servidor Web Nginx de produção
FROM nginx:alpine

# Copia arquivos estáticos compilados do estágio anterior
COPY --from=builder /app/dist /usr/share/nginx/html

# Configuração personalizada do Nginx com proxy reverso para /api
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
