from gtts import gTTS
from playsound import playsound
import speech_recognition as sr
import os
import time

# Mock eCommerce and additional data (Indian style)
catalog = {
    "coffee": 70,    # ₹70
    "sandwich": 120, # ₹120
    "water": 25      # ₹25
}
weather_data = {"current": "Sunny, 32°C"}
music_file = r"C:\Users\tinku\OneDrive\Desktop\GitHub_Files\CarVoiceAssistant\song1.mp3"
orders = [
    {"item": "coffee", "price": 70, "status": "Delivered"},
    {"item": "sandwich", "price": 120, "status": "Pending"}
]

# Supported languages
languages = {
    "english": "en",
    "telugu": "te"
}

# Simplified Telugu translations with basic words
telugu_translations = {
    "Welcome to the In-Car Voice Assistant!": "కారు సహాయకుడికి స్వాగతం!",
    "Please say your command.": "మీ ఆదేశం చెప్పండి.",
    "Stopping the assistant.": "సహాయకుడు ఆపుతున్నాం.",
    "Good Bye!!": "పోతే కలుద్దాం!!",
    "Petrol level is at 75%. Nearest petrol pump is 3 kilometers away.": "పెట్రోల్ 75% ఉం�dి. సమీప పంపు 3 కిలోమీటర్ల దూరంలో.",
    "Playing the song.": "పాట ప్రారంభం అవుతోంది.",
    "Current weather: Sunny, 32°C.": "ప్రస్తుత వాతావరణం: సూర్యుడు, 32 డిగ్రీ.",
    "Your order for {item} is placed.": "మీ {item} ఆర్డర్ పెట్టబడింది.",
    "Invalid order. Please check the catalog.": "తప్పు ఆర్డర్. కేటలాగ్ చూడండి.",
    "Available items: {items}": "అందుబాటులో ఉన్నవి: {items}",
    "Please say or type the item to order.": "ఆర్డర్ చేయాలి అని చెప్పండి లేదా రాయండి.",
    "Sorry, I didn't understand that command. Say or type 'help' for options.": "క్షమించండి, అర్థం కాలేదు. 'సహాయం' చెప్పండి లేదా రాయండి.",
    "Available commands: {commands}": "ఉన్న ఆదేశాలు: {commands}",
    "No speech detected. Retry {retries} of {max_retries}.": "మాటలు కనిపించలేదు. {retries}/{max_retries} ప్రయత్నం.",
    "Could not understand audio. Retry {retries} of {max_retries}.": "శబ్దం అర్థం కాలేదు. {retries}/{max_retries} ప్రయత్నం.",
    "Max retries reached. Please type your command.": "గరిష్ట ప్రయత్నాలు. రాయండి ఆదేశం.",
    "Speech recognition error. Please type your command.": "మాట గుర్తింపు తప్పు. రాయండి ఆదేశం.",
    "Microphone error. Please type your command.": "మైక్ తప్పు. రాయండి ఆదేశం."
}

# Cache for pre-generated audio files
audio_cache = {}

def speak(text, lang="en"):
    """Convert text to speech and play it with caching and proper timing."""
    try:
        if lang == "te" and text in telugu_translations:
            translated_text = telugu_translations[text].format(**{k: v for k, v in locals().items() if k in telugu_translations[text]})
        else:
            translated_text = text
        cache_key = f"{translated_text}_{lang}"
        filename = "temp_response.mp3"
        if cache_key not in audio_cache:
            if os.path.exists(filename):
                os.remove(filename)
            tts = gTTS(text=translated_text, lang=lang, slow=False)
            tts.save(filename)
            audio_cache[cache_key] = filename
        playsound(audio_cache[cache_key])
        time.sleep(2)  # Increased delay to ensure audio completes
    except Exception as e:
        print(f"[{lang}] Error in text-to-speech: {e}")

