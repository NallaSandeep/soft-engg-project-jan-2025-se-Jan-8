# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies first for better caching
COPY studyhub/frontend/package*.json ./
RUN npm install

# Copy application code
COPY studyhub/frontend/ .

# Add curl for healthcheck
RUN apk add --no-cache curl

EXPOSE 3000

# Set environment variables
ENV NODE_ENV=development
ENV REACT_APP_API_URL=http://localhost:5000
ENV REACT_APP_INDEXER_URL=http://localhost:8000
ENV WDS_SOCKET_PORT=0

# Add health check script
COPY docker/frontend/health-check.sh /health-check.sh
RUN chmod +x /health-check.sh

HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
    CMD /health-check.sh

# Use development server with hot reloading
CMD ["npm", "start"]