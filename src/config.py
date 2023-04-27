from request_handlers import create_model, train_model, model_predict


class RabbitConfig:
    # RabbitMQ Main Configuration
    HOST = 'rabbit_mq'
    PORT = 5672
    USER = 'guest'
    PASSWORD = 'guest'


class MainTopic:
    # RabbitMQ Main Topic Names
    MAIN = 'manager_in'
    ERROR = 'error-message'


class ProviderConfig:
    # RabbitMQ Provider Configuration
    NAME = 'sklearn_service'
    TOPIC_NAME = 'sklearn_service_topic'


class RequestStatus:
    # Status values
    CREATE = 'CREATE'
    TRAIN = 'TRAIN'
    PREDICT = 'PREDICT'


def REGISTER_MESSAGE(algorithms):
    return {
        "provider": ProviderConfig.NAME,
        "topic": ProviderConfig.TOPIC_NAME,
        "algorithms": [{
            "algorithmName": alg,
            "hyperparameters": [{
                'descriptionFlag': p[0],
                'description': p[1]
            } for p in params]
        } for alg, params in algorithms.items()]
    }


def ERROR_MESSAGE(model_id, errorType, errorMessage, datetime):
    return {
        "modelId": model_id,
        "errorType": errorType,
        "errorMessage": errorMessage,
        "localDateTime": datetime
    }


REQUEST_HANDLER_MAP = {
    RequestStatus.CREATE: {
        'request_handler': create_model,
        'comp_request_keys': {
            'model_name': 'classifier',
            'raw_params': 'options'
        },
        'comp_response_keys': {
            'serialized_model': {'serializedModelData': ['model']}
        },
        'topic_name': MainTopic.MAIN
    },
    RequestStatus.TRAIN: {
        'request_handler': train_model,
        'comp_request_keys': {
            'serialized_model': {'serializedModelData': ['model']},
            'features': 'features',
            'labels': 'labels'
        },
        'comp_response_keys': {
            'serialized_model': {'serializedModelData': ['model']},
            'metrics': 'metrics'
        },
        'topic_name': MainTopic.MAIN
    },
    RequestStatus.PREDICT: {
        'request_handler': model_predict,
        'comp_request_keys': {
            'serialized_model': {'serializedModelData': ['model']},
            'features': 'features'
        },
        'comp_response_keys': {
            'predict_labels': {'serializedModelData': ['labels']},
            'predict_proba': {'serializedModelData': ['distributions']}
        },
        'topic_name': MainTopic.MAIN
    }
}
