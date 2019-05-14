from quart import Quart,request,send_file
import asyncio

app = Quart(__name__)

@app.route('/getImage',methods=['GET'])
async def send_image_job():
    return send_file('./bkchn.png',mimetype='image/png')



if __name__ == '__main__':
    app.run(host='0.0.0.0',port='5000')