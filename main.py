from gtts import gTTS
from playsound import playsound
from translate import Translator
import speech_recognition as sr
import os
import time
from flask import Flask, jsonify

app = Flask(__name__)

# Mock data
catalog = {"coffee": 70, "sandwich": 120, "water": 25}
weather_data = {"current": "Sunny, 32°C"}
music_files = [
    "C:/Users/tinku/OneDrive/Desktop/GitHub_Files/CarVoiceAssistant/music/song1.mp3",
    "C:/Users/tinku/OneDrive/Desktop/GitHub_Files/CarVoiceAssistant/music/song2.mp3",
    "C:/Users/tinku/OneDrive/Desktop/GitHub_Files/CarVoiceAssistant/music/song3.mp3"
]
orders = []

# Telugu to English command mapping with improved synonyms
telugu_commands = {
    "పెట్రోల్": "petrol", "ఇంధనం": "petrol", "ఫ్యూయల్": "petrol",
    "పాటలు ప్లే చేయండి": "play songs", "సంగీతం ప్లే చేయండి": "play songs", "పాటలు": "play songs",
    "వాతావరణం": "weather",
    "ఆర్డర్": "order", "ఆర్డర్ చేయండి": "order",
    "కేటలాగ్": "catalog", "జాబితా": "catalog",
    "సహాయం": "help",
    "నిలిపివేయండి": "exit", "నిష్క్రమించండి": "exit", "ఆపండి": "exit"
}

# Supported languages
languages = {"english": "en", "telugu": "te"}

# Function to simulate text-to-speech
def speak(text, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)
        filename = "response.mp3"
        tts.save(filename)
        playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"Error in text-to-speech: {e}")

# Function to translate text
def translate_text(text, src_lang="en", dest_lang="en"):
    try:
        translator = Translator(from_lang=src_lang, to_lang=dest_lang)
        return translator.translate(text).replace("Sunny", "సన్ని").replace("°C", "డిగ్రీ సెల్సియస్")  # Improved Telugu
    except Exception as e:
        print(f"Translation error: {e}")
        return text

# Function to get voice or text input
def get_input(lang="en", max_retries=3):
    recognizer = sr.Recognizer()
    retries = 0
    use_voice = True
    while True:
        if use_voice and retries <= max_retries:
            try:
                with sr.Microphone(device_index=1) as source:
                    print("Listening for your command...")
                    speak("దయచేసి మీ ఆజ్ఞను చెప్పండి." if lang == "te" else "Please say your command.", lang)
                    recognizer.adjust_for_ambient_noise(source, duration=2)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=12)  # Increased for Telugu
                    command = recognizer.recognize_google(audio, language=lang if lang == "en" else "te-IN")
                    print(f"You said: {command}")
                    return command.lower().strip()
            except sr.UnknownValueError:
                retries += 1
                print(f"Could not understand audio. Retry {retries}/{max_retries}.")
                speak(f"ఆడియో అర్థం కాలేదు. పునరుదానం {retries}/{max_retries}." if lang == "te" else
                      f"Could not understand audio. Retry {retries}/{max_retries}.", lang)
                if retries == max_retries:
                    use_voice = False
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}. Switching to text input.")
                speak("ప్రసంగ గుర్తింపు దోషం. టైప్ చేయండి." if lang == "te" else "Speech recognition error. Please type.", lang)
                use_voice = False
            except sr.WaitTimeoutError:
                retries += 1
                print(f"No speech detected. Retry {retries}/{max_retries}.")
                speak(f"ప్రసంగం గుర్తించబడలేదు. పునరుదానం {retries}/{max_retries}." if lang == "te" else
                      f"No speech detected. Retry {retries}/{max_retries}.", lang)
                if retries == max_retries:
                    use_voice = False
            except Exception as e:
                print(f"Microphone error: {e}. Switching to text input.")
                speak("మైక్రోఫోన్ దోషం. టైప్ చేయండి." if lang == "te" else "Microphone error. Please type.", lang)
                use_voice = False
        if not use_voice:
            prompt = ("ఆజ్ఞను టైప్ చేయండి (లేదా 'వాయిస్' రీట్రై కోసం లేదా 'ఎక్సిట్' కి నిష్క్రమించండి): " 
                      if lang == "te" else "Enter your command (or 'voice' to retry or 'exit' to quit): ")
            command = input(prompt).lower().strip()
            if command == "voice":
                retries = 0
                use_voice = True
                continue
            elif command == "exit":
                return None
            return command

# Function to play music
def play_music(selection, lang="en"):
    try:
        if selection in ["1", "2", "3"]:
            index = int(selection) - 1
            if 0 <= index < len(music_files):
                print(f"Playing {music_files[index].split('/')[-1]}...")
                speak(f"సాంగ్ నంబర్ {selection} ప్లే అవుతోంది." if lang == "te" else f"Playing song number {selection}.", lang)
                playsound(music_files[index])
                return True
        print("Invalid selection. Defaulting to song 1.")
        speak("తప్పు ఎంపిక. మూడు ప్రయత్నాల తర్వాత పాట 1 డిఫాల్ట్‌గా ప్లే అవుతుంది." if lang == "te" else
              "Invalid selection. Defaulting to song 1 after three attempts.", lang)
        playsound(music_files[0])
        return True
    except Exception as e:
        print(f"Error playing music: {e}")
        speak("సంగీతం ప్లే చేయడంలో దోషం. మళ్లీ ప్రయత్నించండి." if lang == "te" else "Error playing music. Try again.", lang)
        return False

