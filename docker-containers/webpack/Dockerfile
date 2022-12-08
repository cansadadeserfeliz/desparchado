FROM node:18-alpine

WORKDIR /app

COPY run.sh /webpack-run.sh
RUN chmod +x /webpack-run.sh

COPY . .

EXPOSE 3000

CMD ["sh", "/webpack-run.sh"]
