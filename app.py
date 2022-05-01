from flask import Flask, render_template, request, url_for, redirect, jsonify
import os
import numpy as np
import random
#import threading
from learning import model, bag_of_words, words, labels, data
from sounds import alter_ego_sounds
import json

app = Flask(__name__)


sprites_path="static/sprites"
alter_ego_sprites=[]
global second_tag

#speech_recognition
import speech_recognition as sr
#import pyttsx3
#import datetime
import wikipedia
#import webbrowser
#import time
#import subprocess
#from ecapture import ecapture as ec
#import wolframalpha
#import requests
import pywhatkit

from werkzeug.utils import secure_filename
import librosa
import soundfile as sf
import unidecode

#Names and responses for the image recognition    
with open ("image_recognition_names_en.json") as file:
    data_ir_names = json.load(file)

#print(data_ir_names["image_recognition_names"])

#Load the Alter Ego sprites
for img in os.listdir(sprites_path):
    img_path=sprites_path+"/"+img
    #print(img_path)
    alter_ego_sprites.append(img_path)
alter_ego_sprites.sort()
   
#Load the backgrounds
bg_path="static/background"
background_anim_paths=[]
for img in os.listdir(bg_path):
    img_path=bg_path+"/"+img
    background_anim_paths.append(img_path)

#Set standard user name
current_user_val = "Stranger"

def choose_response(json_file, change_name, second_tag_arg, add_msg):
    if second_tag_arg != "no_second_tag":
        try:
            print("Log: Setting second_tag = {}".format(second_tag_arg))
            global second_tag
            second_tag = second_tag_arg
        except:
            print("Log: Error Setting second_tag = {}".format(second_tag_arg))
    responses = json_file['responses']
    sprites = json_file['sprites']
    sounds = json_file['sounds']
    if add_msg != "no_add_msg":
        ae_response = random.choice(responses) + " " + add_msg
    else:
        ae_response = random.choice(responses)
    chosen_sprite = random.choice(sprites)
    chosen_sprite_path = alter_ego_sprites[chosen_sprite]
    chosen_sound = random.choice(sounds)
    chosen_sound_path = alter_ego_sounds[chosen_sound]
    print("Log: Sprite change to", chosen_sprite_path)
    print("Log: Sound to play", chosen_sound_path)
    return jsonify(message=ae_response, sprite=chosen_sprite_path, sound=chosen_sound_path, new_name=change_name)

def statement_clean_pl(statement, tag):
    rem_wiki = ["wikipedia", "czym", "jest", 
                "wytlumacz", "czy", "mozesz", "powiedziec",
                "o", "to", "co", "kim", "mi", 
                "jest", "do cholery"]
    rem_song = ["mozesz", "odtworz", "zagraj","czy","puscic"]
    query = statement.split()
    if (tag == "wikipedia"):
        resultwords  = [word for word in query if word.lower() not in rem_wiki]
    if (tag == "play_song"):
        resultwords  = [word for word in query if word.lower() not in rem_song]
    statement = ' '.join(resultwords)
    return statement

def decode(text):
    decoded_string = unidecode.unidecode(text)
    return decoded_string

def statement_clean_en(statement, tag):
    rem_wiki = ["wikipedia", "what's", "explain", 
                "can", "you", "tell", "me",
                "who", "what", "is", "a", "an", 
                "about"]
    rem_song = ["play", "can", "you"]
    query = statement.split()
    if (tag == "wikipedia"):
        resultwords  = [word for word in query if word.lower() not in rem_wiki]
    if (tag == "play_song"):
        resultwords  = [word for word in query if word.lower() not in rem_song]
    statement = ' '.join(resultwords)
    return statement


@app.route('/', methods=["POST", "GET"])
def index():
    return render_template("index.html")


@app.route('/alter_ego', methods=["POST", "GET"])
def alter_ego():
    return render_template("alter_ego.html", 
                               alter_ego_sprites = alter_ego_sprites,
                               current_user = current_user_val)

@app.route("/welcome", methods=["GET"])
def hello():
    tag = "welcome_message"
    for tg in data ["intents"]:
        if tg['tag'] == tag:
            return choose_response(tg, "second", "welcome_message_2", "no_add_msg")
    
@app.route("/get_response", methods=["POST"])
def get_response():
    statement = request.form["input_text_nm"]
        
    results = model.predict([bag_of_words(statement, words)])[0] #tablica prawdopodobienstw
    results_index = np.argmax(results) #wskazuje index najwiekszego prawdopodobienstwa
    tag = labels[results_index] #wskazuje odpowiedni tag
        
    print("Log: Tag = " + tag)
    if results[results_index] > 0.7:
        #losowanie odpowiedzi
        for tg in data ["intents"]:
            if tg['tag'] == tag:
                if tg['tag'] == "wikipedia":
                    statement = statement_clean_en(statement, "wikipedia")
                    results = wikipedia.summary(statement, sentences=3)
                    return choose_response(tg, "unchanged", "no_second_tag", results)
                if tg['tag'] == "play":
                    song = statement_clean_en(statement, "play_song")
                    pywhatkit.playonyt(song, True, True)
                    return choose_response(tg, "unchanged", "no_second_tag", song)
#                if tg['tag'] == "aio":
#                    return choose_response(tg, "second", "aio_2", "no_add_msg")
                if tg['tag'] == "recognition":
                    return choose_response(tg, "second", "recognition", "no_add_msg")
                else:
                    return choose_response(tg, "unchanged", "no_second_tag", "no_add_msg")
    else:
        for tg in data["intents"]:
            if tg['tag'] == "noanswer":
                return choose_response(tg, "unchanged", "no_second_tag", "no_add_msg")
            
@app.route("/second_response", methods=["GET"])
def second_response():
    if second_tag == "recognition":
        import image_recognition_camera
        ir_result = image_recognition_camera.recognition()
        print("Log: Thread finished, result =",ir_result)
        for names in data_ir_names ["recognition_names"]:
            if names['tag'] == ir_result:
                return choose_response(names, ir_result, "no_second_tag", "no_add_msg")
    if second_tag == "welcome_message_2":
        for tg in data["intents"]:
            if tg['tag'] == second_tag:
                return choose_response(tg, "unchanged", "no_second_tag", "no_add_msg")
#    if second_tag == "aio_2":
#        for tg in data["intents"]:
#            if tg['tag'] == second_tag:
#                return choose_response(tg, "unchanged", "no_second_tag", "no_add_msg")
        
@app.route("/process_audio", methods=["POST"])
def process_audio():
    if request.method == 'POST':
        print(request.files)
        if 'file' not in request.files:
            print("file not in request")
            return "voice file error"
        else:
            file = request.files['file']
            if file:
                print("if file:")
                file.save(secure_filename(file.filename))
                x,_ = librosa.load('./recording.wav', sr=16000)
                sf.write('tmp.wav', x, 16000)
                
                recognizer = sr.Recognizer()
                audioFile = sr.AudioFile('tmp.wav')
                
                with audioFile as source:
                    data = recognizer.record(source)
                try:
                    #EN
                    transcript = recognizer.recognize_google(data,language='en-US')
                    #PL
                    #transcript = recognizer.recognize_google(data,language='pl-PL')
                except:
                    transcript = "voice command failed"
                return decode(transcript)
            else:
                print("Something went wrong...")
                return "voice file error"
            
@app.route("/listening", methods=["GET"])
def listening():
    for tg in data["intents"]:
        if tg['tag'] == "voice_command":
            return choose_response(tg, "unchanged", "no_second_tag", "no_add_msg")