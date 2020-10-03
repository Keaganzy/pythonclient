from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *
from datetime import datetime

import threading
import time
import json


class IBapi(EWrapper, EClient):
    def __init__(self, client_id):
        EClient.__init__(self, self)
        self.client_id = client_id

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)

    def updateAccountValue(self, key: str, val: str, currency: str, accountName: str):
        super().updateAccountValue(key, val, currency, accountName)
        # print("UpdateAccountValue. Key:", key, "Value:", val,"Currency:", currency, "AccountName:", accountName)

    def updatePortfolio(self, contract: Contract, position: float, marketPrice: float, marketValue: float, averageCost: float, unrealizedPNL: float, realizedPNL: float, accountName: str):
        super().updatePortfolio(contract, position, marketPrice, marketValue,averageCost, unrealizedPNL, realizedPNL, accountName)
        
        if self.client_id == 0: #master update positions size
            try:
                master_details['positions'][contract.symbol] = position
            except:
                master_details['positions'] = {contract.symbol: position}
            pass
            # Master ID
        else:
            try:
                child_details[self.client_id - 1]['positions'][contract.symbol] = position #child update positions size based on clientID
            except:
                child_details[self.client_id - 1]['positions'] = {contract.symbol: position}
      
        for child in child_details: #gets the difference in dict to find positions not the same
            A = list(child['positions'].keys())
            B = list(master_details['positions'].keys())
            commonKeys = set(A) - (set(A) - set(B))
            for key in commonKeys:
                if((child['positions'][key]) * child['risk_divide'] != (master_details['positions'][key])):
                    print(key ,":" ,(child['positions'][key]) , " should be " , (master_details['positions'][key]), "risk mul:", child['risk_divide'])
                    
                    if((child['positions'][key]) > 0 and master_details['positions'][key] > 0 ): #give binary to child
                        child['binary_indicator'][key] = [0,0]
                    if((child['positions'][key]) > 0 and master_details['positions'][key] < 0 ):
                        child['binary_indicator'][key] = [0,1]
                    if((child['positions'][key]) < 0 and master_details['positions'][key] > 0 ):
                        child['binary_indicator'][key] = [1,0]
                    if((child['positions'][key]) < 0 and master_details['positions'][key] < 0 ):
                        child['binary_indicator'][key] = [1,1]

                if((child['positions'][key]) * child['risk_divide'] == (master_details['positions'][key])):          
                    child['binary_indicator'][key] = None

        for child in child_details:
            print(json.dumps(child['binary_indicator']))
            print(json.dumps(child['positions']))

        # print("UpdatePortfolio.", "Symbol:", contract.symbol, "SecType:", contract.secType, "Exchange:", contract.exchange, "Position:", position, "MarketPrice:", marketPrice,
        #            "MarketValue:", marketValue, "AverageCost:", averageCost,
        #           "UnrealizedPNL:", unrealizedPNL, "RealizedPNL:", realizedPNL,
        #           "AccountName:", accountName)

    def updateAccountTime(self, timeStamp: str):
        super().updateAccountTime(timeStamp)
        # print("UpdateAccountTime. Time:", timeStamp)

    def accountDownloadEnd(self, accountName: str):
        super().accountDownloadEnd(accountName)
        print("AccountDownloadEnd. Account:", accountName)
        # child_details[0]['all_positions']['FB']= 9.0
        # for child in child_details:
        #     print(accountName,child["account_name"],";",json.dumps(child['all_positions']))
            

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
            # print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, order.totalQuantity, orderState.status)    
            order_str = f'Open Order to Child:\n' + \
                        f'Master Order ID: {orderId}\n' + \
                        f'Symbol: {contract.symbol} [ {contract.secType} @ {contract.exchange} ]\n' + \
                        f'Action: {order.action} {order.totalQuantity} [{order.orderType}]\n' + \
                        f'Status: {orderState.status}\n\n'
            totalQ = order.totalQuantity
            # # if orderState.status == 'PreSubmitted':
            # #     pass
            # else:
            for child in child_details:
                if isinstance(child['app'].nextorderId, int) and orderId < 0:
                    print(f'Manual Order Number {orderId} Received')
                    if not have_order(child['order_list'], orderId):
                        child['order_list'].append( [child['app'].nextorderId, orderId] )
                        print(f'Child [{child["ip_address"]}]: Manual Order ID {orderId} paired with {child["app"].nextorderId}')
                        print(f'Current Order Type: {order.orderType}')
                        print(child['order_list'], '\n\n\n')
                        TQ = order.totalQuantity 
                        if contract.secType == "STK":
                            if (contract.symbol in (child['binary_indicator'].keys())): #search dict for contract
                                print('Found binary indicator')

                                if (child['binary_indicator'].get(contract.symbol) == [0,0] or child['binary_indicator'].get(contract.symbol) == [1,1]):    #if child has more position. Dont buy
                                    if((order.totalQuantity//child["risk_divide"]) + (abs(master_details['positions'].get(contract.symbol))//child["risk_divide"]) < abs(child['positions'].get(contract.symbol))):
                                        break

                                if (order.action == 'BUY'):
                                    print(child['binary_indicator'].get(contract.symbol))

                                    if (child['binary_indicator'].get(contract.symbol) == [0,0]):
                                        if((order.totalQuantity//child["risk_divide"]) + (master_details['positions'].get(contract.symbol)//child["risk_divide"]) > child['positions'].get(contract.symbol)):
                                            order.totalQuantity = (order.totalQuantity//child["risk_divide"]) + (master_details['positions'].get(contract.symbol)//child["risk_divide"]) - child['positions'].get(contract.symbol)
                                            child['app'].placeOrder(child['app'].nextorderId, contract, order) #place order based on client 0 order
                                            child['app'].reqIds(child['app'].nextorderId)
                                            order.totalQuantity = totalQ
                                    
                                    if (child['binary_indicator'].get(contract.symbol) == [0,1]):
                                        if(order.totalQuantity <= abs(master_details['positions'].get(contract.symbol))):
                                            OA = order.action
                                            OT = order.orderType
                                            order.action = 'SELL'
                                            order.orderType = "MKT"
                                            order.totalQuantity = abs(child['positions'].get(contract.symbol))
                                            child['app'].placeOrder(child['app'].nextorderId, contract, order) #place order based on client 0 order
                                            child['app'].reqIds(child['app'].nextorderId)
                                            order.action = OA
                                            order.orderType = OT
                                            order.totalQuantity = totalQ

                                    if (child['binary_indicator'].get(contract.symbol) == [1,0]):
                                        order.totalQuantity = (order.totalQuantity//child["risk_divide"]) + abs((master_details['positions'].get(contract.symbol))//child["risk_divide"]) + abs(child['positions'].get(contract.symbol))
                                        child['app'].placeOrder(child['app'].nextorderId, contract, order) #place order based on client 0 order
                                        child['app'].reqIds(child['app'].nextorderId)
                                        order.totalQuantity = totalQ
                                        print('CBCBCBBCBCBCBCBBCBC', child['positions'].get(contract.symbol))

                                    if (child['binary_indicator'].get(contract.symbol) == [1,1]):
                                        if(TQ <= abs((master_details['positions'].get(contract.symbol)))):
                                            TQ = child['positions'].get(contract.symbol) * (TQ/master_details['positions'].get(contract.symbol))
                                            order.totalQuantity = round(TQ)
                                            child['app'].placeOrder(child['app'].nextorderId, contract, order) #place order based on client 0 order
                                            child['app'].reqIds(child['app'].nextorderId)
                                            order.totalQuantity = totalQ
                                        if(order.totalQuantity > abs(master_details['positions'].get(contract.symbol))):
                                            order.totalQuantity = ((order.totalQuantity - abs(master_details['positions'].get(contract.symbol)))//child["risk_divide"]) + abs(child['positions'].get(contract.symbol))
                                            child['app'].placeOrder(child['app'].nextorderId, contract, order) #place order based on client 0 order
                                            child['app'].reqIds(child['app'].nextorderId)
                                            order.totalQuantity = totalQ



                                if(order.action == 'SELL'):

                                    if(child['binary_indicator'].get(contract.symbol) == [0,0]):
                                        if(order.totalQuantity <= master_details['positions'].get(contract.symbol)):
                                            TQ = child['positions'].get(contract.symbol) * (TQ/master_details['positions'].get(contract.symbol))
                                            order.totalQuantity = round(TQ)
                                            print("testting",TQ)
                                            child['app'].placeOrder(child['app'].nextorderId, contract, order) #place order based on client 0 order
                                            child['app'].reqIds(child['app'].nextorderId)
                                            order.totalQuantity = totalQ
                                        if(order.totalQuantity > master_details['positions'].get(contract.symbol)):
                                            order.totalQuantity = ((order.totalQuantity - master_details['positions'].get(contract.symbol))//child["risk_divide"]) + child['positions'].get(contract.symbol)
                                            child['app'].placeOrder(child['app'].nextorderId, contract, order) #place order based on client 0 order
                                            child['app'].reqIds(child['app'].nextorderId)
                                            order.totalQuantity = totalQ

                                    if(child['binary_indicator'].get(contract.symbol) == [0,1]):
                                        order.totalQuantity = (order.totalQuantity//child["risk_divide"]) + abs((master_details['positions'].get(contract.symbol))//child["risk_divide"]) + abs(child['positions'].get(contract.symbol))
                                        child['app'].placeOrder(child['app'].nextorderId, contract, order) #place order based on client 0 order
                                        child['app'].reqIds(child['app'].nextorderId)
                                        order.totalQuantity = totalQ

                                    if(child['binary_indicator'].get(contract.symbol) == [1,0]):
                                        if(order.totalQuantity <= abs(master_details['positions'].get(contract.symbol))):
                                            OA = order.action
                                            OT = order.orderType
                                            order.action = 'BUY'
                                            order.orderType = "MKT"
                                            order.totalQuantity = abs(child['positions'].get(contract.symbol))
                                            child['app'].placeOrder(child['app'].nextorderId, contract, order) #place order based on client 0 order
                                            child['app'].reqIds(child['app'].nextorderId)
                                            order.action = OA
                                            order.orderType = OT
                                            order.totalQuantity = totalQ

                                    if(child['binary_indicator'].get(contract.symbol) == [1,1]):
                                        if((order.totalQuantity//child["risk_divide"]) + (abs(master_details['positions'].get(contract.symbol))//child["risk_divide"]) > abs(child['positions'].get(contract.symbol))):
                                            order.totalQuantity = (order.totalQuantity//child["risk_divide"]) + (abs(master_details['positions'].get(contract.symbol))//child["risk_divide"]) - abs(child['positions'].get(contract.symbol))
                                            child['app'].placeOrder(child['app'].nextorderId, contract, order) #place order based on client 0 order
                                            child['app'].reqIds(child['app'].nextorderId)
                                            order.totalQuantity = totalQ
                            
                            if(child['positions'].get(contract.symbol) is None):
                                if (order.action == 'SELL' and master_details['positions'].get(contract.symbol) > 0):    #check opposite directions 
                                    break

                                if (order.action == 'BUY' and master_details['positions'].get(contract.symbol) < 0):    #check opposite directions 
                                    break

                                else:
                                    order.totalQuantity //= child["risk_divide"] 
                                    child['app'].placeOrder(child['app'].nextorderId, contract, order) 
                                    child['app'].reqIds(child['app'].nextorderId) 
                                    order.totalQuantity = totalQ

                            if(child['positions'].get(contract.symbol) is not None):
                                if (order.action == 'SELL' and (child['positions'].get(contract.symbol) == 0 and child['positions'].get(contract.symbol) - order.totalQuantity//child["risk_divide"] < 0 and master_details['positions'].get(contract.symbol)) > 0):    #check opposite directions 
                                    break

                                if (order.action == 'BUY' and (child['positions'].get(contract.symbol) == 0 and  child['positions'].get(contract.symbol) + order.totalQuantity//child["risk_divide"] > 0 and master_details['positions'].get(contract.symbol)) < 0):
                                    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                                    break

                                else:
                                    order.totalQuantity //= child["risk_divide"] #need to account for % mod values to prevent misallignment of position sizing (etc B>23 = 4child, B>22 = 4child. S> 22+23 = 45 = 9child. EXTRA ONE... so position -1 instead of 0)
                                    #regardless of -ve or +ve will reallign. if zero we go zero.
                                    
                                    #Wrote draft code in words. Will explain


                                    child['app'].placeOrder(child['app'].nextorderId, contract, order) #place order based on client 0 order
                                    child['app'].reqIds(child['app'].nextorderId) #reqID increments the next validId *some error.. the api calls this 3 times per trade i do. fking retard. might be because of the threading also. need to do some self check on -id
                                    order.totalQuantity = totalQ
                print(order_str)
        
            

    def execDetails(self, reqId, contract, execution):
        print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)

# def buySwitch(x, totalQty, risk, CPOS, MPOS):
#     return {
#         '[0,0]': 1,
#         '[0,1]': 2,
#         '[1,0]': 1,
#         '[1,1]': 2
#     }.get(x, 9)    # 9 is default if x not found (trying to use switch)
                
def have_order(child_list, orderId):
    if len(child_list) > 0:
        for order_pair in child_list:
            if orderId in order_pair:
                print(f'Order Number {orderId} Found!')
                return True
    return False
    
def child_connect(child_details):
    temp_app = IBapi(child_details['client_id'])
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
    'account_name' : None,
    'positions' : {}
}

master_app = IBapi(master_details['client_id'])
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
        'account_name' : None,
        'risk_divide' : 5,
        "positions": {},
        'binary_indicator' : {}
    },
    {
        'ip_address': '127.0.0.1',
        'port': 7501,
        'client_id': 2,
        'account_name' : None,
        'risk_divide' : 10,
        "positions": {},
        'binary_indicator' : {}
    }
]

for i, child_det in enumerate(child_details):
    child_details[i]['app'] = child_connect(child_det)
    child_details[i]['order_list'] = []

master_app.reqAutoOpenOrders(True) #this allows to know what orders are placed because orderid will show up -ve

for child in child_details:
    child['app'].reqAccountUpdates(True, child['app'].clientId)

master_app.reqAccountUpdates(True, master_app.clientId)# request postions will call updatePortfolio()

time.sleep(3)

for child in child_details: #gets the difference in dict to find positions not the same
    A = list(child['positions'].keys())
    B = list(master_details['positions'].keys())
    commonKeys = set(A) - (set(A) - set(B))
    for key in commonKeys:
        if((child['positions'][key]) * child['risk_divide'] != (master_details['positions'][key])):
            print(key ,":" ,(child['positions'][key]) , " should be " , (master_details['positions'][key]), "risk mul:", child['risk_divide'])
            
            if((child['positions'][key]) > 0 and master_details['positions'][key] > 0 ): #give binary to child
                child['binary_indicator'][key] = [0,0]
                
            if((child['positions'][key]) > 0 and master_details['positions'][key] < 0 ):
                child['binary_indicator'][key] = [0,1]
            if((child['positions'][key]) < 0 and master_details['positions'][key] > 0 ):
                child['binary_indicator'][key] = [1,0]
            if((child['positions'][key]) < 0 and master_details['positions'][key] < 0 ):
                child['binary_indicator'][key] = [1,1]          

for child in child_details:
    print(json.dumps(child['binary_indicator']))
    print(json.dumps(child['positions']))

print(json.dumps(master_details['positions']))