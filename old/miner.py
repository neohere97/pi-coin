from flask import Flask,request
import httplib2
import threading
import json
import hashlib
import time
import socket

app=Flask(__name__)

difficulty_bits = 15

target = 2 ** (256-difficulty_bits)

hostname = socket.gethostname()

transactions = []

prev_hash = 0

someone_else_found = False

index = 0

max_nonce = 30000000


def enter_loop():
    global transactions,prev_hash,index
    while True:
        transactions, prev_hash, index = get_job() 
        if(transactions[0]["txion"] == "None"):
            print("Going to sleep")
            time.sleep(20)
            enter_loop()         
        find_nonce(transactions,prev_hash)


def find_nonce(transactions,hash):
    global someone_else_found
    found_nonce = False
    
    for nonce in range(max_nonce):
        now_time = time.time()
        hash_result = hashlib.sha256(str.encode(str(transactions) + str(nonce)+ str(hash) + str(now_time))).hexdigest()
        if(someone_else_found):
            print('***************SOMEONE ELSE FOUND******************')            
            someone_else_found = False
            break
        if int(hash_result, 16) < target:
            calc_hash = hash_result
            calc_nonce = nonce
            found_nonce = True
            break

    if found_nonce:
        print(calc_nonce)
        form_block(calc_nonce,calc_hash,now_time)        


def get_new_pbh():
    global prev_hash
    http = httplib2.Http()
    res, data = http.request('http://localhost:5000/latestHash',"GET")
    prev_hash = json.loads(data.decode("utf-8"))

    

def get_job():
    http = httplib2.Http()
    res, data = http.request('http://localhost:5000/job',"GET")
    job = data.decode("utf-8")
    return job['txions'],job['pbh'],job["index"]


def form_block(nonce,hash,ts):
    global prev_hash,index
    block ={"title":f"block {index + 1} ",
    "description":"yolo",
    "index":index + 1,
    "icon":"http://192.168.2.105:5005/bkchn.png",
    "pbh":prev_hash,
    "pow":nonce,
    "hash":hash,
		"timestamp":ts,
		"hostname":hostname,
    "txions":transactions
      }
    t = threading.Thread(target=send_block, args=(block))   
    t.start()
    


def send_block(block):
    global someone_else_found
    http = httplib2.Http()
    res, data = http.request('http://192.168.2.105:5003/blockFound',"POST", json.dumps(block))
    if(data.decode('utf-8') == "Fail"):
        someone_else_found = True
        print(data)

@app.route('/newHash', methods=["POST"])
def newHash():
    global prev_hash,someone_else_found
    prev_hash = json.loads(request.data.decode('utf-8'))
    someone_else_found = True

    return "OK",200 

if __name__ == '__main__':
    t = threading.Thread(target=enter_loop)
    t.start()
    app.run(host='0.0.0.0',port='5001')
    