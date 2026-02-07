# --- Stage 1: Build ---
FROM node:20-alpine AS build-stage
WORKDIR /app



COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# --- Stage 2: Production ---
FROM nginx:stable-alpine AS production-stage
# Copie des fichiers buildés depuis le stage précédent
COPY --from=build-stage /app/dist /usr/share/nginx/html
# Copie de la conf Nginx custom
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]