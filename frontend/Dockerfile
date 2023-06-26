# build stage
FROM node:lts-alpine as build-stage

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY ./ ./

RUN npm run build -- --mode production

# production stage
FROM nginx:stable-alpine as production-stage

COPY .storage/ /etc/nginx/.storage/

RUN mkdir -p /etc/nginx/.storage/logs

COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY .storage/configs/nginx.conf /etc/nginx/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
