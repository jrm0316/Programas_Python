from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ========== CONFIGURAÇÕES DO EMAIL ==========
EMAIL_ORIGEM = "xyz@gmail.com"
SENHA_APP = "**** **** **** ****"  # senha de app do Gmail (senha de app, não a normal)
EMAIL_DESTINO = "xyz@gmail.com"

# ========== SCRAPING DO INDEED ==========
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

url = "https://br.indeed.com/jobs?q=python&l=São+Paulo"
driver.get(url)
time.sleep(5)

vagas = []
cards = driver.find_elements(By.CSS_SELECTOR, ".job_seen_beacon")

for card in cards:
    try:
        titulo = card.find_element(By.CSS_SELECTOR, "h2 a").text
    except:
        titulo = "Não informado"

    try:
        empresa = card.find_element(By.CSS_SELECTOR, '[data-testid="company-name"]').text
    except:
        empresa = "Não informado"

    try:
        local = card.find_element(By.CSS_SELECTOR, '[data-testid="text-location"]').text
    except:
        local = "Não informado"

    try:
        link = card.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")
    except:
        link = "Sem link"

    vagas.append({
        "Título": titulo,
        "Empresa": empresa,
        "Local": local,
        "Link": link
    })

driver.quit()

arquivo_csv = "vagas_indeed.csv"
df = pd.DataFrame(vagas)
df.to_csv(arquivo_csv, index=False, encoding="utf-8-sig")

print("Extração concluída! Total de vagas:", len(vagas))

# ========== ENVIO DE EMAIL ==========
mensagem = MIMEMultipart()
mensagem["From"] = EMAIL_ORIGEM
mensagem["To"] = EMAIL_DESTINO
mensagem["Subject"] = "Relatório de vagas Indeed - Python São Paulo"

corpo = f"""
Olá!

Segue em anexo o relatório com {len(vagas)} vagas encontradas no Indeed para 'Python - São Paulo'.

Atenciosamente,
Seu Robô de Vagas
"""
mensagem.attach(MIMEText(corpo, "plain"))

# Anexo CSV
with open(arquivo_csv, "rb") as anexo:
    parte = MIMEBase("application", "octet-stream")
    parte.set_payload(anexo.read())
encoders.encode_base64(parte)
parte.add_header("Content-Disposition", f"attachment; filename={arquivo_csv}")
mensagem.attach(parte)

# Envia
try:
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ORIGEM, SENHA_APP)
        smtp.send_message(mensagem)
        print(f"E-mail enviado com sucesso para {EMAIL_DESTINO}!")
except Exception as e:
    print("Erro ao enviar e-mail:", e)
