import json
import logging
import os
import time
import traceback

from bird.http.requests_wrapper import post
from bird.utilities.utils import set_alert_log, thread_local

logger = logging.getLogger(__name__)


def call_uv(object_type, object_data, retry_count=0):
    """
    This function makes a DSB call to update UV.  If there is any error retries for 3 times.

    :param object_type: document type that is being passed as input
    :param object_data:  data that is coming as input
    :param retry_count: intializing the retry count to 0
    :return: Either success or error message
    """
    url = f"{os.getenv('DSB_BASE_URL')}{os.getenv('DSB_RESOURCE')}"
    data = {'objectType': object_type, 'objectData': object_data}
    headers = {"Accept": "application/json", "Content-type": "application/json"}
    params = {'requestid': thread_local.correlation_id}
    try:
        response = post(url=url, data=json.dumps(data), headers=headers, params=params).json()

        handle_exception(response, retry_count, object_type, object_data)
    except Exception as ex:
        message = f"An exception of type {type(ex).__name__} occurred. Arguments:{ex.args}"
        raise ProcessException(msg=ex.msg, extended_info=message)


def set_alerts_and_emails(svr_message, message):
    """
    Sets an alert and logs an error which generates an email.

    :param svr_message: svr message generated when thrown an error
    :param message: exception error from try except blocks in call_uv method
    :return: None
    """

    logger.error(f'Reason for failure:  {svr_message}')
    set_alert_log({'error': {'message': message,
                             'traceback': traceback.format_exc()}})

    return None


def handle_exception(response, retry_count, object_type, object_data):
    num_tries = int(os.getenv('MAX_RETRIES', 3))
    response_results = response.get('results', {})
    response_data = response_results.get('results', {}).get('responseData')
    svr_message = response_results.get('results', {}).get('svrMessage')
    svr_status = response.get('results', {}).get('results', {}).get('svrStatus', '')

    if svr_status == '0':
        return logger.debug(f'Success Message:  {response_data}')
    else:
        svr_ctrl_code = response_results.get('results', {}).get('svrCtrlCode', '')
        server_control_code = response.get('universeError', '').get('serverControlCode', '')
        if svr_ctrl_code == "DSB-4_2" or server_control_code == '503':
            if retry_count < num_tries:
                retry_count = retry_count + 1
                back_off = float(os.getenv("BACKOFF_FACTOR", '0.5'))
                try:
                    time.sleep(retry_count * back_off)  # exponential
                    call_uv(object_type, object_data, retry_count)
                except Exception as ex:
                    message = f"An exception of type {type(ex).__name__} occurred. Arguments:{ex.args}"
                    logger.warning(message)
            logger.warning("retry count exceeded")

        raise ProcessException(msg=svr_message, status=svr_status, code=svr_ctrl_code)


class ProcessException(Exception):
    def __init__(self, msg, cause=None, code=None, status=None, extended_info=None):
        self.code = code
        self.cause = cause
        self.msg = msg
        self.status = status
        self.extended_info = extended_info



