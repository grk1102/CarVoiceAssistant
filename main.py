from gtts import gTTS
from playsound import playsound
from translate import Translator
import speech_recognition as sr
import os
import time
from flask import Flask, jsonify

app = Flask(__name__)

# Mock eCommerce and additional data (Indian style)
catalog = {
    "coffee": 70,    # ₹70 (approx. ₹50-100 range)
    "sandwich": 120, # ₹120 (approx. ₹80-150 range)
    "water": 25      # ₹25 (approx. ₹20-30 range)
}
weather_data = {"current": "Sunny, 32°C"}  # Typical Indian weather
music_playlist = ["Bollywood Hit", "Tamil Song", "Punjabi Track"]  # Indian music
orders = [
    {"item": "coffee", "price": 70, "status": "Delivered"},
    {"item": "sandwich", "price": 120, "status": "Pending"}
]

# Supported languages
languages = {
    "english": "en",
    "telugu": "te"
}

# Function to simulate text-to-speech
def speak(text, lang="en"):
    """Convert text to speech and play it, then clean up the audio file."""
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
    """Translate text from source to destination language."""
    try:
        translator = Translator(from_lang=src_lang, to_lang=dest_lang)
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

# Function to get voice or text input
def get_input(lang="en", max_retries=2, use_voice=True):
    """Get input via voice or text with retry logic."""
    recognizer = sr.Recognizer()
    retries = 0
    while retries <= max_retries:
        if use_voice:
            try:
                with sr.Microphone(device_index=1) as source:  # Use Realtek mic
                    print("Listening for your command...")
                    speak("Please say your command.", lang)
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=7)
                    command = recognizer.recognize_google(audio, language=lang if lang == "en" else "te-IN")
                    print(f"You said: {command}")
                    return command.lower().strip()
            except sr.UnknownValueError:
                retries += 1
                print(f"Could not understand audio. Retry {retries}/{max_retries}.")
                speak(f"Could not understand audio. Retry {retries} of {max_retries}.", lang)
                if retries == max_retries and lang == "te":
                    print("Telugu recognition failed. Switching to English.")
                    speak("Telugu recognition failed. Switching to English.", lang)
                    return get_input("en", max_retries, use_voice)
                elif retries == max_retries:
                    print("Max retries reached. Switching to text input.")
                    speak("Max retries reached. Please type your command or say exit.", lang)
                    use_voice = False
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}. Switching to text input.")
                speak("Speech recognition error. Please type your command.", lang)
                use_voice = False
            except sr.WaitTimeoutError:
                retries += 1
                print(f"No speech detected. Retry {retries}/{max_retries}.")
                speak(f"No speech detected. Retry {retries} of {max_retries}.", lang)
                if retries == max_retries:
                    print("Max retries reached. Switching to text input.")
                    speak("Max retries reached. Please type your command or say exit.", lang)
                    use_voice = False
            except Exception as e:
                print(f"Microphone error: {e}. Switching to text input.")
                speak("Microphone error. Please type your command.", lang)
                use_voice = False
        if not use_voice:
            return input("Enter your command (or 'exit' to quit): ").lower().strip()
    return None

# Function to process commands
def process_command(command, lang="en"):
    """Process user commands and return True to exit if 'stop' or 'exit'."""
    if not command:
        return False
    
    if command in ["stop", "exit"]:
        print("Stopping the assistant...")
        speak("Stopping the assistant.", lang)
        print("Good Bye!!")
        speak("Good Bye!!")
        return True
    
    # Navigation and Indian-style commands
    if "navigate" in command or "go to" in command:
        response = "Navigating to your destination. Please follow the route."
    elif "petrol" in command or "fuel" in command:
        response = "Petrol level is at 75%. Nearest petrol pump is 3 kilometers away."
    # eCommerce commands
    elif "order" in command:
        for item in catalog:
            if item in command:
                orders.append({"item": item, "price": catalog[item], "status": "Pending"})
                response = f"Ordered {item} for ₹{catalog[item]}. Delivery to your car in 10 minutes."
                break
        else:
            response = "Item not found. Available items: " + ", ".join(f"{item} (₹{price})" for item, price in catalog.items())
    elif "catalog" in command or "menu" in command:
        response = "Available items: " + ", ".join(f"{item} (₹{price})" for item, price in catalog.items())
    # New commands
    elif "weather" in command:
        response = f"Current weather: {weather_data['current']}."
    elif "play music" in command:
        response = f"Playing music from playlist: {', '.join(music_playlist)}."
    elif "help" in command:
        response = "Available commands: navigate, petrol, order, catalog, weather, play music, help, stop, exit."
    else:
        response = "Sorry, I didn't understand that command. Say or type 'help' for options."
    
    translated_response = translate_text(response, src_lang="en", dest_lang=lang)
    print(f"Assistant: {translated_response}")
    speak(translated_response, lang)
    return False

# API endpoints for dashboard
@app.route('/api/orders', methods=['GET'])
def get_orders():
    return jsonify(orders)

@app.route('/api/weather', methods=['GET'])
def get_weather():
    return jsonify(weather_data)

@app.route('/api/music', methods=['GET'])
def get_music():
    return jsonify({"playlist": music_playlist})

# Main loop for the assistant
def main():
    """Main function to run the voice assistant."""
    recognizer = sr.Recognizer()
    
    # Ask for user’s language preference
    print("Please say or type 'english' or 'telugu' to select language.")
    speak("Please say or type 'english' or 'telugu' to select language.", "en")
    lang_choice = get_input("en", use_voice=True)
    if lang_choice is None or lang_choice not in languages:
        lang_choice = input("Invalid input. Type language (english/telugu): ").lower()
    lang_code = languages.get(lang_choice, "en")
    
    # Welcome message
    welcome_msg = "Welcome to the In-Car Voice Assistant!"
    print(welcome_msg)
    speak(welcome_msg, lang_code)
    example_msg = "Available commands: navigate, petrol, order, catalog, weather, play music, help. Say or type stop or exit to quit."
    print(example_msg)
    speak(example_msg, lang_code)
    
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