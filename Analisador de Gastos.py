import sqlite3
import csv
import os
import pandas as pd
import openai

# Nome do banco
BANCO = "gastos.db"

# Cria (ou conecta) ao banco
def criar_banco():
    conn = sqlite3.connect(BANCO)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS despesas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoria TEXT,
        valor REAL,
        mes TEXT,
        ano INTEGER
    )
    """)

    conn.commit()
    conn.close()


# Função para inserir despesa
def inserir_despesa(categoria, valor, mes, ano):
    conn = sqlite3.connect(BANCO)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO despesas (categoria, valor, mes, ano) VALUES (?, ?, ?, ?)",
        (categoria, valor, mes, ano)
    )
    conn.commit()
    conn.close()


# Função para ler dados do usuário manualmente
def inserir_dados_manualmente():
    print("\n=== Inserir Despesas Manualmente ===")
    while True:
        categoria = input("Categoria (ou ENTER para parar): ").strip()
        if categoria == "":
            break
        valor = float(input(f"Valor gasto com {categoria}: R$ "))
        mes = input("Mês: ")
        ano = int(input("Ano: "))
        inserir_despesa(categoria, valor, mes, ano)
        print(f"{categoria} adicionada com sucesso!\n")

def inserir_dados_csv(caminho_csv):
    import csv
    import os

    if not os.path.exists(caminho_csv):
        print("Arquivo não encontrado!")
        return

    # Abre o arquivo com UTF-8-SIG para remover BOM do Excel
    with open(caminho_csv, newline='', encoding='utf-8-sig') as f:
        # Detecta delimitador automaticamente
        primeira_linha = f.readline()
        f.seek(0)
        delimitador = ';' if ';' in primeira_linha else ','

        leitor = csv.DictReader(f, delimiter=delimitador)
        for linha in leitor:
            # Normaliza os nomes das colunas: remove espaços e minúsculas
            linha_normalizada = {k.strip().lower(): v.strip() for k, v in linha.items() if k}

            try:
                categoria = linha_normalizada['categoria']
                valor = float(linha_normalizada['valor'])
                mes = linha_normalizada['mes']
                ano = int(linha_normalizada['ano'])
                inserir_despesa(categoria, valor, mes, ano)
                print(f"Inserido: {categoria} - R${valor} ({mes}/{ano})")
            except KeyError as e:
                print(f"Coluna ausente: {e}. Verifique o cabeçalho do CSV.")
            except ValueError:
                print(f"Erro ao converter valor numérico em {linha_normalizada}")


def visualizar_despesas():
    conn = sqlite3.connect(BANCO)
    cursor = conn.cursor()

    print("\n=== Visualizar Despesas ===")
    filtro_mes = input("Filtrar por mês (ou ENTER para todos): ").strip()
    filtro_ano = input("Filtrar por ano (ou ENTER para todos): ").strip()

    # Monta a query dinamicamente conforme o filtro
    query = "SELECT categoria, valor, mes, ano FROM despesas"
    params = []
    if filtro_mes and filtro_ano:
        query += " WHERE mes = ? AND ano = ?"
        params = [filtro_mes, int(filtro_ano)]
    elif filtro_mes:
        query += " WHERE mes = ?"
        params = [filtro_mes]
    elif filtro_ano:
        query += " WHERE ano = ?"
        params = [int(filtro_ano)]

    cursor.execute(query, params)
    resultados = cursor.fetchall()

    if not resultados:
        print("Nenhuma despesa encontrada.")
    else:
        print(f"\n{'Categoria':<20} {'Valor (R$)':<12} {'Mês':<10} {'Ano':<6}")
        print("-" * 50)
        total = 0
        for cat, val, mes, ano in resultados:
            print(f"{cat:<20} {val:<12.2f} {mes:<10} {ano:<6}")
            total += val
        print("-" * 50)
        print(f"Total: R${total:.2f}")

    conn.close()

def analisar_despesas():

    openai.api_key = "....................."  # Coloque sua chave aqui

    # Lê todas as despesas do banco
    conn = sqlite3.connect(BANCO)
    df = pd.read_sql_query("SELECT categoria, valor, mes, ano FROM despesas", conn)
    conn.close()

    if df.empty:
        print("Nenhuma despesa encontrada para análise.")
        return

    # Converte DataFrame em tabela de texto
    dados_texto = df.to_csv(index=False)

    # Cria prompt para o ChatGPT
    prompt = f"""
    Você é um assistente financeiro. Analise os dados abaixo de despesas mensais.
    Retorne:
    - Total gasto por categoria
    - Média mensal por categoria
    - Maior e menor despesa
    - Principais insights e recomendações

    Dados:
    {dados_texto}
    """

    print("\nEnviando dados para análise pelo ChatGPT...")

    resposta = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # ou "gpt-3.5-turbo"
        #model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um analista financeiro."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=600
    )

    #resultado = resposta['choices'][0]['message']['content']
    #print("\nResultado da análise:\n")
    #print(resultado)
    resultado = resposta.choices[0].message.content
    print("\nResultado da análise:\n")
    print(resultado)

# Função principal
def main():
    criar_banco()

    print("=== Sistema de Registro de Despesas ===")
    print("1 - Inserir dados manualmente")
    print("2 - Inserir dados a partir de arquivo CSV")
    print("3 - Visualizar despesas")
    print("4 - Analisar despesas com ChatGPT")
    print("5 - Fim")
    escolha = input("Escolha uma opção (1, 2, 3, 4 ou 5): ")

    if escolha == "1":
        inserir_dados_manualmente()
    elif escolha == "2":
        caminho = input("Digite o caminho do arquivo CSV: ").strip()
        inserir_dados_csv(caminho)
    elif escolha == "3":
        visualizar_despesas()
    elif escolha == "4":
        analisar_despesas()
    elif escolha == "5":
        exit()
    else:
        print("Opção inválida!")

    print("\nOperação concluída!")


if __name__ == "__main__":
    main()
