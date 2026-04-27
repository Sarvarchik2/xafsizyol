# Build stage
FROM node:22 AS build-stage

WORKDIR /app

# Copy package.json (don't rely on package-lock.json for architecture-specific native bindings)
COPY package.json ./

# Install dependencies from scratch for the container's architecture
RUN rm -f package-lock.json && npm install --legacy-peer-deps

# Copy project files
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:22-alpine

WORKDIR /app

# Copy the built output and package files from the build-stage
COPY --from=build-stage /app/.output ./.output
COPY --from=build-stage /app/package*.json ./

# Expose the port Nuxt will run on
EXPOSE 3000

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=3000
ENV NODE_ENV=production

# Start the application
CMD ["node", ".output/server/index.mjs"]
