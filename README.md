# Sklearn Microservice

## Сборка и запуск провайдера:

```
docker build -t sklearn_provider .
docker run sklearn_provider
```

## Сборка и запуск провайдера вместе с сервером RabbitMQ:

```
docker-compose build
docker-compose up
```