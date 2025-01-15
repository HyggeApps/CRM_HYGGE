import requests

def firebase_json():
    # URL de download direto do Google Drive
    url = "https://drive.google.com/uc?id=1UIeLYKWoMn1yuUsZrnMRQlYfthyuzlt_&export=download"

    # Nome do arquivo local para salvar
    file_name = "firebase_credentials.json"

    try:
        # Fazer o download do arquivo
        response = requests.get(url)
        response.raise_for_status()  # Verificar se houve erro HTTP

        # Salvar o arquivo localmente
        with open(file_name, "wb") as file:
            file.write(response.content)

        return file_name
    except requests.exceptions.RequestException as e:
        return f"Erro ao baixar o arquivo: {e}"