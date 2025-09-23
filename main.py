import random
import sys
import speech_recognition as sr
import pyttsx3
import wikipedia
import webbrowser
import datetime
import os
import pyjokes
import difflib
import urllib.parse

# Initialize the speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1)    # Volume level (0.0 to 1.0)

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def normalize_text(text):
    return text.lower().strip()
