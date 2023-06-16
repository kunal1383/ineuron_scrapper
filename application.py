from flask import Flask, render_template, request,jsonify
from flask import Response
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from application_logger.app_logger import Logger

application = Flask(__name__)
app = application

@app.route('/',methods = ['GET'])
def homePage():
    return render_template("index.html")

@app.route('/courses' ,methods = ['GET' ,'POST'])
def courses():
    try:
        if request.method == "POST":
            selected_course = request.form.get('course')
            url =  'https://ineuron.ai/category/' + selected_course.upper() +'/'
    except Exception as e:
        return Response("Error Occured %s" % e)     
        
    # Do something with the selected course
    #return 'Selected Course: {}'.format(url)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
    
    