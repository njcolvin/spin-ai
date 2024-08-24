import os
from anthropic import Anthropic
import pyttsx3
import time

# get the users ride difficulty
level_terms = {
    "easy": "beginner",
    "medium": "intermediate",
    "hard": "advanced",
}
# API client
client = Anthropic(
    # This is the default and can be omitted
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)
# TTS engine
engine = pyttsx3.init()

def get_spin_class() -> str:
    spin_class = ""
    messages = []
    ready = False
    while not ready:
        if not messages:
            level = None
            while level not in ("easy", "medium", "hard"):
                level = input("Enter the difficulty of your ride. (easy, medium, hard): ")
            level = level_terms[level]

            # get the users ride duration
            length = None
            while length not in (10, 20, 30, 45, 60):
                length = int(input("Enter the duration of your ride in minutes. (10, 20, 30, 45, 60): "))

            # get the users ride category
            category = None
            while category not in ("speed", "power", "hills", "combo"):
                category = input("Enter the category of your ride. (speed, power, hills, combo): ")
            messages.append({
                "role": "user",
                "content": f"You are a personal trainer. Write a minute-by-minute {level} level {length} minute {category} cycling class with exact cadence and resistance ranges for every block. Each block also has a single sentence description, which can include but is not limited to a pattern of changing positions or surge and recovery. There are 3 positions: in the saddle, out of the saddle on back handlebars, and out of the saddle on front handlebars. Warm up and cool down should be between 1 and {length//10} minutes long. Cadence is in units of RPM, ranges should be between 5-10 units, the minimum cadence is 45 and maximum is 125. Resistance is a 32 level scale and ranges should be 5 units. Format each block as follows:\n\n<title>\nTime: <start_minute>-<end_minute>\nCadence: <cadence_low>-<cadence_high>\nResistance: <resistance_low>-<resistance_high>\nDescription: <description>\n\nDo not include any other information in your message besides the blocks of your class.",
            })
        
        message = client.messages.create(
            max_tokens=512,
            messages=messages,
            model="claude-3-5-sonnet-20240620",
        )
        spin_class = "\n".join([
            block.text for block in message.content if block.type == "text"
        ])
        messages.append({
            "role": "assistant",
            "content": spin_class,
        })

        print(spin_class)
        engine.say("Here is your ride. Let me know when you are ready to begin.")
        engine.runAndWait()
        user_ready = input("\nReady? (y/n/m(odify)/q(uit)): ")
        match user_ready:
            case "y":
                ready = True
            case "n":
                messages = []
            case "m":
                modification = input("Enter the ride modification. (easier, harder, faster, slower, heavier, lighter): ")
                messages.append({
                    "role": "user",
                    "content": f"Make it {modification}."
                })
            case "q":
                spin_class = ""
                ready = True
    return spin_class

def speak_at_time(engine, text, target_time):
    current_time = time.time()
    if current_time < target_time:
        time.sleep(target_time - current_time)
    engine.say(text)
    engine.runAndWait()

# beginning of script, get users class
spin_class = get_spin_class()
if not spin_class:
    quit()
# split the class up by double line breaks
spin_class_split = spin_class.split("\n\n")

engine.say("Let's go!")
engine.runAndWait()

# iterate each triplet of time/description, cadence, resistance and play audio at each time
num_blocks = len(spin_class_split)
for i, block in enumerate(spin_class_split, start=1):
    block_split = block.split("\n")
    
    block_start_time = time.time()
    start_dlg = f"Block {i} of {num_blocks} has started."
    speak_at_time(engine, start_dlg, block_start_time + 1)

    title = block_split[0]
    speak_at_time(engine, title, block_start_time + 3)
    
    time_split = block_split[1].split(": ")[1].split("-")
    start_time = int(time_split[0])
    end_time = int(time_split[1])
    duration = end_time - start_time
    time_dlg = f"{duration} minute{'s' if duration > 1 else ''}"
    speak_at_time(engine, time_dlg, block_start_time + 4)

    cadence_split = block_split[2].split(": ")[1].split("-")
    cadence_low = int(cadence_split[0])
    cadence_high = int(cadence_split[1])
    cadence_dlg = f"Cadence between {cadence_low} and {cadence_high}"
    speak_at_time(engine, cadence_dlg, block_start_time + 6)

    resistance_split = block_split[3].split(": ")[1].split("-")
    resistance_low = int(resistance_split[0])
    resistance_high = int(resistance_split[1])
    resistance_dlg = f"Resistance between {resistance_low} and {resistance_high}"
    speak_at_time(engine, resistance_dlg, block_start_time + 8)

    description = block_split[4].split(": ")[1]
    speak_at_time(engine, description, block_start_time + 10)

    # 5-4-3-2-1 countdown
    for i in range(5, 0, -1):
        speak_at_time(engine, str(i), block_start_time + 15 + (5 - i))

    speak_at_time(engine, "begin", block_start_time + 20)

    # announce each minute of the block, 30 seconds, 10 seconds, 5-4-3-2-1 countdown
    if duration > 1:
        for i in range(duration - 1, 1, -1):
            speak_at_time(engine, f"{i} minutes left", block_start_time + (duration - i) * 60)
        
        speak_at_time(engine, "1 minute left", block_start_time + (duration - 1) * 60)

    speak_at_time(engine, "30 seconds left", block_start_time + (duration - 1) * 60 + 30)
    speak_at_time(engine, "10", block_start_time + (duration - 1) * 60 + 30 + 20)
    for i in range(5, 0, -1):
        speak_at_time(engine, str(i), block_start_time + (duration - 1) * 60 + 30 + 20 + 5 + (5 - i))

engine.say("Ride is over. Good work.")
engine.runAndWait()
engine.stop()
