# Frontend Dockerfile
FROM node:19.0.0

# Set the working directory
WORKDIR /app

# Install necessary build tools
RUN apt-get update && \
    apt-get install -y python3 make g++ && \
    rm -rf /var/lib/apt/lists/*

# Copy package files
COPY package*.json ./

# Install dependencies with specific platform
RUN npm install --platform=linux --arch=x64

# Install vite globally
RUN npm install -g vite

# Copy the rest of the application
COPY . .

# Build the application to ensure all dependencies are properly installed
RUN npm install

# Expose port 8080
EXPOSE 8080

# Start the application
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]