# Function to process commands
def process_command(command, lang="en"):
    if not command:
        return False
    
    translated_command = telugu_commands.get(command.split()[0] if " " in command else command, command)
    
    if translated_command in ["exit", "stop"]:
        print("Stopping the assistant...")
        speak("సహాయకుడు ఆగిపోతున్నాడు..." if lang == "te" else "Stopping the assistant...", lang)
        print("Good Bye!!")
        speak("వీడ్కోలు!!" if lang == "te" else "Good Bye!!", lang)
        return True
    
    if "petrol" in translated_command:
        response = "పెట్రోల్ స్థాయి 75% ఉంది. సమీప పెట్రోల్ పంప్ 3 కిలోమీటర్ల దూరంలో ఉంది." if lang == "te" else "Petrol level is at 75%. Nearest petrol pump is 3 kilometers away."
    elif "play songs" in translated_command:
        for attempt in range(3):
            speak("దయచేసి 1, 2, లేదా 3 ని ఎంచుకోండి." if lang == "te" else "Please say or type 1, 2, or 3 to select a song.", lang)
            selection = get_input(lang)
            if selection in ["1", "2", "3"]:
                if play_music(selection, lang):
                    return False
            if attempt < 2:
                speak("తప్పు ఎంపిక. మరో ప్రయత్నం." if lang == "te" else "Invalid selection. Try again.", lang)
        play_music("1", lang)  # Default to song 1 after 3 attempts
        return False
    elif "weather" in translated_command:
        weather_translated = translate_text(weather_data["current"], "en", lang)
        response = f"ప్రస్తుత వాతావరణం: {weather_translated}." if lang == "te" else f"Current weather: {weather_translated}."
    elif "order" in translated_command:
        response = "ఎలాంటి అంశాలు: " + ", ".join(f"{item} (₹{price})" for item, price in catalog.items()) if lang == "te" else "Available items: " + ", ".join(f"{item} (₹{price})" for item, price in catalog.items())
        print(f"Assistant: {response}")
        speak(response, lang)
        speak("దయచేసి ఆర్డర్ చేయాలనున్న అంశాన్ని చెప్పండి." if lang == "te" else "Please say or type the item to order.", lang)
        item = get_input(lang)
        if item and item in catalog:
            orders.append({"item": item, "price": catalog[item], "status": "Placed"})
            response = f"మీ {item} ఆర్డర్ ప్లేస్ చేయబడింది." if lang == "te" else f"Your order for {item} is placed."
        else:
            response = "అవకతవక ఆర్డర్. దయచేసి కేటలాగ్ ని తిరిగి చూడండి." if lang == "te" else "Invalid order. Please check the catalog."
    elif "catalog" in translated_command:
        response = "ఎలాంటి అంశాలు: " + ", ".join(f"{item} (₹{price})" for item, price in catalog.items()) if lang == "te" else "Available items: " + ", ".join(f"{item} (₹{price})" for item, price in catalog.items())
    elif "help" in translated_command:
        response = ("ఎలాంటి ఆజ్ఞలు: 'పెట్రోల్', 'పాటలు ప్లే చేయండి', 'వాతావరణం', 'ఆర్డర్', 'కేటలాగ్', 'సహాయం', 'నిలిపివేయండి'." if lang == "te" else
                   "Available commands: 'petrol', 'play songs', 'weather', 'order', 'catalog', 'help', 'exit'.")
    else:
        response = "క్షమించండి, నాకు ఆ ఆజ్ఞ అర్థం కాలేదు. 'సహాయం' చెప్పండి." if lang == "te" else "Sorry, I didn't understand. Say 'help'."
    
    print(f"Assistant: {response}")
    speak(response, lang)
    return False

# API endpoints (minimal for orders)
@app.route('/api/orders', methods=['GET'])
def get_orders():
    return jsonify(orders)

# Main loop for the assistant
def main():
    recognizer = sr.Recognizer()
    lang_code = None
    
    while lang_code is None:
        print("Please say or type 'english' or 'telugu' to select language.")
        speak("Please say or type 'english' or 'telugu' to select language.", "en")
        lang_choice = get_input("en")
        if lang_choice is None or lang_choice not in languages:
            lang_choice = input("Invalid input. Type language (english/telugu): ").lower()
        if lang_choice in languages:
            lang_code = languages[lang_choice]
    
    welcome_msg = "స్వాగతం ఇన్-కార్ వాయిస్ అసిస్టెంట్‌కు!" if lang_code == "te" else "Welcome to the In-Car Voice Assistant!"
    print(welcome_msg)
    speak(welcome_msg, lang_code)
    help_msg = ("ఎలాంటి ఆజ్ఞలు: 'పెట్రోల్', 'పాటలు ప్లే చేయండి', 'వాతావరణం', 'ఆర్డర్', 'కేటలాగ్', 'సహాయం', 'నిలిపివేయండి'." if lang_code == "te" else
                "Available commands: 'petrol', 'play songs', 'weather', 'order', 'catalog', 'help', 'exit'.")
    print(help_msg)
    speak(help_msg, lang_code)
    
    while True:
        command = get_input(lang_code)
        if command is None:
            continue
        if process_command(command, lang_code):
            break
        time.sleep(1)

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False), daemon=True).start()
    main()