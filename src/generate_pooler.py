from flask import Flask,request  
import random
import threading
import json
import time
import httplib2

app=Flask(__name__)

first_names = ['Carletta', 'Rachelle', 'Renata', 'Ann', 'Karlyn', 'Nydia', 'Keva', 'Willis', 'Allan', 'Akiko', 'Suellen', 'Nickole', 'Ashanti', 'Alisha', 'Ami', 'Bea', 'Jeannine', 'Krystina', 'Carita', 'Lina', 'Rosario', 'Bobbye', 'Senaida', 'Georgann', 'Georgiann', 'Eula', 'Edward', 'Trevor', 'Yetta', 'Carri', 'Hoyt', 'Linh', 'Kristian', 'Carlie', 'Raina', 'Enoch', 'Lindsy', 'Jacqualine', 'Edison', 'Dalene', 'Eva', 'Latosha', 'Wei', 'Leanna', 'Elinore', 'Frederic', 'Pattie', 'Flavia', 'Lynetta', 'Kaylene']

last_names = ['Wm', 'Roscoe', 'Chauncey', 'Graig', 'Malcolm', 'Morgan', 'Dennis', 'Mary', 'Ezekiel', 'Harold', 'Giuseppe', 'Darnell', 'Brant', 'Alejandro', 'Mark', 'Lemuel', 'Herschel', 'Granville', 'Noble', 'Cesar', 'Dewayne', 'Mike', 'Efrain', 'Jeramy', 'Merle', 'Hassan', 'Roberto', 'Jules', 'Rashad', 'Basil', 'Hugh', 'Lane', 'Quentin', 'Hollis', 'Tomas', 'Ferdinand', 'Wendell', 'Roy', 'Stuart', 'Andre', 'Jame', 'Rhett', 'Kelly', 'Darwin', 'Diego', 'Milton', 'Lynn', 'Markus', 'Fermin', 'Rich']

alphabets = [' A ', ' B ' , ' C ', ' D ', ' E ' , ' F ', ' G ', ' H ', ' I ' , ' J ', ' K ', ' L ', ' M ', ' N ', ' O ', ' P ', ' Q ', ' R ', ' S ', ' T ', ' U ', ' V ', ' W ', ' X ', ' Y ', ' Z ']

state = False

peer_nodes = []

no_of_transactions_permin = 20

job_queue = []

txns = []

pool_monitoring = False

sync_timestamp = 0

@app.route('/setState',methods =["POST"])
def setState():
    global state
    state_s = json.loads(request.data.decode('utf-8'))['setState']
    if(state_s == "Start"):
        state = True
        t= threading.Thread(target=generate_trans)
        t.start() 
        print("Started")
    elif(state_s == "Stop"):
        state = False


    return "OK", 200
   
@app.route('/nodeAnnounce',methods =["POST"])
def nodeAnnounce():
    global peer_nodes
    node = json.loads(request.data.decode('utf-8'))
    peer_nodes.append(node)
    print(peer_nodes)
    threading.Thread(target=announce_node_to_network,args=(node,)).start()
    return "OK",200

@app.route('/numTrans',methods =["POST"])
def numTrans():
    global no_of_transactions_permin
    no_of_transactions_permin = json.loads(request.data.decode('utf-8'))['numTrans']
    print("no of transactions set to {}".format(no_of_transactions_permin))

    return "OK",200

@app.route('/monPool',methods =["POST"])
def monPool():
    global pool_monitoring
    data = json.loads(request.data.decode('utf-8'))['monPool']
    if(data == "Start"):
        pool_monitoring = True
        threading.Thread(target=monitor_distribute).start()
    else:
        pool_monitoring = False

    return "OK",200


def generate_trans():
    global state
    while True:
        if(not state):
            break
        transaction_string = "{} paid {} {} PI coins".format(random.choice(first_names) + random.choice(alphabets) + random.choice(last_names),random.choice(first_names) + random.choice(alphabets) + random.choice(last_names),random.randint(1,500))
        transaction = {
            "txion":transaction_string,
            "timeStamp":time.time(),
            "title":transaction_string,
            "description":time.time()
        }
        send_to_pooler(transaction)    
        # print(transaction)    
        time.sleep(60/no_of_transactions_permin)


def send_to_pooler(transaction):
    global txns,job_queue
    txns.append(transaction)
    if(len(txns) == 16):
        job_queue.append(txns)        
        txns = []
        print("Job Queue length {}".format(len(job_queue)))
        threading.Thread(target=monitor_distribute).start()
        
def announce_node_to_network(node):
    global peer_nodes
    http = httplib2.Http()
    for i in peer_nodes:
        http.request('http://{}:{}/peerFound'.format(i["ip"],i["port"]),'POST',json.dumps(node))

def monitor_distribute():
    global job_queue,peer_nodes 
    if(len(job_queue) >= 40):
        http = httplib2.Http()
        for i in peer_nodes:
            jobs = job_queue[0:5]
            del job_queue[0:5]
            http.request('http://{}:{}/jobs'.format(i["ip"],i["port"]),'POST',json.dumps(jobs))
    
@app.route('/sync',methods =["GET"])
def sync(): 
    global sync_timestamp 
    sync_timestamp = time.time()    
    threading.Thread(target=sync_timer).start()
    return "OK",200


def sync_timer():
    global peer_nodes,state,sync_timestamp
    print("Sync Enabled")
    http = httplib2.Http()
    while True:               
        if(time.time() - sync_timestamp >= 40):
            state = False                         
            for i in peer_nodes:
                http.request('http://{}:{}/syncTime'.format(i["ip"],i["port"]),'POST',json.dumps({"sync_status":"Yes"}))            
            sync_timestamp = time.time()
            # for i in peer_nodes:
            #     http.request('http://{}:{}/syncTime'.format(i["ip"],i["port"]),'POST',json.dumps({"sync_status":"No"}))
            

               

    

if __name__ == '__main__':           
    app.run(host='0.0.0.0',port='5000')
     
    