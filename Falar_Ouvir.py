import speech_recognition as sr
import pyttsx3

# Inicializa sintetizador de voz
#engine = pyttsx3.init()

def falar(texto):
    engine = pyttsx3.init()
    print("Assistente:", texto)
    engine.say(texto)
    engine.runAndWait()

def ouvir():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Estou ouvindo...")
        audio = r.listen(source)
    try:
        texto = r.recognize_google(audio, language="pt-BR")
        print("Você disse:", texto)
        return texto.lower()
    except sr.UnknownValueError:
        falar("Desculpe, não entendi.")
        return None
    except sr.RequestError:
        falar("Erro no serviço de reconhecimento de voz.")
        return None

def responder(pergunta):
    # Regras simples (simulando chatbot)
    if "olá tudo bem" in pergunta or "oi tudo bem?" in pergunta: # Eu
        return "Olá, tudo e contigo?" # PC
    elif "tudo bem sim" in pergunta:
        return "legal"
    elif "qual o seu nome" in pergunta:
        return "Eu sou seu assistente de voz em Python, me chamo Eva e você?"
    elif "me chamo Juliano" in pergunta:
        return "Prazer Juliano."
    elif "tchau" in pergunta or "até logo" in pergunta:
        return "Até mais! Foi bom falar com você."
    else:
        return "Desculpe, não sei responder isso ainda."

def main():
    falar("Olá! Pode falar comigo.")
    while True:
        pergunta = ouvir()
        if not pergunta:
            continue
        resposta = responder(pergunta)
        falar(resposta)
        #print('O valor é: ', resposta)
        if "tchau" in pergunta or "até logo" in pergunta:
            break

if __name__ == "__main__":
    main()
