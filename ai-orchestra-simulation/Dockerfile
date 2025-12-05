# Multi-stage build for Avatar Renderer
FROM node:18-slim AS builder

# Install build dependencies including canvas requirements
RUN apt-get update && apt-get install -y \
    python3 \
    make \
    g++ \
    pkg-config \
    libpixman-1-dev \
    libcairo2-dev \
    libjpeg-dev \
    libgif-dev \
    librsvg2-dev \
    libpango1.0-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Production stage
FROM node:18-slim AS production

# Install runtime dependencies for canvas
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libjpeg62-turbo \
    libgif7 \
    librsvg2-2 \
    libpango-1.0-0 \
    libpixman-1-0 \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r avatar && useradd -r -g avatar avatar

WORKDIR /app

# Copy package files
COPY package*.json ./

# Copy dependencies from builder
COPY --from=builder /app/node_modules ./node_modules

# Copy application code
COPY . .

# Change ownership
RUN chown -R avatar:avatar /app
USER avatar

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3001/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) }).on('error', () => process.exit(1))"

# Start the application
CMD ["node", "avatar-renderer-v2.js"]