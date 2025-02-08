import pytest
from unittest.mock import Mock
import docker
from .app import app


def pytest_addoption(parser):
    parser.addoption(
        "--use-docker",
        action="store_true",
        default=False,
        help="Run tests with the real docker integration"
    )


# @pytest.fixture
# def docker_integration(request, monkeypatch):
#     use_docker = request.config.getoption("--use-docker")
#     if not use_docker:
#         mock_container = Mock()
#         mock_container.logs.return_value = [b'Test log output']
#         mock_container.wait.return_value = {'StatusCode': 0}
#         mock_client = Mock()
#         mock_client.containers.run.return_value = mock_container
#         monkeypatch.setattr(app, "get_docker_client", lambda: mock_client)
#         return mock_client
#     else:
#         return docker.from_env() 
