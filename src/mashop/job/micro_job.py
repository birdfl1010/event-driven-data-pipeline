import json
import logging
import os
import uuid

from kafka import KafkaConsumer
from bird.utilities import thread_local
from bird.utilities.decorators import elapsed_time

from bird.job import package_name
from bird.job.utils import call_uv, set_alerts_and_emails, ProcessException

logger = logging.getLogger(__name__)

kafka_consumer = None  # type: KafkaConsumer


def run(params):
    global kafka_consumer

    logger.info(f'Job {package_name} Started')

    logger.debug('Connecting to Kafka...')
    # consume vendor-rewards microservice topic:
    kafka_consumer = KafkaConsumer(
        os.getenv('APP_KAFKA_TOPIC'),
        bootstrap_servers=os.getenv('APP_KAFKA_HOSTS'),
        group_id=os.getenv('APP_KAFKA_GROUP_ID'),
        auto_offset_reset=os.getenv('APP_KAFKA_SETTINGS_AUTOOFFSETRESET'),
        enable_auto_commit=os.getenv('APP_KAFKA_SETTINGS_AUTOCOMMIT'))

    logger.info(f'Waiting for messages... in TOPIC: [{os.getenv("APP_KAFKA_TOPIC")}]')
    for msg in kafka_consumer:
        logger.debug(f'Message received. Data {msg}')
        msg = json.loads(msg.value.decode('utf-8'))
        try:
            process_message(msg)
        except ProcessException as ex:
            message = f"An exception of type {type(ex).__name__} occurred. Arguments:{ex.args}"
            set_alerts_and_emails(svr_message=ex.msg, message=message)
        except Exception as ex:
            message = f"An unexpected exception of type {type(ex).__name__} occurred. Arguments:{ex.args}"
            set_alerts_and_emails(svr_message=message, message=message)

    logger.info(f'Job {package_name}  Ended')


@elapsed_time
def process_message(msg):
    logger.debug('Processing message...')
    # STEP 1 - extract global properties like correlation_id
    correlation_id = msg.get('correlation_id') or str(uuid.uuid4())
    thread_local.correlation_id = correlation_id

    # STEP 2 - extract uv required properties (object_type and object_data)
    object_type = msg.get('object_type')
    object_data = msg.get('object_data')

    # STEP 3 - call UV through DSB
    call_uv(object_type, object_data)

    # STEP 4 - log result, send notification if failed
    logger.debug('Done processing message...')
