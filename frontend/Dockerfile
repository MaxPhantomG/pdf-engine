FROM alpine:3.19 AS builder
WORKDIR /frontend

COPY public /frontend/public
COPY src /frontend/src
COPY src/styles.css /frontend/styles.css

FROM nginx:1.25-alpine

COPY --from=builder /frontend/public /usr/share/nginx/html
COPY --from=builder /frontend/src /usr/share/nginx/html/src
COPY --from=builder /frontend/styles.css /usr/share/nginx/html/styles.css

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
