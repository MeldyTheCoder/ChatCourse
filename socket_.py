import fastapi
from fastapi_socketio import socket_manager


def get_sio_for_app(app: fastapi.FastAPI):
    return socket_manager.SocketManager(
        app=app,
        mount_location='/socket.io',
        cors_allowed_origins=['*'],
        ping_timeout=15000,
        ping_interval=20000,
        always_connect=True,
    )
