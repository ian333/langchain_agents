# config.py
language = "english"

def set_language(new_language):
    global language
    language = new_language

def get_language():
    return language
