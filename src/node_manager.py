from flask import Flask,request
import asyncio
import json
import httplib2
import threading
import chain_manager as cm



app = Flask(__name__)
node_list = []
@app.route('/announce',methods=['POST'])
def announce():
    global node_list    
    node_list.append(json.loads(request.data.decode('utf-8')))
    t= threading.Thread(target=update_ui)
    t.start()    
    return json.dumps(cm.actual_chain)

@app.route('/blockFound',methods=['POST'])
def blockFound():       
    return cm.validate_respond(json.loads(request.data.decode('utf-8')))

    

def update_ui():
    http  =  httplib2.Http()
    http.request('http://192.168.2.105:1880/found','POST',json.dumps(node_list))



if __name__ == '__main__':
    app.run(host='0.0.0.0',port='5004')