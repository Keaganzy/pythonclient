from Client import Client
import logging
import threading
import time

def ib_connect(client_details):
    ip_address = client_details['ip_address']
    port = client_details['port']
    client_id = client_details['client_id']

    app = Client(client_id)
    app.connect(ip_address, port, client_id)
    app.nextorderId = None

    thread = threading.Thread(target=app.run, daemon=True)
    thread.start()

    while not isinstance(app.nextorderId, int):
        time.sleep(1)
    logging.info(f'Connected to Client {client_id} on {ip_address}')
    logging.info(f'Client {client_id} Current Order: {app.nextorderId}')

    return app


