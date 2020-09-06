from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *

import threading
import time


class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)

    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        print('orderStatus - orderid:', orderId, 'status:', status, 'filled',
              filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)

    def openOrder(self, orderId, contract, order, orderState):
        print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange,
              ':', order.action, order.orderType, order.totalQuantity, orderState.status)

    def execDetails(self, reqId, contract, execution):
        print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency,
              execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)

    def position(self, account: str, contract: Contract, position: float, avgCost: float):
        super().position(account, contract, position, avgCost)
        print("Position.", "Account:", account, "Symbol:", contract.symbol, "SecType:",
        contract.secType, "Currency:", contract.currency, "Position:", position, "Avg cost:", avgCost)


def FX_order(symbol):
    contract = Contract()
    contract.symbol = symbol[:3]
    contract.secType = 'CASH'
    contract.exchange = 'IDEALPRO'
    contract.currency = symbol[:3]
    return contract

def createInstance(address,port,client_ID):
    app = IBapi()
    app.connect(address,port,client_ID)
    app.nextorderId = None
    print("within Create")
    return app

print("start of Prog")

def run_loop():
        master_app.run()
        apps.run()


master_app = createInstance('127.0.0.1', 7498, 0)

print("After Master app")

apps = [] 


start_port = 7499
start_client = 1
for i in range(1):
    temp_app = createInstance('127.0.0.1', start_port + i, start_client + i)
    apps.append(temp_app)

# def runMasterLoop():
#     print('68')
#     # master_app.run()
#     print('69')
#     while not isinstance(master_app.nextorderId, int):
#         print('connecting')
#         master_app.run()
#     print('Master App connected')

# runMasterLoop()
# def run_loop():
#     for app in apps:
#         app.run()
#         while not isinstance(app.nextorderId, int):
#             print('connecting')
#             app.run()
#         print('connected')


api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1)
# api_thread2 = threading.Tread(target=run_loop, daemon=True)
# api_thread2.start()


# master_app.reqPositions()

# Create order object
order = Order()
order.action = 'BUY'
order.totalQuantity = 10
order.orderType = 'LMT'
order.lmtPrice = '396'

print("Asdasd",apps[0].nextorderId)
nextorderId = apps[0].nextValidId(apps[0].orderId)
print("Asdasd123",apps[0].nextorderId)
print("123123",master_app.nextorderId) # I think the wrapper is not doing the automatic details to the array due to some restrictions or sth. cos the master_app.nextorderId seems to be updated even before going into the connection check loop

# int(apps[0].nextorderId)

# while True:
#     if isinstance(apps[0].nextorderId, int):
#         print('connected')
#         break
#     else:
#         print('waiting for connection')
#         time.sleep(1)

while True:
    if isinstance(master_app.nextorderId, int):
        print('connected')
        break
    else:
        print('waiting for connection')
        time.sleep(1)        

# apps.placeOrder(apps.nextorderId, FX_order('TSLA'), order)
# master_app.placeOrder(master_app.nextorderId, FX_order('TSLA'), order)
# master_app.cancelOrder(1)

# apps[0].placeOrder(apps[0].nextorderId, FX_order('EURUSD'), order)

print("Asdasd",apps[0].nextorderId)
print("aretyrtyrty",master_app.nextorderId)
