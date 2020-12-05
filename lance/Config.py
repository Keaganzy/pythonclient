import os
import json
import uuid

def get_ip_address():
    def check_ip_octet(octet):
        if octet >= 0 and octet <= 255:
            return True
        return False

    ip_address = ''
    valid_ip = False

    while not valid_ip:
        ip_address = input("Please enter client's IP Address: ")
        valid_ip = True
        for octet in ip_address.split('.'):
            if octet.isdigit():
                valid_ip = valid_ip and check_ip_octet(int(octet))
            else:
                valid_ip = False
        
        if not valid_ip:
            print('Invalid IP Address, Please enter again')
        
    return ip_address
    

def get_port():
    port = 0

    while port < 1 or port > 65535:
        port = input("Please enter client's port number: ")
        if not port.isdigit() or (int(port) < 1 or int(port) > 65535):
            port = 0
            print('Invalid Port Number, please enter again')
        else:
            port = int(port)

    return port


def get_account_name():
    return input('Please enter account name (Press enter to leave it blank):')


def get_risk():
    risk_divide = -1

    while risk_divide < 0:
        risk_divide = input("Please enter client risk: ")
        if not risk_divide.isdigit():
            print("Invalid risk. Please enter again")
        else:
            risk_divide = int(risk_divide)

    return risk_divide

# Initial Check for Config Folders
if not os.path.exists('client_config'):
    os.makedirs('client_config')
    os.chdir('client_config')
else:
    os.chdir('client_config')

# ip_address = get_ip_address()
# port = get_port()
# account_name = get_account_name()
# risk_divide = get_risk()

data = {
    'ip_address': get_ip_address(),
    'port': get_port(),
    'account_name': get_account_name(),
    'risk_divide': get_risk()
}


id = uuid.uuid1()
filename = id.hex + '.json'

with open(filename, 'w') as f:
    json.dump(data, f)
    print('\nClient profile created!')