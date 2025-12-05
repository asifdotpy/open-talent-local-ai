FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY tsconfig.json ./
COPY src ./src

RUN npm install -g tsx

EXPOSE 3400

CMD ["npx", "tsx", "src/index.ts"]
