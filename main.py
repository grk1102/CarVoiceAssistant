from gtts import gTTS
from playsound import playsound
from translate import Translator
import speech_recognition as sr
import os
import time

# Mock eCommerce catalog
catalog = {
    "coffee": 5.99,
    "sandwich": 7.99,
    "water": 1.99
}

# Supported languages
languages = {
    "english": "en",
    "telugu": "te"
}

# Function to simulate text-to-speech
def speak(text, lang="en"):
    try:
        tts = gTTS(text=text, lang=lang)
        filename = "response.mp3"
        tts.save(filename)
        playsound(filename)
        os.remove(filename)  # Clean up audio file
    except Exception as e:
        print(f"Error in text-to-speech: {e}")

# Function to translate text
def translate_text(text, src_lang="en", dest_lang="en"):
    try:
        translator = Translator(from_lang=src_lang, to_lang=dest_lang)
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

# Function to get voice input
def get_voice_input(lang="en"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your command...")
        speak("Please say your command.", lang)
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            command = recognizer.recognize_google(audio, language=lang)
            print(f"You said: {command}")
            return command
        except sr.WaitTimeoutError:
            print("No speech detected. Please try again.")
            speak("No speech detected. Please try again.", lang)
            return None
        except sr.UnknownValueError:
            print("Could not understand audio. Please try again.")
            speak("Could not understand audio. Please try again.", lang)
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}. Falling back to text input.")
            speak("Speech recognition error. Please type your command.", lang)
            return input("Enter your command (or 'exit' to quit): ")

# Function to process commands
def process_command(command, lang="en"):
    if command is None:
        return
    command = command.lower().strip()
    
    # Navigation commands
    if "navigate" in command or "go to" in command:
        response = "Navigating to your destination. Please follow the route."
    elif "fuel" in command or "gas" in command:
        response = "Fuel level is at 75%. Nearest gas station is 2 miles away."
    # eCommerce commands
    elif "order" in command:
        for item in catalog:
            if item in command:
                response = f"Ordered {item} for ${catalog[item]}. Delivery to your car in 10 minutes."
                break
        else:
            response = "Item not found. Available items: " + ", ".join(catalog.keys())
    elif "catalog" in command or "menu" in command:
        response = "Available items: " + ", ".join(f"{item} (${price})" for item, price in catalog.items())
    else:
        response = "Sorry, I didn't understand that command. Try 'navigate', 'fuel', or 'order'."
    
    # Translate response to user's language
    translated_response = translate_text(response, src_lang="en", dest_lang=lang)
    print(f"Assistant: {translated_response}")
    speak(translated_response, lang)
    return translated_response

# Main loop for the assistant
def main():
    # Initialize speech recognizer
    recognizer = sr.Recognizer()
    
    # Ask for user’s language preference (voice input)
    print("Please say 'english' or 'telugu' to select language.")
    speak("Please say 'english' or 'telugu' to select language.", "en")
    lang_choice = get_voice_input("en")
    if lang_choice is None:
        lang_choice = input("Speech not detected. Type language (english/telugu): ").lower()
    lang_code = languages.get(lang_choice.lower(), "en")
    
    # Welcome message
    welcome_msg = "Welcome to the In-Car Voice Assistant!"
    print(welcome_msg)
    speak(welcome_msg, lang_code)
    example_msg = "Example commands: navigate to store, check fuel, order coffee, show catalog"
    print(example_msg)
    speak(example_msg, lang_code)
    
    while True:
        # Get voice input for commands
        command = get_voice_input(lang_code)
        if command and command.lower() == "exit":
            goodbye_msg = "Goodbye!"
            print(goodbye_msg)
            speak(goodbye_msg, lang_code)
            break
        
        # Translate user input to English for processing
        translated_command = translate_text(command, src_lang=lang_code, dest_lang="en")
        process_command(translated_command, lang_code)

if __name__ == "__main__":
    main()