import json
import difflib
import datetime
import webbrowser
import os
from FUNCTION.SPEAK.speak import JarvisSpeaker

speaker = JarvisSpeaker()

# --- Dynamically get the path to commands.json ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # points to JARVIS/
COMMANDS_PATH = os.path.join(BASE_DIR, "DATA", "COMMANDS", "commands.json")

with open(COMMANDS_PATH, "r") as f:
    COMMANDS = json.load(f)

def find_best_match(user_input: str):
    user_input = user_input.lower()
    for key, data in COMMANDS.items():
        for phrase in data["keywords"]:
            if phrase in user_input:
                return key, data
    # Fallback: fuzzy match if not exact
    all_phrases = [p for d in COMMANDS.values() for p in d["keywords"]]
    best = difflib.get_close_matches(user_input, all_phrases, n=1, cutoff=0.6)
    if best:
        for key, data in COMMANDS.items():
            if best[0] in data["keywords"]:
                return key, data
    return None, None


def execute_command(command_key, data):
    if not command_key:
        speaker.speak("Sorry, I didn't understand that command.")
        return

    response = data["response"]

    if command_key == "open_browser":
        webbrowser.open("https://www.google.com")
    elif command_key == "play_music":
        pass
    elif command_key == "time":
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        response = f"{response} {current_time}"

    speaker.speak(response)
