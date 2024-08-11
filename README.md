# AI Generated Spin Class 🚴

Generate a cycling class with Claude 3.5 Sonnet!

## Installation

Python 3 required, 3.11+ recommended.

    git clone https://github.com/njcolvin/spin-ai.git
    pip install anthropic==0.33.0 py3-tts==3.5

You will need an Anthropic API key saved as an environment variable on your device.

You can also copy and paste it in from the Anthropic website. Look for this code in `app.py`:

    api_key=os.environ.get("ANTHROPIC_API_KEY")

Replace `os.environ.get("ANTHROPIC_API_KEY")` with your key in quotes:

    api_key="YOUR_KEY_HERE"

## Usage

    python app.py
