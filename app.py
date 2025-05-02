from flask import Flask, render_template, request
from flask_cors import CORS
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from deep_translator import GoogleTranslator
import os
import requests

# Ensure the 'saved_conversations' directory exists
if not os.path.exists('saved_conversations'):
    os.makedirs('saved_conversations')

# Get the next available conversation file number
conversation_files = os.listdir('saved_conversations')
if conversation_files:
    filenumber = max([int(f) for f in conversation_files if f.isdigit()]) + 1
else:
    filenumber = 1

file_path = f'saved_conversations/{filenumber}.txt'
with open(file_path, "w+") as file:
    file.write('bot : Hi There! I am a medical chatbot. You can begin conversation by typing in a message and pressing enter.\n')

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# Initialize ChatterBot
english_bot = ChatBot(
    'Bot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        {'import_path': 'chatterbot.logic.BestMatch'}
    ],
    database_uri='sqlite:///database.sqlite3'
)

# Train the bot using ListTrainer
trainer = ListTrainer(english_bot)
trainer.train([
    "Hello",
    "Hi there!",
    "How are you?",
    "I'm good, how can I help you?",
    "What is your name?",
    "I am a medical chatbot.",
    "I have a fever.",
    "You may have a viral infection. Drink plenty of fluids and rest. If symptoms persist, consult a doctor.",
    "I have a headache.",
    "Headaches can be caused by stress, dehydration, or an underlying condition. Try drinking water and resting.",
    "I have stomach pain.",
    "You may have indigestion or gastritis. Try eating light food and staying hydrated.",
    "I have COVID-19 symptoms.",
    "COVID-19 symptoms include fever, cough, and difficulty breathing. Please isolate and consult a doctor."
])

def translate_text(text, src_lang, dest_lang):
    try:
        return GoogleTranslator(source=src_lang, target=dest_lang).translate(text)
    except Exception:
        return "Translation service is currently unavailable."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["GET"])
def get_bot_response():
    user_message = request.args.get("msg", "")
    language = request.args.get("lang", "en")  # Default to English

    if not user_message:
        return "Error: No message received."

    # Translate input to English before processing
    translated_input = translate_text(user_message, src_lang=language, dest_lang="en")
    bot_response = str(english_bot.get_response(translated_input))

    # Translate chatbot response back to the user's language
    translated_response = translate_text(bot_response, src_lang="en", dest_lang=language)

    return translated_response


def fetch_medical_advice(symptoms):
    api_url = "https://api.healthcare.gov/disease"  # Replace with a real API
    params = {"symptoms": symptoms, "format": "json"}
    
    try:
        response = requests.get(api_url, params=params)
        data = response.json()
        
        if "treatment" in data:
            return data["treatment"]
        else:
            return "No specific treatment found. Consult a healthcare professional."
    except Exception:
        return "Could not fetch medical advice at the moment."

if __name__ == "__main__":
    app.run(debug=True)
