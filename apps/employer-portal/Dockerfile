# syntax=docker/dockerfile:1

FROM node:20-bullseye AS builder
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build || echo "Skipping build for placeholder app"

FROM node:20-bullseye AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app .
EXPOSE 3000
CMD ["npm", "run", "start"]
