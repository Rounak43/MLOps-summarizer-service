# =============================================================================
# frontend/Dockerfile
# Multi-stage production Docker recipe for React+Vite frontend
# =============================================================================

# --- Stage 1: Build static assets ---
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package dependencies
COPY package*.json ./
RUN npm ci

# Copy remaining source code and compile Vite bundle
COPY . .
RUN npm run build

# --- Stage 2: Serve compiled assets using Nginx ---
FROM nginx:1.23-alpine

# Copy compiled static assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Write a customized Nginx config inline to support React Router single-page navigation
RUN echo ' \
server { \
    listen 80; \
    server_name localhost; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $$uri $$uri/ /index.html; \
    } \
    error_page 500 502 503 504 /50x.html; \
    location = /50x.html { \
        root /usr/share/nginx/html; \
    } \
} \
' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
