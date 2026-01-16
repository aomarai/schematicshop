FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN if [ -f package-lock.json ]; then \
		npm ci; \
	else \
		npm install; \
	fi

# Copy app files
COPY . .

# Build app
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
