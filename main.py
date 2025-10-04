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

COMMON_NAMES = ["elon musk", "barack obama", "taylor swift", "natu naatu", "naatu naatu"]
# Expand COMMON_NAMES with names/phrases you use often for better typo correction.

def speak(text):
    engine.say(text)
    engine.runAndWait()

def normalize(text):
    return text.strip().lower()

def fuzzy_correct(query, candidates=COMMON_NAMES, cutoff=0.7):
    # try to correct single or multi-word queries by checking best matches
    query = normalize(query)
    # check whole phrase first
    matches = difflib.get_close_matches(query, candidates, n=1, cutoff=cutoff)
    if matches:
        return matches[0]
    # try matching words inside
    words = query.split()
    for w in words:
        m = difflib.get_close_matches(w, [c for cand in candidates for c in cand.split()], n=1, cutoff=cutoff)
        if m:
            # return candidate containing best match
            for cand in candidates:
                if m[0] in cand.split():
                    return cand
    return query

# -----------------------
# Openers
# -----------------------
def open_youtube_search(query):
    q = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={q}"
    webbrowser.open(url)
    speak(f"Opening YouTube results for {query}")

def open_wikipedia(query):
    # try to form a likely Wikipedia URL by turning spaces into underscores.
    # fallback to Google search if wikipedia page might not exist.
    title = query.strip().replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title)}"
    webbrowser.open(url)
    speak(f"Opening Wikipedia page for {query}")

def open_google_search(query):
    q = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={q}"
    webbrowser.open(url)
    speak(f"Searching Google for {query}")

def open_generic_page(query):
    # Heuristic: if query contains "wiki" or "wikipedia" or looks like "about X", open wiki.
    if query.startswith("about "):
        open_wikipedia(query[len("about "):])
    else:
        open_google_search(query)

# -----------------------
# Command parsing
# -----------------------
def handle_command_text(command_text):
    cmd = normalize(command_text)
    if cmd == "none" or not cmd:
        return
    # common patterns:
    # open video <terms>
    # open youtube <terms>
    # open page <terms>
    # open about <terms>
    # about <terms>
    tokens = cmd.split()
    if tokens[0] == "open" and len(tokens) > 1:
        subtype = tokens[1]
        remainder = " ".join(tokens[2:]) if len(tokens) > 2 else ""
        if subtype in ("video", "youtube", "song", "music"):
            if not remainder:
                speak("Which video would you like me to open?")
                return
            remainder = fuzzy_correct(remainder)
            open_youtube_search(remainder)
            return
        elif subtype in ("page", "wiki", "website", "web"):
            if not remainder:
                speak("Which page should I open?")
                return
            remainder = remainder.replace("about ", "")  # handle accidental 'about' in remainder
            remainder = fuzzy_correct(remainder)
            # prefer wiki for known persons
            if any(name in remainder for name in ["elon", "musk", "wiki", "wikipedia"]):
                open_wikipedia(remainder)
            else:
                open_google_search(remainder)
            return
        else:
            # fallback: treat everything after 'open' as a query
            remainder = " ".join(tokens[1:])
            remainder = fuzzy_correct(remainder)
            open_generic_page(remainder)
            return

    # handle 'about <name>'
    if tokens[0] == "about" and len(tokens) > 1:
        remainder = " ".join(tokens[1:])
        remainder = fuzzy_correct(remainder)
        open_wikipedia(remainder)
        return

    # handle 'play <song>'
    if tokens[0] == "play" and len(tokens) > 1:
        remainder = " ".join(tokens[1:])
        remainder = fuzzy_correct(remainder)
        open_youtube_search(remainder)
        return

    # direct keywords: "naatu naatu" or "natu naatu" treat as video
    if "naatu naatu" in cmd or "natu naatu" in cmd:
        open_youtube_search("naatu naatu full song")
        return

    # if nothing recognized, do a google search
    remainder = cmd
    remainder = fuzzy_correct(remainder)
    open_google_search(remainder)

# -----------------------
# Voice / CLI entrypoints
# -----------------------
def take_command_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        r.pause_threshold = 1
        audio = r.listen(source, phrase_time_limit=8)
    try:
        print("🔍 Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        print(f"You said: {query}")
    except Exception as e:
        print("❌ Could not understand audio.")
        return "None"
    return query.lower()

def main():
    # CLI mode: allow running commands directly from terminal
    if len(sys.argv) > 1:
        # join all args as command
        cmd_text = " ".join(sys.argv[1:])
        print("Command-line mode:", cmd_text)
        handle_command_text(cmd_text)
        return

    # otherwise voice loop
    speak("Assistant started. Say a command or say 'exit' to stop.")
    while True:
        command = take_command_voice()
        if command in ("none", "None"):
            speak("I didn't catch that. Please repeat.")
            continue
        if any(word in command for word in ("exit", "quit", "stop", "bye")):
            speak("Goodbye.")
            break
        # auto-correct common typos (example: 'elion musk' -> 'elon musk')
        # do fuzzy correction inside handler
        handle_command_text(command)

if __name__ == "__main__":
    main()
