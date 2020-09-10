from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *
from datetime import datetime

import threading
import time


class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)

    def updatePortfolio(self, contract: Contract, position: float, marketPrice: float, marketValue: float, averageCost: float, unrealizedPNL: float, realizedPNL: float, accountName: str):
        super().updatePortfolio(contract, position, marketPrice, marketValue,averageCost, unrealizedPNL, realizedPNL, accountName)
        
        
        if accountName == 'DU2589906' : #put portfolio in child account and update only when position changes
            if not have_order(childportlist, contract.symbol): #reuse function to find (paiseh was lazy/dont know how to code another find function)
                
                    childportlist.append([contract.symbol,position])
            else :
                
                for x in range(len(childportlist)):
                    if(childportlist[x][0] in contract.symbol):  #needs exact match and not substring. Some symbols can be "B" and some symbols can be "BABA". Different stocks
                        if not (childportlist[x][1] == position ):
                            childportlist[x] = [contract.symbol,position]
        for x in range(len(childportlist)): 
            print('child',childportlist[x])

        if accountName == 'DU2309508' : #put portfolio in master account and update only when position changes
            if not have_order(portlist, contract.symbol):
                
                    portlist.append([contract.symbol,position])
            else :
                
                for x in range(len(portlist)):
                    if(portlist[x][0] in contract.symbol): #needs exact match and not substring. Some symbols can be "B" and some symbols can be "BABA". Different stocks
                        if not (portlist[x][1] == position ):
                            portlist[x] = [contract.symbol,position]
        for x in range(len(portlist)): 
            print('Master',portlist[x])
       
        # for child in child_details:
            
        #     i = len(child["positions"])
        #     for i in child["positions"]:
        #         child["positions"].append([contract, position, marketPrice, marketValue,averageCost, unrealizedPNL, realizedPNL, accountName])
        #     print("asdasdasdsad",child["positions"])

        # child_details['positions']['contract'] = contract
        # print(child_details['positions']['contract'])

        # print("UpdatePortfolio.", "Symbol:", contract.symbol, "SecType:", contract.secType, "Exchange:", contract.exchange, "Position:", position, "MarketPrice:", marketPrice,
        #            "MarketValue:", marketValue, "AverageCost:", averageCost,
        #           "UnrealizedPNL:", unrealizedPNL, "RealizedPNL:", realizedPNL,
        #           "AccountName:", accountName)

    def updateAccountTime(self, timeStamp: str):
        super().updateAccountTime(timeStamp)
        print("UpdateAccountTime. Time:", timeStamp)

    def accountDownloadEnd(self, accountName: str):
        super().accountDownloadEnd(accountName)
        print("AccountDownloadEnd. Account:", accountName)

    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
            # need to code cancelling orders here based on orderid (but need to first store pairs)
            print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice, 'clientid', clientId)
            
            if status == 'Cancelled' and orderId < 0:
                for child in child_details:
                    for child_order_list in child['order_list']:
                        if orderId in child_order_list:
                            print(f'Cancelling Master Order Number {orderId}')
                            print(f'Matching Child Order {child_order_list[0]}')
                            child['app'].cancelOrder(child_order_list[0])
                        
                
    def openOrder(self, orderId, contract, order, orderState):
            # Keagan Edit
            # When this is triggered can try to create order to other clients
            
            order_str = f'Open Order to Child:\n' + \
                        f'Master Order ID: {orderId}\n' + \
                        f'Symbol: {contract.symbol} [ {contract.secType} @ {contract.exchange} ]\n' + \
                        f'Action: {order.action} {order.totalQuantity} [{order.orderType}]\n' + \
                        f'Status: {orderState.status}\n\n'
            
            for child in child_details:
                if isinstance(child['app'].nextorderId, int) and orderId < 0:
                    print(f'Manual Order Number {orderId} Received')
                    if not have_order(child['order_list'], orderId):
                        child['order_list'].append( [child['app'].nextorderId, orderId] )
                        print(f'Child [{child["ip_address"]}]: Manual Order ID {orderId} paired with {child["app"].nextorderId}')
                        print(f'Current Order Type: {order.orderType}')
                        print(child['order_list'], '\n\n\n')
                        
                        if contract.secType == "STK":
                            order.totalQuantity //= child["riskdivide"] #need to account for % mod values to prevent misallignment of position sizing (etc B>23 = 4child, B>22 = 4child. S> 22+23 = 45 = 9child. EXTRA ONE... so position -1 instead of 0)
                            #regardless of -ve or +ve will reallign. if zero we go zero.

                            #Wrote draft code in words. Will explain


                        child['app'].placeOrder(child['app'].nextorderId, contract, order) #place order based on client 0 order
                        child['app'].reqIds(child['app'].nextorderId) #reqID increments the next validId *some error.. the api calls this 3 times per trade i do. fking retard. might be because of the threading also. need to do some self check on -id

            print(order_str)
            # print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, order.totalQuantity, orderState.status)
            

    def execDetails(self, reqId, contract, execution):
        print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)

                
def have_order(child_list, orderId):
    if len(child_list) > 0:
        for order_pair in child_list:
            if orderId in order_pair:
                print(f'Order Number {orderId} Found!')
                return True
    return False
    
def child_connect(child_details):
    temp_app = IBapi()
    temp_app.connect(child_details['ip_address'], child_details['port'], child_details['client_id'])
    temp_app.nextorderId = None
    
    temp_thread = threading.Thread(target=temp_app.run, daemon=True)
    temp_thread.start()
    time.sleep(3)
    
    while not isinstance(temp_app.nextorderId, int):
        print(f'Waiting for Child IP [{child_details["ip_address"]}] Connection')
        time.sleep(1)
    print(f'Child IP [{child_details["ip_address"]}] Connected')
    print(f'Child IP [{child_details["ip_address"]}] Current Order: {temp_app.nextorderId}\n\n')
    
    return temp_app



all_orders = []

# Master TWS Settings
master_details = {
    'ip_address': '127.0.0.1',
    'port': 7498,
    'client_id': 0,
    'positions' : {
        # 'contract' : 
        # contract, position, marketPrice, marketValue,averageCost, unrealizedPNL, realizedPNL, accountName
        
    } #dictionary
}

master_app = IBapi()
master_app.connect(master_details['ip_address'], master_details['port'], master_details['client_id'])
master_app.nextorderId = None

master_thread = threading.Thread(target=master_app.run, daemon=True)
master_thread.start()
time.sleep(3)

# While there is no instance, continue while loop
while not isinstance(master_app.nextorderId, int):
    print('Waiting for Master Connection')
    time.sleep(1)
print('Master Connected')
print(f'Master Current Order: {master_app.nextorderId}')


# Child TWS Settings

child_details = [
    {
        'ip_address': '220.255.254.206',
        'port': 7499,
        'client_id': 1,
        'riskdivide' : 5,
        'positions' :  #dunno how to use
        {
            'contract' : None,
            'position' : None, 
            'marketPrice' : None,
            'marketValue' : None,
            'averageCost' : None,
            'unrealizedPNL' : None,
            'realizedPNL' : None,
            'accountName' : None,
        }
    }
]

for i, child_det in enumerate(child_details):
    child_details[i]['app'] = child_connect(child_det)
    child_details[i]['order_list'] = []
    child_details[i]['all_positions'] = []

childportlist = []
portlist = []

master_app.reqAutoOpenOrders(True) #this allows to know what orders are placed because orderid will show up -ve

for child in child_details:
    child['app'].reqAccountUpdates(True, child['app'].clientId)

master_app.reqAccountUpdates(True, master_app.clientId)# request postions will call updatePortfolio()

time.sleep(3)