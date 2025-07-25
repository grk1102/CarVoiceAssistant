from gtts import gTTS
from playsound import playsound
from translate import Translator
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

# Function to process commands
def process_command(command, lang="en"):
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
    
    # Ask for user’s language preference
    lang_choice = input("Select language (english/telugu): ").lower()
    lang_code = languages.get(lang_choice, "en")

    print("Welcome to the In-Car Voice Assistant!")
    speak("Welcome to the In-Car Voice Assistant!",lang_code)  
    print("Example commands: 'navigate to store', 'check fuel', 'order coffee', 'show catalog'")
    speak("Example commands: 'navigate to store', 'check fuel', 'order coffee', 'show catalog'",lang_code)
    
    while True:
        # Get user input
        command = input("Enter your command (or 'exit' to quit): ")
        if command.lower() == "exit":
            print("Goodbye!")
            speak("Goodbye!", lang_code)
            break
        
        # Translate user input to English for processing
        translated_command = translate_text(command, src_lang=lang_code, dest_lang="en")
        process_command(translated_command, lang_code)

if __name__ == "__main__":
    main()