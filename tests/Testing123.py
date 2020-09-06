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
            # need to code cancelling orders here based on orderid (but need to first store pairs)
            print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)
            if (status == 'Cancelled'):
                if(orderId <0):
                    rows=len(x) #finding the max number of rows in the matrix
                    columns=len(x[0])
                    for i in range(rows):
                        for j in range(columns):
                            if x[i-1][1]==orderId:
                                print("heyYAAAA")
                                app1.cancelOrder(x[i-1][0])
                
	     

	
	def openOrder(self, orderId, contract, order, orderState):
            # Keagan Edit
            # When this is triggered can try to create order to other clients
            
            if(isinstance(app1.nextorderId, int)): # check if 2nd account connected
                print("insidefirst")
                if(orderId <0): #API triggers for client 0 so that orderid will be -ve
                    print('inside openorder',app1.nextorderId)
                                            
                    if arrayx(orderId):
                        x.append([app1.nextorderId,orderId])
                        print('append')                   
                        # if(arrayx(orderId)): #check array for -orderId
                        print(x)
                        order.totalQuantity /= 5
                        app1.placeOrder(app1.nextorderId, contract, order) #place order based on client 0 order
                        app1.reqIds(app1.nextorderId) #reqID increments the next validId *some error.. the api calls this 3 times per trade i do. fking retard. might be because of the threading also. need to do some self check on -id
            print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, order.totalQuantity, orderState.status)

	def execDetails(self, reqId, contract, execution):
		print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)


def run_loop():
    app.run()

def run_loop1():
    app1.run()
    

#Function to create FX Order contract
def FX_order(symbol):
	contract = Contract()
	contract.symbol = symbol[:3]
	contract.secType = 'CASH'
	contract.exchange = 'IDEALPRO'
	contract.currency = symbol[3:]
	return contract

x = []
x.append([10000,10000])

def arrayx(orderId): #failed at using array. FML...
    print("x value",x)
    print('orderid in array', orderId)
    
    rows=len(x) #finding the max number of rows in the matrix
    print(rows)
    columns=len(x[0])
    print(columns)
    print('VALUE',x[0][1])
    for i in range(rows):
        # for j in range(columns):
            if x[i-1][1]==orderId:
                print("Found it!")
                return False
                
            else:
                return True


app = IBapi()
app1 = IBapi()
app.connect('127.0.0.1', 7498, 0)
app1.connect('192.168.1.43', 7499, 1)

app.nextorderId = None
app1.nextorderId = None

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()
time.sleep(3)

api_thread1 = threading.Thread(target=run_loop1, daemon=True)
api_thread1.start()
time.sleep(3)


#Check if the API is connected via orderid
while True:
	if isinstance(app.nextorderId, int):
		print('connected')
		break
	else:
		print('waiting forasd connection')
		time.sleep(1)

while True:
	if isinstance(app1.nextorderId, int):
		print('connected')
		break
	else:
		print('waiting for connection')
		time.sleep(1)

#Create order object
order = Order()
order.action = 'BUY'
order.totalQuantity = 100000
order.orderType = 'LMT'
order.lmtPrice = '1.10'


print('asd',app1.nextorderId)
print('a123',app.nextorderId)
#Place order
# app.placeOrder(app.nextorderId, FX_order('EURUSD'), order)
# app1.placeOrder(app.nextorderId, FX_order('EURUSD'), order)
#app.nextorderId += 1

app.reqAutoOpenOrders(True) 
#this allows to know what orders are placed because orderid will show up -ve



time.sleep(3)

#Cancel order 
# print('cancelling order')
# app.cancelOrder(app.nextorderId)

# time.sleep(3)
# app.disconnect()