#imports all libraries needed
from collections import OrderedDict
from flask import Flask, render_template,request
import cv2
import numpy as np
import json
import os
import fitbit
import gather_keys_oauth2 as Oauth2
import pandas as pd 
import datetime
import tkinter as tk
from tkinter import ttk
from google.cloud import vision

import io

### IoT dependencies
# from flask import Flask, render_template,request, redirect, url_for
from pyduino import *
import time



#
"""
from flask_sqlalchemy import SQLAlchemy
"""
#

app = Flask(__name__)

#
"""
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
    
class User(db.Model):
    name=db.Column(db.String(20),primary_key=True)
    prefferedFragrance=db.Column(db.String(10))
db.create_all()
user=User(name='Sophieeee',prefferedFragrance='lavender')
db.session.add(user)
db.session.commit()
""" 
#

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/', methods=['GET','POST'])
def my_link():
    calm=""
    FinalEmotion=""
    count=0
    heartRateNeutralStart=80
    heartRateNeutralEnd=100
    heartRateDummyValue=110
    
    #EMOTIONS and their corresponding FRAGRANCES
    angryFragrance="rose"
    happyFragrance="lavender"
    sadFragrance="woods"
    surprisedFragrance="citrus"
    calmFragrance="ocean"
    
    #DEFAULT USER PREFERENCES
    Sophie="lavender"
    Claire="ocean"
    Josephine="ocean"
    Benoit="rose"
    Faustine="woods"
    Harvey="citrus"
    Emile="rose"
    

    values_dict={'angry': 'angry','happy': 'happy','surprised': 'surprised','sad': 'sad'}
        
    question= request.form['questionnaire']
    userName= request.form['userName']
    print("userName = ", userName)
    print("question =",question)
   # ********************GOOGLE VISION*************************************
    
    #open('pri.txt', 'w').close()
   
    #Emotions
    emo = ['Angry', 'Surprised','Sad', 'Happy']
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                        'LIKELY', 'VERY_LIKELY')

    ############## Spanish version #################
    #emo = ['Bravo', 'Sorprendido','Triste', 'Feliz']
    #string = 'Sin emocion'

    #from google.oauth2 import service_account
    #credentials = service_account.Credentials.from_service_account_file('key.json')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']= "E:\Flask_Web_app\key.json"


    # Instantiates a client
    vision_client = vision.ImageAnnotatorClient()

    cv2.imshow('Video', np.empty((5,5),dtype=float))
    
    compressRate = 1
    while cv2.getWindowProperty('Video', 0) >= 0:
        video_capture = cv2.VideoCapture(0)
        ret, img = video_capture.read()
        img = cv2.resize(img, (0,0), fx=compressRate , fy=compressRate )

        ok, buf = cv2.imencode(".jpeg",img)
        image = vision.types.Image(content=buf.tostring())

        response = vision_client.face_detection(image=image)
        faces = response.face_annotations
        len(faces)
        for face in faces:
            x = face.bounding_poly.vertices[0].x
            y = face.bounding_poly.vertices[0].y
            x2 = face.bounding_poly.vertices[2].x
            y2 = face.bounding_poly.vertices[2].y
            cv2.rectangle(img, (x, y), (x2, y2), (0, 255, 0), 2)

            sentiment = [likelihood_name[face.anger_likelihood],
                        likelihood_name[face.surprise_likelihood],
                        likelihood_name[face.sorrow_likelihood],
                        likelihood_name[face.joy_likelihood]]
                        #likelihood_name[face.under_exposed_likelihood],
                        #likelihood_name[face.blurred_likelihood],
                        #likelihood_name[face.headwear_likelihood]]

            
            with open("pri.txt", "a") as text_file:
                for item, item2 in zip(emo, sentiment):
                    print(item, ":", item2, file=text_file)
    

            string = 'No sentiment'

            if not (all( item == 'VERY_UNLIKELY' for item in sentiment) ):
                if any( item == 'VERY_LIKELY' for item in sentiment):
                    state = sentiment.index('VERY_LIKELY')
                    # the order of enum type Likelihood is:
                    #'LIKELY', 'POSSIBLE', 'UNKNOWN', 'UNLIKELY', 'VERY_LIKELY', 'VERY_UNLIKELY'
                    # it makes sense to do argmin if VERY_LIKELY is not present, one would espect that VERY_LIKELY
                    # would be the first in the order, but that's not the case, so this special case must be added
                else:
                    state = np.argmin(sentiment)

                string = emo[state]

            cv2.putText(img,string, (x,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

        cv2.imshow("Video", img)
        cv2.waitKey(1)
        video_capture.release()

    # When everything is done, release the capture
    cv2.destroyAllWindows()

    
    
    dictList = []
    with open('pri.txt', 'r') as f:
            for line in f:
                elements = line.rstrip().split(":")
                dictList.append(dict(zip(elements[::2], elements[1::2])))
                        
                        
                        
    for i in range(0,len(dictList)):
        for key in dictList[i]:
            varx=dictList[i][key].lstrip()
            dictList[i][key]=varx

   
    dictnew = {}

    for k,v in [(key, d[key]) for d in dictList for key in d]:
        if k not in dictnew:
            dictnew[k] = [v]
        else:
            dictnew[k].append(v)   
            
   
    def counter(dict1):
        dictnew= {'Angry ':[{'VERY_LIKELY': 0},{'LIKELY': 0},{'POSSIBLE': 0}, {'UNLIKELY': 0},{'VERY_UNLIKELY':0}], 
                'Surprised ': [{'VERY_LIKELY': 0},{'LIKELY': 0}, {'POSSIBLE': 0}, {'UNLIKELY': 0},{'VERY_UNLIKELY':0}],
                'Sad ': [{'VERY_LIKELY': 0},{'LIKELY': 0}, {'POSSIBLE': 0}, {'UNLIKELY': 0},{'VERY_UNLIKELY':0}],
                'Happy ':[{'VERY_LIKELY': 0},{'LIKELY': 0}, {'POSSIBLE': 0}, {'UNLIKELY': 0},{'VERY_UNLIKELY':0}]}

        for key in dict1.keys():
            for k in dictnew.keys():
                if key==k:
                    for j in range(0,len(dict1[key])):
                        for m in range(0,5):
                            for n in dictnew[key][m].keys():
                                if n==dict1[key][j]:
                                    dictnew[key][m][n]=dictnew[key][m][n]+1
        
        for k in dictnew.keys():
            dictnew[k][4]['VERY_UNLIKELY']=0
                    
        return dictnew


    dictnew=counter(dictnew) 
   
    def score(dict1):
        order=['VERY_LIKELY','LIKELY', 'POSSIBLE', 'UNLIKELY']
        scoredict={'Angry ':0, 
                'Surprised ': 0,
                'Sad ': 0,
                'Happy ':0} 
        for key in dict1.keys():
            for j in range(0,len(dict1[key])):
                for n in dictnew[key][j].keys():
                    if dictnew[key][j][n]>0:
                        scoredict[key]=scoredict[key]+ dictnew[key][j][n]
        
        listvar=[]
        var1=0
        final= {'Angry ':'VERY_UNLIKELY', 
                'Surprised ': 'VERY_UNLIKELY',
                'Sad ': 'VERY_UNLIKELY',
                'Happy ':'VERY_UNLIKELY'}
        for k in scoredict.keys():
            if scoredict[k]>var1:
                listvar.clear()
                listvar.append({k:scoredict[k]})
                var1=scoredict[k]
            elif scoredict[k]==var1:
                listvar.append({k:scoredict[k]})
        semi=[]
        varneed=0
        
        for p in range(0,len(listvar)):
            for kites in listvar[p].keys():
                for key in dict1.keys():
                    if key==kites:
                        for l in range(0,4):
                            for locks in dict1[key][l].keys():
                                if dict1[key][l][locks]>0:
                                    if len(semi)>0:
                                        for z in semi[0].keys():
                                            if order.index(semi[0][z])> order.index(locks):                                       
                                                semi.pop()
                                                
                                                semi.append({key: locks})
                                            
                                    else: semi.append({key:locks})
                                        
        for keys in semi[0].keys():
            final[keys]=semi[0][keys]
        for key, value in final.items():
            if(key=="Angry "):
                angry=value
                values_dict["angry"]=angry
            if(key=="Surprised "):
                surprised=value
                values_dict["surprised"]=surprised
            if(key=="Sad "):
                sad=value
                values_dict["sad"]=sad
            if(key=="Happy "):
                happy=value
                values_dict["happy"]=happy
        return(scoredict, listvar, final)

        
        
        
    scoredict, listvar, final=score(dictnew)

    #open('pri.txt', 'w').close()
    

    #*******************FITBIT*******************************
    
    #Server authentication
    server=Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
    server.browser_authorize()
    ACCESS_TOKEN=str(server.fitbit.client.session.token['access_token'])
    REFRESH_TOKEN=str(server.fitbit.client.session.token['refresh_token'])
    auth2_client=fitbit.Fitbit(CLIENT_ID,CLIENT_SECRET,oauth2=True,access_token=ACCESS_TOKEN,refresh_token=REFRESH_TOKEN)
    yesterday = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d"))
    yesterday2 = str((datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
    today = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    fit_statsHR = auth2_client.intraday_time_series('activities/heart', base_date=today, detail_level='1sec')
    time_list = []
    val_list = []
    for i in fit_statsHR['activities-heart-intraday']['dataset']:
        val_list.append(i['value'])
        time_list.append(i['time'])
    heartdf = pd.DataFrame({'Heart Rate':val_list,'Time':time_list})
    if len(val_list) == 0:
        heartRate=heartRateDummyValue  #if FitBit is not synced today then the list is empty.Value 90 assigned to heartRate if fitbit is not synced today.
    else:
        heartRate=val_list[-1] #Latest value from fitbit app is assigned to heartRate
    print(f'HeartRate={heartRate}') #Prints heartRate in Terminal
    
    
    #***********************ALGORITHM************************************
    #assign heartRate
    if(heartRate<heartRateNeutralStart):
        heartBeat="below"
    elif (heartRate>heartRateNeutralEnd):
        heartBeat="above"
    else:
        heartBeat="neutral"
    for emotion, value in values_dict.items(): 
        print(emotion," = ",value)
        if (value=="VERY_LIKELY"): #1st branch of algorithm-one emotion is VERY_LIKELY
            FinalEmotion=emotion
    if(FinalEmotion == ""): #3rd branch of algorithm-all emotions are VERY_UNLIKELY
            for emotion, value in values_dict.items():
                if (value=="VERY_UNLIKELY"):
                    count+=1
            if(count==4):
                if(heartBeat =="above"):
                    if(question =="left"):
                        FinalEmotion="angry"
                    elif(question =="right"):
                        FinalEmotion="happy"
                    elif(question =="neutral"):
                        FinalEmotion="Print emotion from Emotion Table"
                    elif(question=="angry"):
                        FinalEmotion="angry"
                    elif(question=="happy"):
                        FinalEmotion="happy"
                    elif(question=="calm"):
                        FinalEmotion="calm"
                    elif(question=="sad"):
                        FinalEmotion="sad"
                elif(heartBeat =="below"):
                    if(question =="left"):
                        FinalEmotion="sad"
                    elif(question =="right"):
                        FinalEmotion="calm"
                    elif(question =="neutral"):
                        FinalEmotion="Print emotion from Emotion Table"
                    elif(question=="angry"):
                        FinalEmotion="angry"
                    elif(question=="happy"):
                        FinalEmotion="happy"
                    elif(question=="calm"):
                        FinalEmotion="calm"
                    elif(question=="sad"):
                        FinalEmotion="sad"
                elif(heartBeat =="neutral"):
                    if(question =="left"):
                        FinalEmotion="Print emotion from Emotion Table"
                    elif(question =="right"):
                        FinalEmotion="Print emotion from Emotion Table"
                    elif(question =="neutral"):
                        FinalEmotion="Print emotion from Emotion Table"
                    elif(question=="angry"):
                        FinalEmotion="angry"
                    elif(question=="happy"):
                        FinalEmotion="happy"
                    elif(question=="calm"):
                        FinalEmotion="calm"
                    elif(question=="sad"):
                        FinalEmotion="sad"
    if(FinalEmotion == ""): #2nd branch of algorithm -neutral
        if(heartBeat =="above"):
                    if(question =="left"):
                        FinalEmotion="angry"
                    elif(question =="right"):
                        FinalEmotion="happy"
                    elif(question =="neutral"):
                        FinalEmotion="Print emotion from Emotion Table"
                    elif(question=="angry"):
                        FinalEmotion="angry"
                    elif(question=="happy"):
                        FinalEmotion="happy"
                    elif(question=="calm"):
                        FinalEmotion="calm"
                    elif(question=="sad"):
                        FinalEmotion="sad"
        elif(heartBeat =="below"):
                    if(question =="left"):
                        FinalEmotion="sad"
                    elif(question =="right"):
                        FinalEmotion="calm"
                    elif(question =="neutral"):
                        FinalEmotion="Print emotion from Emotion Table"
                    elif(question=="angry"):
                        FinalEmotion="angry"
                    elif(question=="happy"):
                        FinalEmotion="happy"
                    elif(question=="calm"):
                        FinalEmotion="calm"
                    elif(question=="sad"):
                        FinalEmotion="sad"
        elif(heartBeat =="neutral"):
                    if(question =="left"):
                        FinalEmotion="Print emotion from Emotion Table"
                    elif(question =="right"):
                        FinalEmotion="Print emotion from Emotion Table"
                    elif(question =="neutral"):
                        FinalEmotion="Print emotion from Emotion Table"
                    elif(question=="angry"):
                        FinalEmotion="angry"
                    elif(question=="happy"):
                        FinalEmotion="happy"
                    elif(question=="calm"):
                        FinalEmotion="calm"
                    elif(question=="sad"):
                        FinalEmotion="sad"
    #prints final emotion in the terminal
    print(f'Final Emotion={FinalEmotion}')
    #Pop up window displays result
    popup = tk.Tk()
    popup.wm_title("Result")
    if(FinalEmotion=="angry"):
        label = ttk.Label(popup, text="Hi "+userName+"!\n You are angry !\n Enjoy the "+angryFragrance+" fragrance!")
    elif(FinalEmotion=="happy"):
        label = ttk.Label(popup, text="Hi "+userName+"!\n You are happy!\n Enjoy the "+happyFragrance+" fragrance!")
    elif(FinalEmotion=="calm"):
        label = ttk.Label(popup, text="Hi "+userName+"!\n You are calm!\n Enjoy the "+calmFragrance+" fragrance!")
    elif(FinalEmotion=="sad"):
        label = ttk.Label(popup, text="Hi "+userName+"!\n You are sad!\n Enjoy the "+sadFragrance+" fragrance!")
    elif(FinalEmotion=="Print emotion from Emotion Table"):
        if(userName=="Sophie"):
            label=ttk.Label(popup, text="Hi "+userName+"! \n You are neutral.\n Enjoy your prefered fragrance "+Sophie+" !")
        elif(userName=="Claire"):
            label=ttk.Label(popup, text="Hi "+userName+"! \n You are neutral.\n Enjoy your prefered fragrance "+Claire+" !")
        elif(userName=="Josephine"):
            label=ttk.Label(popup, text="Hi "+userName+"! \n You are neutral.\n Enjoy your prefered fragrance "+Josephine+" !")
        elif(userName=="Benoit"):
            label=ttk.Label(popup, text="Hi "+userName+"! \n You are neutral.\n Enjoy your prefered fragrance "+Benoit+" !")
        elif(userName=="Faustine"):
            label=ttk.Label(popup, text="Hi "+userName+"! \n You are neutral.\n Enjoy your prefered fragrance "+Faustine+" !")
        elif(userName=="Harvey"):
            label=ttk.Label(popup, text="Hi "+userName+"! \n You are neutral.\n Enjoy your prefered fragrance "+Harvey+" !")
    elif(FinalEmotion=="surprised"):
        label=ttk.Label(popup, text="Hi \n You are surprised!\n Enjoy the "+surprisedFragrance+" fragrance!")
    else:
        label=ttk.Label(popup, text="test case")
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="ok", command = popup.destroy)
    B1.pack()
    popup.mainloop()
    #Retains and displays the web page
    
    #arduino code starts
    # initialize connection to Arduino
    # if your arduino was running on a serial port other than '/dev/ttyACM0/'
    # declare: a = Arduino(serial_port='/dev/ttyXXXX')
    a = Arduino() 
    time.sleep(3)

    # declare the pins we're using
    LED_PIN = 50
    ANALOG_PIN = 0
    emotion = 50
    # initialize the digital pin as output
    a.set_pin_mode(emotion,'O')
    print('Arduino initialized')

        # if we make a post request on the webpage aka press button then do stuff
        # if request.method == 'POST':
            # if we press the turn on button
            
            # print("emotion =", emotion)
    # if request.form['submit'] == 'start' :
    #     # emotion = FinalEmotion
    if FinalEmotion == "angry":
        emotion = 42  ##enter the pin assigned
    elif FinalEmotion == "happy":
        emotion = 50 ##enter the pin assigned
    elif FinalEmotion == "sad":
        emotion = 48 ##enter the pin assigned
    elif FinalEmotion == "calm":
        emotion = 46 ##enter the pin assigned
    elif FinalEmotion == "surprised":
        emotion = 44  ##enter the pin assigned
    else:
        emotion = 46  ##enter the pin assigned
        
    print('TURN ON')
    try:
        #turn off the LED on arduino
        for i in range(0,100):
            a.digital_write(i,0)
        # turn on LED on arduino
        print("emotion inside catch type =", type(emotion))
        print("emotion inside catch value =", emotion)
        # a.set_pin_mode(emotion,'O')
        a.digital_write(emotion,1)
    except :   
            print("already entered")

    
    return (''), 204

if __name__ == '__main__':
  app.run(debug=True)
    

    
