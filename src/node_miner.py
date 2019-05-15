import hashlib
from flask import Flask,request
import httplib2
import json
import threading
import socket
import time
app=Flask(__name__)

hostname = socket.gethostname()
max_nonce = 30000000
difficulty_bits = 12
target = 2 ** (256-difficulty_bits)
found_nonce_elsewhere = False
transactions = []
chain = []
prev_hash = ""



def initialize():    
    global chain,prev_hash
    http = httplib2.Http()
    data = {
        "hostname":hostname,
        "ip":"192.168.2.101"
    }
    res, dat = http.request("http://localhost:5004/announce","POST", json.dumps(data))
    chain = json.loads(dat)['chain']
    prev_hash = chain[len(chain)-1]['hash']
    
    
def enter_loop():
    global transactions,prev_hash
    while True:
        transactions = get_txions() 
        if(transactions[0]["txion"] == "None"):
            break 
        find_nonce(transactions,prev_hash)


def find_nonce(transactions,hash):
    found_nonce = False
    for nonce in range(max_nonce):
        hash_result = hashlib.sha256(str.encode(str(transactions) + str(nonce)+ str(hash) )).hexdigest()
        if(found_nonce_elsewhere):
            print('***************Shit*************IIIII')
            break
        if int(hash_result, 16) < target:
            calc_hash = hash_result
            calc_nonce = nonce
            found_nonce = True
            break

    if found_nonce:
        print(calc_nonce)
        form_block(calc_nonce,calc_hash)
        # validate(calc_nonce,hostname)
        # send_to_peers(calc_nonce)
        # return calc_hash, calc_nonce


def form_block(nonce,hash):
    global prev_hash,chain
    block ={"title":f"block {chain[len(chain)-1]['index'] + 1} ",
    "description":"yolo",
    "index":chain[len(chain)-1]['index'] + 1,
    "icon":"http://192.168.2.105:5005/bkchn.png",
    "pbh":prev_hash,
    "pow":nonce,
    "hash":hash,
		"timestamp":time.time(),
		"hostname":hostname,
    "txions":transactions
      }
    chain.append(block)
    send_block(block)
    prev_hash = chain[len(chain)-1]['hash']


def send_block(block):
    http = httplib2.Http()
    res, data = http.request('http://localhost:5004/blockFound',"POST", json.dumps(block))
    print(data)
     

# def validate(nonce, host):    
#     hash_result = hashlib.sha256(str.encode(str(transactions) + str(nonce))).hexdigest()
#     if int(hash_result, 16) < target:
#         block = {
#             "transactions":transactions,
#             "host":host,
#             "hash":hash_result
#         }
#         chain.append(block)
#         print(chain)
#     else:
#         return False
    #  If all nodes return True, then add the block to the chain

def get_txions():
    http = httplib2.Http()
    res, data = http.request('http://localhost:5000/gettxions',"GET")
    return json.loads(data)

if __name__ == '__main__':
    initialize()
    enter_loop()
    
       
    