def get_input(lang="en", max_retries=2):
    """Get input via voice or text with optimized latency and debugging."""
    recognizer = sr.Recognizer()
    retries = 0
    while retries <= max_retries:
        try:
            with sr.Microphone(device_index=0) as source:
                print(f"[{lang}] కమాండ్ కోసం వినిపించబడుతోంది..." if lang == "te" else f"[{lang}] Listening for your command...")
                speak("Please say your command.", lang)
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                command = recognizer.recognize_google(audio, language=lang if lang == "en" else "te-IN")
                print(f"[{lang}] గుర్తించబడింది: {command}" if lang == "te" else f"[{lang}] Recognized: {command}")
                return command.lower().strip()
        except sr.UnknownValueError:
            retries += 1
            print(f"[{lang}] శబ్దం అర్థం కాలేదు. {retries}/{max_retries} ప్రయత్నం." if lang == "te" else f"[{lang}] Could not understand audio. Retry {retries}/{max_retries}.")
            speak(f"Could not understand audio. Retry {retries} of {max_retries}.", lang)
            if retries == max_retries:
                return input(f"[{lang}] Max retries reached. Type your command (or 'exit' to quit): ").lower().strip()
        except (sr.RequestError, sr.WaitTimeoutError, Exception) as e:
            retries += 1
            print(f"[{lang}] ప్రసంగ లోపం: {e}. {retries}/{max_retries} ప్రయత్నం." if lang == "te" else f"[{lang}] Speech error: {e}. Retry {retries}/{max_retries}.")
            speak("Speech error. Please type your command.", lang)
            if retries == max_retries:
                return input(f"[{lang}] Max retries reached. Type your command (or 'exit' to quit): ").lower().strip()
    print(f"[{lang}] Input failed after max retries.")
    return None

def play_music(lang="en"):
    """Play a single predefined song with Telugu optimization."""
    try:
        print(f"[{lang}] ప్లే చేస్తోంది: {music_file.split('/')[-1]}..." if lang == "te" else f"[{lang}] Playing {music_file.split('/')[-1]}...")
        speak("Playing the song.", lang)
        playsound(music_file)
        return True
    except Exception as e:
        print(f"[{lang}] సంగీతం ప్లే చేయడంలో లోపం: {e}" if lang == "te" else f"[{lang}] Error playing music: {e}")
        speak("Error playing music. Try again.", lang)
        return False

