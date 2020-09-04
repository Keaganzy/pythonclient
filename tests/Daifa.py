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
    contract.currency = symbol[3:]
    return contract

def createInstance(address,port,client_ID):
    app = IBapi()
    app.connect(address,port,client_ID)
    app.nextorderId = None
    print("within Create")
    return app

print("start of Prog")

master_app = createInstance('127.0.0.1', 7498, 1)

print("After Master app")

# apps = [] 


# start_port = 7499
# start_client = 124
# for i in range(1):
#     temp_app = createInstance('127.0.0.1', start_port + i, start_client + i)
#     apps.append(temp_app)

def runMasterLoop():
    print('68')
    master_app.run()
    print('69')
    while not isinstance(master_app.nextorderId, int):
        print('connecting')
        # master_app.run()
    print('Master App connected')

runMasterLoop()
# def run_loop():
#     for app in apps:
#         app.run()
#         while not isinstance(app.nextorderId, int):
#             print('connecting')
#             app.run()
#         print('connected')


# api_thread = threading.Thread(target=runMasterLoop, daemon=True)
# api_thread.start()
# api_thread2 = threading.Tread(target=run_loop, daemon=True)
# api_thread2.start()
