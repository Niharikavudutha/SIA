import pyttsx3
import speech_recognition as sr
 
engine = pyttsx3.init()
 
def speak(text):
    print("Bot:", text)
    engine.say(text)
    engine.runAndWait()
 
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎧 Listening... (say something)")
        r.adjust_for_ambient_noise(source, duration=1)  # Reduce background noise
       
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
        except Exception as e:
            print("❌ Mic error:", e)
            speak("Mic issue. Try again.")
            return ""
 
    try:
        text = r.recognize_google(audio)
        print("✅ Recognized:", text)
        return text.lower()
    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError as e:
        print(f"❌ Could not request results: {e}")
        speak("Sorry, speech service is not available.")
        return ""