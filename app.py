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
                "content": f"You are a personal trainer. Write a minute-by-minute {level} level {length} minute {category} cycling class with exact cadence and resistance ranges for every block. Warm-up and cool down should be between 1 and {length//10} minutes long. Speed is in units of RPM, ranges should be between 5-10 units, the minimum cadence is 45 and maximum is 125. Power is a 32 level scale and ranges should be 5 units. Format each block as follows:\n\n<block_title>\nTime: <start_minute>-<end_minute>\nSpeed: <speed_low>-<speed_high>\nPower: <power_low>-<power_high>\n\nDo not include any other information in your message besides the blocks of your class.",
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
        engine.say("Here is your class. Let me know when you are ready to begin.")
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

spin_class = get_spin_class()
if not spin_class:
    quit()
# split the class up by double line breaks
spin_class_split = spin_class.split("\n\n")

engine.say("Let's go!")
engine.runAndWait()

# iterate each triplet of time/description, cadence, resistance and play audio at each time
for block in spin_class_split:
    block_split = block.split("\n")
    
    title = block_split[0]
    engine.say(title)
    engine.runAndWait()
    # add a delay between saying each part of the workout block
    time.sleep(1)

    time_split = block_split[1].split(": ")[1].split("-")
    start_time = int(time_split[0])
    end_time = int(time_split[1])
    time_dlg = f"{end_time - start_time} minutes"
    engine.say(time_dlg)
    engine.runAndWait()
    time.sleep(1)


    cadence_split = block_split[2].split(": ")[1].split("-")
    cadence_low = int(cadence_split[0])
    cadence_high = int(cadence_split[1])
    cadence_dlg = f"Cadence between {cadence_low} and {cadence_high}"
    engine.say(cadence_dlg)
    engine.runAndWait()
    time.sleep(1)

    resistance_split = block_split[3].split(": ")[1].split("-")
    resistance_low = int(resistance_split[0])
    resistance_high = int(resistance_split[1])
    cadence_dlg = f"Resistance between {resistance_low} and {resistance_high}"
    engine.say(cadence_dlg)
    engine.runAndWait()

    time.sleep(1)

    # 5-4-3-2-1 countdown
    for i in range(5, 0, -1):
        engine.say(str(i))
        engine.runAndWait()
        time.sleep(1)

    engine.say("begin")
    engine.runAndWait()

    block_duration = end_time - start_time
    # announce each minute of the block, 30 seconds, 10 seconds, 5-4-3-2-1 countdown
    if block_duration > 1:
        for i in range(block_duration - 1, 1, -1):
            time.sleep(60)
            engine.say(f"{i} minutes left")
            engine.runAndWait()
        
        time.sleep(60)
        engine.say("1 minute left")
        engine.runAndWait()

    time.sleep(30)
    engine.say("30 seconds left")
    engine.runAndWait()

    time.sleep(20)
    engine.say("10")
    engine.runAndWait()

    time.sleep(5)
    for i in range(5, 0, -1):
        engine.say(str(i))
        engine.runAndWait()
        time.sleep(1)

engine.say("Class is over. Good work.")
engine.runAndWait()
engine.stop()