def process_command(command, lang="en", last_command=None):
    """Process user commands with simplified Telugu support, avoiding repeats."""
    if not command or command.strip() == "":
        return False
    
    # Skip if the same command was just processed
    if last_command == command:
        print(f"[{lang}] Command {command} already processed, skipping...")
        return False
    
    if command in ["exit", "Exit", "EXIT"]:  # Universal exit command
        print(f"[{lang}] సహాయకుడు ఆపుతున్నాం..." if lang == "te" else f"[{lang}] Stopping the assistant...")
        speak("Stopping the assistant.", lang)
        print(f"[{lang}] పోతే కలుద్దాం!!" if lang == "te" else f"[{lang}] Good Bye!!")
        speak("Good Bye!!", lang)
        return True
    
    if command in ["stop", "ఆపు"]:  # Stop command for temporary pause
        print(f"[{lang}] సహాయకుడు ఆపుతున్నాం..." if lang == "te" else f"[{lang}] Stopping the assistant...")
        speak("Stopping the assistant.", lang)
        print(f"[{lang}] తిరిగి చెప్పండి ప్రారంభం కోసం..." if lang == "te" else f"[{lang}] Say again to resume...")
        speak("Say again to resume.", lang)
        return False  # Does not exit, just pauses
    
    if "navigate" in command or "go to" in command or "నావిగేట్" in command:
        response = "మీ గమ్యస్థానానికి వెళ్తున్నాం. మార్గం పాటించండి." if lang == "te" else "Navigating to your destination. Please follow the route."
    elif "petrol" in command or "fuel" in command or "పెట్రోల్" in command:
        response = "పెట్రోల్ 75% ఉంది. సమీప పంపు 3 కిలోమీటర్ల దూరంలో." if lang == "te" else "Petrol level is at 75%. Nearest petrol pump is 3 kilometers away."
    elif "order" in command or "buy" in command or "ఆర్డర్" in command:
        item = command.replace("order", "").replace("buy", "").replace("ఆర్డర్", "").strip() or "custom item"
        orders.append({"item": item, "status": "ordered"})
        response = f"మీ {item} ఆర్డర్ పెట్టబడింది." if lang == "te" else f"Your order for {item} is placed."
    elif "catalog" in command or "menu" in command or "కేటలాగ్" in command:
        items_str = ", ".join(f"{item} (₹{price})" for item, price in catalog.items())
        response = f"అందుబాటులో ఉన్నవి: {items_str}" if lang == "te" else f"Available items: {items_str}"
    elif "weather" in command or "climate" in command or "వాతావరణం" in command:
        response = "ప్రస్తుత వాతావరణం: సూర్యుడు, 32 డిగ్రీ." if lang == "te" else f"Current weather: {weather_data['current']}."
    elif "play song" in command or "play songs" in command or "పాట ప్లే" in command:
        if play_music(lang):
            response = "పాటను ఆనందించండి!" if lang == "te" else "Enjoy your music!"
        else:
            response = "పాట ప్లే చేయలేదు. మళ్లీ ప్రయత్నించండి." if lang == "te" else "Music playback failed. Try again."
    elif "help" in command or "సహాయం" in command:
        commands = "'నావిగేట్', 'పెట్రోల్', 'ఆర్డర్', 'కేటలాగ్', 'వాతావరణం', 'పాట ప్లే', 'సహాయం', 'ఆపు' (పాజ్), 'exit' (ఇంగ్లీష్‌లో చెప్పండి నిష్క్రమణ కోసం)"
        response = f"ఉన్న ఆదేశాలు: {commands}" if lang == "te" else f"Available commands: {commands}"
    else:
        response = "క్షమించండి, అర్థం కాలేదు. 'సహాయం' చెప్పండి." if lang == "te" else "Sorry, I didn't understand that command. Say or type 'help' for options."
    
    print(f"[{lang}] సహాయకుడు: {response}" if lang == "te" else f"[{lang}] Assistant: {response}")
    speak(response, lang)
    return False

def main():
    """Main function to run the voice assistant with optimized performance."""
    recognizer = sr.Recognizer()
    last_command = None
    
    print("Please say or type 'english' or 'telugu' to select language.")
    speak("Please say or type 'english' or 'telugu' to select language.", "en")
    lang_choice = get_input("en")
    while lang_choice is None or lang_choice not in languages:
        print("Invalid input. Please say or type 'english' or 'telugu'.")
        speak("Invalid input. Please say or type 'english' or 'telugu'.", "en")
        lang_choice = get_input("en")
    lang_code = languages.get(lang_choice, "en")
    
    welcome_msg = "కారు సహాయకుడికి స్వాగతం!" if lang_code == "te" else "Welcome to the In-Car Voice Assistant!"
    print(f"[{lang_code}] {welcome_msg}")
    speak(welcome_msg, lang_code)
    example_msg = ("ఉన్న ఆదేశాలు: 'నావిగేట్', 'పెట్రోల్', 'ఆర్డర్', 'కేటలాగ్', 'వాతావరణం', 'పాట ప్లే', 'సహాయం'. 'ఆపు' (పాజ్) లేదా 'exit' (ఇంగ్లీష్‌లో నిష్క్రమణ) చెప్పండి." if lang_code == "te" else
                   "Available commands: 'navigate to store', 'petrol', 'order item name', 'catalog', 'weather', 'play song', 'help'. Say or type 'stop' (pause) or 'exit' to quit.")
    print(f"[{lang_code}] {example_msg}")
    speak(example_msg, lang_code)
    
    while True:
        print(f"[{lang_code}] Waiting for command...")
        command = get_input(lang_code)
        if command is None:
            print(f"[{lang_code}] No command received, retrying...")
            continue
        if process_command(command, lang_code, last_command):
            break
        last_command = command  # Update last command after processing

if __name__ == "__main__":
    main()