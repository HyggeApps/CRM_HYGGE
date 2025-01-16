from pymongo.mongo_client import MongoClient
import yaml
import tempfile
import warnings
warnings.filterwarnings("ignore")

def create_temp_config_from_mongo(collection_users):


    # Buscar todos os usuários no MongoDB
    users_data = collection_users.find()

    # Criar um dicionário para armazenar os dados do config temporário
    temp_config_data = {
        'credentials': {
            'usernames': {}
        }
    }

    # Adicionar usuários do MongoDB ao config temporário
    for user_data in users_data:
        username = user_data['email']

        # Preparar os dados do usuário no formato do config.yaml
        user_yaml_data = {
            'email': user_data.get('email', ''),
            'failed_login_attempts': 0,
            'first_name': user_data.get('nome', ''),
            'last_name': user_data.get('sobrenome', ''),
            'logged_in': False,
            'password': user_data.get('senha', ''),  # Idealmente, a senha deve ser hasheada
            'roles': [user_data.get('hierarquia', 'viewer')]
        }

        # Adicionar o usuário ao config temporário
        temp_config_data['credentials']['usernames'][username] = user_yaml_data
        print(f"Usuário {username} adicionado ao config temporário.")

    # Criar um arquivo temporário para salvar o config.yaml (como texto)
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.yaml', encoding='utf-8') as temp_file:
        yaml.dump(temp_config_data, temp_file, default_flow_style=False)
        temp_file_path = temp_file.name

    print(f"Arquivo config temporário criado: {temp_file_path}")
    return temp_file_path

def load_config_and_check_or_insert_cookies(config_file_path):
    # Carregar o arquivo YAML existente
    try:
        with open(config_file_path, 'r') as file:
            config_data = yaml.safe_load(file)
            if config_data is None:
                config_data = {}  # Caso o arquivo esteja vazio
    except FileNotFoundError:
        config_data = {}  # Se o arquivo não existir ainda

    # Verificar e garantir que a seção 'cookie' exista
    if 'cookie' not in config_data:
        config_data['cookie'] = {
            'expiry_days': 0,
            'key': 'some_signature_key',
            'name': 'some_cookie_name'
        }
        print("Seção 'cookie' criada com valores padrão.")

    # Verificar se a chave 'name' está na seção 'cookie'
    cookie_name = config_data['cookie'].get('name')
    if not cookie_name:
        config_data['cookie']['name'] = 'some_cookie_name'
        print("Chave 'name' na seção 'cookie' criada com valor padrão.")

    # Salvar o arquivo atualizado
    with open(config_file_path, 'w') as file:
        yaml.dump(config_data, file, default_flow_style=False)

    return config_data

