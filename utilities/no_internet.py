import socket
from urllib.parse import urlparse

_patched = False

def restrict_network(db_uri):
    """Disable outgoing connections except to the host/port in db_uri."""
    parsed = urlparse(db_uri)
    allowed_host = parsed.hostname
    allowed_port = parsed.port or 5432

    global _patched
    if _patched:
        return
    _patched = True

    orig_create_connection = socket.create_connection
    orig_connect = socket.socket.connect
    orig_connect_ex = socket.socket.connect_ex

    def guarded_create_connection(address, *args, **kwargs):
        host, port = address[0], address[1]
        if host == allowed_host and port == allowed_port:
            return orig_create_connection(address, *args, **kwargs)
        raise RuntimeError("Network disabled by --nointernet")

    def guarded_connect(self, address):
        host, port = address[0], address[1]
        if host == allowed_host and port == allowed_port:
            return orig_connect(self, address)
        raise RuntimeError("Network disabled by --nointernet")

    def guarded_connect_ex(self, address):
        host, port = address[0], address[1]
        if host == allowed_host and port == allowed_port:
            return orig_connect_ex(self, address)
        raise RuntimeError("Network disabled by --nointernet")

    socket.create_connection = guarded_create_connection
    socket.socket.connect = guarded_connect
    socket.socket.connect_ex = guarded_connect_ex
