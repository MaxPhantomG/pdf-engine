FROM node:20-alpine

WORKDIR /src

COPY package.json ./
RUN npm install --omit=dev

COPY . .

EXPOSE 8080

CMD ["npm", "start"]

