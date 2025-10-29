from BRAIN.processor import execute_command, find_best_match
from FUNCTION.LISTEN import listen
from FUNCTION.SPEAK.speak import JarvisSpeaker
import time

def main():
    # Initialize Jarvis speaker once
    speaker = JarvisSpeaker()

    speaker.speak("Hello, Mr. Shivang. Jarvis is now online and ready for your command.")

    while True:
        try:
            # Listen for the user's voice
            query = listen()

            if not query:
                continue

            print(f"User said: {query}")

            # Exit condition
            if any(exit_word in query.lower() for exit_word in ["exit", "quit", "stop", "bye"]):
                speaker.speak("Goodbye, Mr. Shivang. Have a great day.")
                break

            # Process and execute the command
            command_key, command_data = find_best_match(query)
            execute_command(command_key, command_data)

        except KeyboardInterrupt:
            # Manual interruption (Ctrl+C)
            speaker.speak("Shutting down Jarvis. Goodbye, Mr. Shivang.")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            speaker.speak("Sorry, something went wrong.")
            time.sleep(1)

if __name__ == "__main__":
    main()
