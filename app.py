# from root import create_app


#api = create_app()

#if __name__ == "__main__":
 #   api.run(debug=True)
from flask import Flask, request, jsonify
from pymongo import MongoClient
import speech_recognition as sr
import datetime

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017/")
db = client['complaints_db']
complaints_collection = db['complaints']
recognizer = sr.Recognizer()
@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    if 'complaint_text' in request.form:
        complaint_text = request.form['complaint_text']
        complaint_type = request.form.get('complaint_type', 'General')
        save_complaint(complaint_text, complaint_type)
        return jsonify({'message': 'Text complaint submitted successfully'}), 200
    elif 'voice' in request.files:
        voice_file = request.files['voice']
        complaint_text = process_voice(voice_file)
        complaint_type = request.form.get('complaint_type', 'General')
        save_complaint(complaint_text, complaint_type)
        return jsonify({'message': 'Voice complaint submitted successfully', 'complaint': complaint_text}), 200
    else:
        return jsonify({'error': 'No valid complaint data provided'}), 400

def save_complaint(complaint_text, complaint_type):
    complaint = {
        "complaint_text": complaint_text,
        "complaint_type": complaint_type,
        "timestamp": datetime.datetime.utcnow(),
        "status": "Pending"
    }
    complaints_collection.insert_one(complaint)

def process_voice(voice_file):
    with sr.AudioFile(voice_file) as source:
        audio = recognizer.record(source)
        try:
            complaint_text = recognizer.recognize_google(audio)
            return complaint_text
        except sr.UnknownValueError:
            return "Could not understand the voice input"
        except sr.RequestError:
            return "Error in processing the voice input"

@app.route('/get_complaints', methods=['GET'])
def get_complaints():
    complaints = list(complaints_collection.find({}, {'_id': False}))
    return jsonify(complaints), 200

if __name__ == '__main__':
    app.run(debug=True)
