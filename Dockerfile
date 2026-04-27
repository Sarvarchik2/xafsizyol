# Build stage
FROM node:18 AS build-stage

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies without running postinstall scripts
RUN npm install --legacy-peer-deps --ignore-scripts

# Copy project files
COPY . .

# Explicitly run nuxt prepare and then build
RUN npx nuxt prepare
RUN npm run build

# Production stage
FROM node:18-alpine

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
