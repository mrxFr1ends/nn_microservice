# RabbitMQ Main Configuration
class Rabbit:
    HOST='rabbit_mq'
    PORT=5672
    USER='guest'
    PASSWORD='guest'

# RabbitMQ Main Topic Names
class MainTopic:
    MAIN='manager_in'
    ERROR='error-message'

# RabbitMQ Provider Configuration
class Provider:
    NAME='sklearn_service'
    TOPIC_NAME='sklearn_service_topic'

# Status values
class RequestStatus:
    CREATE='Создать модель'
    TRAIN='Обучить модель'
    PREDICT='Получить предсказание'

class ResponseStatus:
    CREATED='Создана'
    TRAINED='Обучена'
    PREDICTED='Предсказала'