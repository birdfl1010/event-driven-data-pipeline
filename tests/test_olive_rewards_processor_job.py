import uuid

from bird.job.micro_job import process_message

__initial_author__ = 'Middleware Architecture Team'
__dev_team__ = 'Middleware Architecture Team'
__copyright__ = 'Bird Inc / SHOP.com'


def test_job():
    message = {
        'id': uuid.uuid4(),
        'message': 'sample message'
    }
    process_message(message)


def test_server_module():
    from bird.server.pytato_server import app
    assert app is not None
    assert len(app.jobs) > 0
