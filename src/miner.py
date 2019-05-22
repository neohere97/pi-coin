import hashlib
import httplib2
import json
import threading
import time
from flask import Flask,request

app=Flask(__name__)

hostname = ''

max_nonce = 30000000

difficulty_bits = 15

target = 2 ** (256-difficulty_bits)

update_hash = False

index = 0

transactions = []

prev_hash = ""

sync_flag = False

@app.route('/latestHash',methods=["POST"])
def latestHash():
    global prev_hash,update_hash
    latest_hash = json.loads(request.data.decode('utf-8'))
    prev_hash = latest_hash["hash"]
    update_hash = True
    print("Hash Updated")

    return "OK", 200

@app.route('/sync_flag',methods=["POST"])
def syncflag():
    global sync_flag
    data = json.loads(request.data.decode('utf-8'))
    
    if(data["sync_status"] == "Yes"):
        sync_flag = True
        print("Paused Mining until sync finishes")
    elif(data["sync_status"] == "No"):
        sync_flag = False
        print("Resumed Mining, Sync completed")
    return "OK", 200

def enter_loop():
    global transactions,prev_hash,index,sync_flag
    while True:
        if(not sync_flag):
            resources = get_job()         
            if(resources["stat"] == "None"):
                print("Going to sleep")
                time.sleep(20)
                enter_loop() 
            else:
                transactions = resources["txions"]
                prev_hash = resources["pbh"]
                index = resources["index"]
                find_nonce()
        else:
            pass

def get_job():
    global transactions,prev_hash,index
    http = httplib2.Http()
    res,data = http.request("http://localhost:5000/giveJob","GET")
    resources = json.loads(data.decode("utf-8"))
    return resources
    

def find_nonce():
    global update_hash,transactions,prev_hash,max_nonce
    found_nonce = False 
    print("New Job Started")   
    for nonce in range(max_nonce):
        now_time = time.time()        
        hash_result = hashlib.sha256(str.encode(str(transactions) + str(nonce)+ str(prev_hash) + str(now_time))).hexdigest()
        if(not sync_flag):
            break
        if(update_hash):
            print('***************SOMEONE ELSE FOUND******************')
            update_hash = False
            break
        if int(hash_result, 16) < target:
            calc_hash = hash_result
            calc_nonce = nonce
            found_nonce = True
            # print(transactions)
            # print(prev_hash)
            # print(now_time)
            # print(nonce)            
            break

    if found_nonce:       
        form_block(calc_nonce,calc_hash,now_time)        


def form_block(nonce,hash,ts):
    global prev_hash,index
    block ={"title":"block {} ".format(index + 1),
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
    send_block(block)
    
    

def send_block(block):    
    http = httplib2.Http()
    http.request('http://localhost:5002/blockFound_miner',"POST", json.dumps(block))
    

def initialize():
    get_id()
    enter_loop()  

def get_id():
    global hostname
    http = httplib2.Http()
    res,data = http.request("http://localhost:5000/getID","GET")

    hostname = data.decode('utf-8')
    print("got hostname {}".format(hostname))

if __name__ == '__main__':
    threading.Thread(target=initialize).start()
    app.run(host='0.0.0.0',port='5003')