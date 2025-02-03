import streamlit as st
import requests
from utils.database import get_collection
import pandas as pd
from datetime import datetime
from modules.contatos import *
from modules.atividades import *
from modules.tarefas import *

def buscar_dados_cnpj(cnpj):
    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def buscar_dados_cep(cep):
    url = f"https://viacep.com.br/ws/{cep}/json/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

@st.fragment
def editar_empresa(user, admin):
    if "empresa_selecionada" not in st.session_state or not st.session_state["empresa_selecionada"]:
        st.warning("Nenhuma empresa selecionada para edição.")
        return
    
    empresa = st.session_state["empresa_selecionada"]

    # Se admin for True, pode editar qualquer empresa
    # Se admin for False, só pode editar as empresas que possui
    eh_proprietario = admin or (user == empresa["Proprietário"])

    st.subheader("✏️ Editar Empresa")

    collection_usuarios = get_collection("usuarios")  # Coleção de usuários
    collection_empresas = get_collection("empresas")

    # Buscar os campos "nome", "sobrenome" e "email" para cada usuário
    usuarios = list(collection_usuarios.find({}, {"nome": 1, "sobrenome": 1, "email": 1}))

    # Formatar a lista de usuários para o formato: "nome sobrenome (email)"
    lista_usuarios = [f'{usuario["nome"]} {usuario["sobrenome"]} ({usuario["email"]})' for usuario in usuarios]
    lista_usuarios.sort()

    with st.form(key="form_edicao_empresa"):
        col1, col2 = st.columns(2)
        with col1:
            razao_social = st.text_input("Nome da Empresa *", value=empresa["Nome"], disabled=not eh_proprietario)
        with col2:
            cidade = st.text_input("Cidade *", value=empresa["Cidade"], disabled=True)  # Cidade não editável
        
        col3, col4 = st.columns(2)
        with col3:
            estado = st.text_input("Estado (UF)", value=empresa["UF"], disabled=True)  # Estado não editável
        with col4:
            novo_usuario = st.selectbox("Usuário (Vendedor)", options=lista_usuarios, 
                                        index=lista_usuarios.index(empresa["Proprietário"]) if empresa["Proprietário"] in lista_usuarios else 0, 
                                        disabled=not eh_proprietario)

        col5, col6 = st.columns(2)
        with col5:
            setor = st.selectbox("Setor *", ["Comercial", "Residencial", "Residencial MCMV", "Industrial"], 
                                 index=["Comercial", "Residencial", "Residencial MCMV", "Industrial"].index(empresa.get("Setor", "Comercial")), 
                                 disabled=not eh_proprietario)
        with col6:
            produto_interesse = st.selectbox("Produto de Interesse *", ["NBR Fast", "Consultoria NBR", "Consultoria HYGGE", "Consultoria Certificação"], 
                                             index=["NBR Fast", "Consultoria NBR", "Consultoria HYGGE", "Consultoria Certificação"].index(empresa.get("Produto de Interesse", "NBR Fast")), 
                                             disabled=not eh_proprietario)

        col7, col8 = st.columns(2)
        with col7:
            tamanho_empresa = st.selectbox("Tamanho da Empresa *", ["Tier 1", "Tier 2", "Tier 3", "Tier 4"], 
                                           index=["Tier 1", "Tier 2", "Tier 3", "Tier 4"].index(empresa.get("Tamanho da Empresa", "Tier 1")), 
                                           disabled=not eh_proprietario)

        submit = st.form_submit_button("💾 Salvar Alterações", disabled=not eh_proprietario)

        if submit and eh_proprietario:
            # Atualiza os dados no banco de dados
            collection_empresas.update_one(
                {"razao_social": empresa["Nome"]},
                {"$set": {
                    "razao_social": razao_social,
                    "usuario": novo_usuario,
                    "setor": setor,
                    "produto_interesse": produto_interesse,
                    "tamanho_empresa": tamanho_empresa,
                }}
            )
            
            st.success("Dados da empresa atualizados com sucesso!")
            st.rerun()     

@st.fragment            
def cadastrar_empresas(user, admin):
    collection_empresas = get_collection("empresas")
    collection_tarefas = get_collection("tarefas")  # Conectar com a coleção de tarefas

    st.header('Cadastro de Empresas')
    st.write('----')

    if "dados_cnpj" not in st.session_state:
        st.session_state["dados_cnpj"] = {}
    if "dados_cep" not in st.session_state:
        st.session_state["dados_cep"] = {}

    # 🔍 Busca CNPJ e CEP antes de exibir o formulário
    st.subheader("🔍 Busca Automática de CNPJ e CEP")
    with st.expander("Preencher Dados com CNPJ e CEP (dois cliques para buscar)"):
        col1, col2 = st.columns(2)
        with col1:
            cnpj_input = st.text_input("CNPJ", max_chars=18, placeholder="Digite o CNPJ", key="cnpj_input")
            if st.button("🔍 Buscar CNPJ", key="buscar_cnpj"):
                cnpj_limpo = cnpj_input.replace(".", "").replace("/", "").replace("-", "").replace(" ", "")
                if len(cnpj_limpo) == 14:
                    dados_cnpj = buscar_dados_cnpj(cnpj_limpo)
                    if dados_cnpj:
                        st.success("Dados do CNPJ encontrados!")
                        st.session_state["dados_cnpj"] = dados_cnpj
                    else:
                        st.error("CNPJ não encontrado!")
                else:
                    st.error("CNPJ inválido! Certifique-se de que tem 14 dígitos.")

        with col2:
            cep_input = st.text_input("CEP", max_chars=10, placeholder="Digite o CEP", key="cep_input")
            if st.button("🔍 Buscar CEP", key="buscar_cep"):
                cep_limpo = cep_input.replace("-", "").replace(" ", "")
                if len(cep_limpo) == 8:
                    dados_cep = buscar_dados_cep(cep_limpo)
                    if dados_cep:
                        st.success("Dados do CEP encontrados!")
                        st.session_state["dados_cep"] = dados_cep
                    else:
                        st.error("CEP não encontrado!")
                else:
                    st.error("CEP inválido! Certifique-se de que tem 8 dígitos.")

    # 📃 Formulário de Cadastro
    st.subheader("📃 Formulário de Cadastro")
    with st.form(key="form_cadastro_empresa"):
        col1, col2 = st.columns(2)
        with col1:
            razao_social = st.text_input("Nome da Empresa *", value=st.session_state["dados_cnpj"].get("nome", ""), key="razao_social")
        with col2:
            cnpj = st.text_input("CNPJ *", value=cnpj_input.replace(".", "").replace("/", "").replace("-", "").replace(" ", ""), max_chars=18, key="cnpj")

        col3, col4 = st.columns(2)
        with col3:
            cidade = st.text_input("Cidade *", value=st.session_state["dados_cnpj"].get("municipio", st.session_state["dados_cep"].get("localidade", "")), key="cidade")
        with col4:
            estado = st.text_input("Estado", value=st.session_state["dados_cnpj"].get("uf", st.session_state["dados_cep"].get("uf", "")), key="estado")

        col5, col6 = st.columns(2)
        with col5:
            setor = st.selectbox("Setor *", ["Comercial", "Residencial", "Residencial MCMV", "Industrial"], key="setor")
        with col6:
            produto_interesse = st.multiselect("Produto de Interesse *", 
                                               ["NBR Fast", "Consultoria NBR", "Consultoria HYGGE", "Consultoria Certificação"],
                                               key="produto_interesse")

        col7, col8 = st.columns(2)
        with col7:
            tamanho_empresa = st.selectbox("Tamanho da Empresa *", ["Tier 1", "Tier 2", "Tier 3", "Tier 4"], key="tamanho_empresa")
        with col8:
            grau_cliente = st.selectbox("Grau do Cliente", ["Lead", "Lead Qualificado", "Oportunidade", "Cliente"], key="grau_cliente", disabled=True)

        submit = st.form_submit_button("✅ Cadastrar")

        if submit:
            if not razao_social or not cnpj or not cidade or not setor or not produto_interesse or not tamanho_empresa:
                st.error("Preencha todos os campos obrigatórios!")
            else:
                existing_company = collection_empresas.find_one({"cnpj": cnpj})
                if existing_company:
                    st.error("Empresa já cadastrada com este CNPJ!")
                else:
                    # Registrar empresa
                    now = datetime.today().strftime("%Y-%m-%d")
                    document = {
                        "razao_social": razao_social,
                        "cnpj": cnpj,
                        "cidade": cidade,
                        "estado": estado,
                        "setor": setor,
                        "tamanho_empresa": tamanho_empresa,
                        "produto_interesse": produto_interesse,  # ✅ Agora é uma lista
                        "grau_cliente": grau_cliente,
                        "usuario": user,
                        "data_criacao": now,
                        "ultima_atividade": now,
                    }
                    collection_empresas.insert_one(document)

                    # Criar automaticamente uma tarefa associada à empresa
                    prazo_execucao = datetime.today().date() + timedelta(days=1)
                    tarefa_document = {
                        "titulo": "Identificar personas",
                        "empresa": cnpj,
                        "data_execucao": prazo_execucao.strftime("%Y-%m-%d"),
                        "observacoes": "Nova empresa cadastrada",
                        "status": "🟨 Em andamento"
                    }
                    collection_tarefas.insert_one(tarefa_document)

                    st.success("Empresa cadastrada com sucesso e tarefa inicial criada!")
                    st.rerun()

                    
@st.fragment
def consultar_empresas(user, admin):
    collection_empresas = get_collection("empresas")

    # Obter lista de vendedores
    vendedores = list(collection_empresas.distinct("usuario"))
    vendedores = [v for v in vendedores if v]

    # Filtros
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        filtro_razao_social = st.text_input("Nome", placeholder="Parte do nome da empresa")
    with col2:
        filtro_cidade = st.text_input("Cidade", placeholder="Digite a cidade")
    with col3:
        filtro_estado = st.text_input("Estado (UF)", max_chars=2, placeholder="Ex: SP")
    with col4:
        filtro_tamanho = st.multiselect("Tamanho", options=["Tier 1", "Tier 2", "Tier 3", "Tier 4"], default=[])
    with col5:
        filtro_vendedor = st.selectbox("Proprietário", options=["Todos"] + vendedores, index=0)
    with col6:
        filtro_data_atividade = st.date_input("Data da última atividade", value=None)

    # Construir query de filtro
    query = {}
    if filtro_razao_social:
        query["razao_social"] = {"$regex": filtro_razao_social, "$options": "i"}
    if filtro_cidade:
        query["cidade"] = {"$regex": filtro_cidade, "$options": "i"}
    if filtro_estado:
        query["estado"] = filtro_estado.upper()
    if filtro_tamanho:
        query["tamanho_empresa"] = {"$in": filtro_tamanho}
    if filtro_vendedor and filtro_vendedor != "Todos":
        query["usuario"] = filtro_vendedor
    if filtro_data_atividade:
        query["ultima_atividade"] = {"$gte": filtro_data_atividade.strftime("%Y-%m-%d")}

    # Buscar empresas no banco de dados com os filtros aplicados
    empresas_filtradas = list(
        collection_empresas.find(
            query,
            {
                "_id": 0,
                "razao_social": 1,
                "usuario": 1,
                "data_criacao": 1,
                "ultima_atividade": 1,
                "cidade": 1,
                "estado": 1,
                "setor": 1,
                "tamanho_empresa": 1,
                "produto_interesse": 1,
                "grau_cliente": 1,
                "cnpj": 1  
            },
        )
    )

    if empresas_filtradas:
        df_empresas = pd.DataFrame(empresas_filtradas)

        # ✅ Garantir que "CNPJ" existe antes de renomear colunas
        if "cnpj" in df_empresas.columns:
            df_empresas = df_empresas.rename(
                columns={
                    "razao_social": "Nome",
                    "usuario": "Proprietário",
                    "data_criacao": "Data de Criação",
                    "ultima_atividade": "Última Atividade",
                    "cidade": "Cidade",
                    "estado": "UF",
                    "setor": "Setor",
                    "tamanho_empresa": "Tamanho",
                    "produto_interesse": "Produto Interesse",
                    "grau_cliente": "Grau Cliente",
                    "cnpj": "CNPJ"
                }
            )
        else:
            st.error("Erro: O campo 'CNPJ' não foi encontrado no banco de dados.")

        # Adicionar a coluna "Visualizar" na primeira posição
        df_empresas.insert(0, "Visualizar", False)

        # ✅ Corrigir seleção no session_state
        empresa_cnpj_selecionada = st.session_state.get("empresa_cnpj_selecionada", None)

        if empresa_cnpj_selecionada and empresa_cnpj_selecionada in df_empresas["CNPJ"].values:
            df_empresas.loc[df_empresas["CNPJ"] == empresa_cnpj_selecionada, "Visualizar"] = True

        # Criar editor de dados interativo
        edited_df = st.data_editor(
            df_empresas,
            column_config={
                "Visualizar": st.column_config.CheckboxColumn(
                    "Visualizar",
                    help="Marque para ver detalhes da empresa"
                ),
            },
            disabled=["Nome", "Proprietário", "Data de Criação", "Última Atividade", "Cidade", "UF", "Setor", "Tamanho", "Produto Interesse", "Grau Cliente", "CNPJ"],
            hide_index=True,
            use_container_width=True
        )

        # 🔹 Atualiza a empresa selecionada corretamente
        novas_selecoes = edited_df[edited_df["Visualizar"]].index.tolist()

        # Se uma empresa foi selecionada, desmarcar todas as outras
        if novas_selecoes:
            selected_index = novas_selecoes[0]
            nova_empresa = edited_df.iloc[selected_index].to_dict()

            # Se a seleção mudou, atualizar session_state
            if empresa_cnpj_selecionada != nova_empresa["CNPJ"]:
                st.session_state["empresa_selecionada"] = nova_empresa
                st.session_state["empresa_cnpj_selecionada"] = nova_empresa["CNPJ"]
                st.rerun()  # 🔄 Garante a atualização imediata no UI

        # Se nenhuma empresa estiver marcada, limpar session_state corretamente
        elif empresa_cnpj_selecionada:
            del st.session_state["empresa_selecionada"]
            del st.session_state["empresa_cnpj_selecionada"]
            st.rerun()

        # Exibir detalhes da empresa selecionada
        if st.session_state.get("empresa_selecionada"):
            empresa = st.session_state["empresa_selecionada"]
            empresa_cnpj = empresa["CNPJ"]

            st.write('----')

            col1, col2 = st.columns([3.5, 6.5])
            with col1:
                st.write("### 🔍 Detalhes da empresa selecionada")
                with st.popover('✏️ Editar empresa'):
                    editar_empresa(user, admin)

                with st.expander("📋 Dados da Empresa", expanded=True):

                    collection_empresas = get_collection("empresas")
                    empresa_cnpj = st.session_state.get("empresa_cnpj_selecionada", None)

                    if empresa_cnpj:
                        empresa_atualizada = collection_empresas.find_one({"cnpj": empresa_cnpj}, {"_id": 0})

                        if empresa_atualizada:
                            dados_empresa = {
                                "Nome": empresa_atualizada.get("razao_social", ""),
                                "Proprietário": empresa_atualizada.get("usuario", ""),
                                "Última Atividade": empresa_atualizada.get("ultima_atividade", ""),
                                "Data de Criação": empresa_atualizada.get("data_criacao", ""),
                                "Cidade/UF": f"{empresa_atualizada.get('cidade', '')}, {empresa_atualizada.get('estado', '')}",
                                "Setor": empresa_atualizada.get("setor", ""),
                                "Tamanho": empresa_atualizada.get("tamanho_empresa", ""),
                                "Produto Interesse": empresa_atualizada.get("produto_interesse", ""),
                                "Grau Cliente": empresa_atualizada.get("grau_cliente", ""),
                                "CNPJ": empresa_atualizada.get("cnpj", "")
                            }

                            df_dados_empresa = pd.DataFrame(dados_empresa.items(), columns=["Campo", "Informação"])
                            st.dataframe(df_dados_empresa, hide_index=True, use_container_width=True)
                        else:
                            st.warning("Empresa não encontrada no banco de dados.")
                    else:
                        st.warning("Nenhuma empresa selecionada.")

                # Integrando a função de exibir contatos
                if empresa_cnpj:
                    st.write('----')
                    st.subheader("☎️ Informações sobre contatos")
                    exibir_contatos_empresa(user, admin, empresa_cnpj)
                else:
                    st.error("Erro ao carregar o CNPJ da empresa.")

            with col2:
                st.write("### 📜 Tarefas para a empresa")
                if empresa_cnpj:
                    gerenciamento_tarefas(user, admin, empresa_cnpj)
                st.write('----')
                st.write("### 📌 Histórico de atividades")
                
                if empresa_cnpj:
                    exibir_atividades_empresa(user, admin, empresa_cnpj)
                else:
                    st.error("Erro ao carregar o CNPJ da empresa.")

        else:
            st.write('----')
            st.info("Selecione uma empresa para ver os detalhes.")



@st.fragment
def excluir_empresa(user, admin):
    if "empresa_selecionada" not in st.session_state or not st.session_state["empresa_selecionada"]:
        st.warning("Nenhuma empresa selecionada para exclusão.")
        return
    
    empresa = st.session_state["empresa_selecionada"]

    # Se admin for True, pode excluir qualquer empresa
    # Se admin for False, só pode excluir as empresas que possui
    pode_excluir = admin

    if not pode_excluir:
        st.error("Você não tem permissão para excluir empresas, solicite para o administrador.")
        return
    else:
        collection_empresas = get_collection("empresas")
        collection_empresas.delete_one({"razao_social": empresa["Nome"]})

        st.success(f"Empresa **{empresa['Nome']}** foi removida com sucesso!")
        st.session_state["empresa_selecionada"] = None  # Limpa a seleção
        st.session_state["confirmar_exclusao"] = False
          # Recarrega a página


@st.fragment
def cadastrar_subempresa():
    collection_empresas = get_collection("empresas")
    collection_subempresas = get_collection("subempresas")

    st.header("Cadastrar sub-empresa na base de dados da HYGGE")
    st.info("Cadastre aqui uma sub-empresa ou variação da empresa matriz.")
    st.write('---')

    # Obter empresas matriz cadastradas
    empresas_matriz = list(collection_empresas.find({}, {"_id": 0, "razao_social": 1, "cnpj": 1}))
    opcoes_matriz = [f"{e['razao_social']} (CNPJ: {e['cnpj']})" for e in empresas_matriz]

    if not empresas_matriz:
        st.warning("Nenhuma empresa matriz encontrada. Cadastre uma empresa matriz antes de adicionar subempresas.")
    else:
        # Variáveis para preenchimento automático e controle de botões
        if "dados_cnpj_sub" not in st.session_state:
            st.session_state["dados_cnpj_sub"] = {}
        if "dados_cep_sub" not in st.session_state:
            st.session_state["dados_cep_sub"] = {}
        if "buscar_cnpj_sub_clicked" not in st.session_state:
            st.session_state["buscar_cnpj_sub_clicked"] = False
        if "buscar_cep_sub_clicked" not in st.session_state:
            st.session_state["buscar_cep_sub_clicked"] = False

        st.subheader("🔍 Busca Automática de CNPJ e CEP")
        with st.expander("Preencher Dados com CNPJ e CEP (dois cliques para buscar)"):
            col1, col2 = st.columns(2)
            with col1:
                cnpj_input = st.text_input("CNPJ da sub-empresa", max_chars=18, placeholder="Digite o CNPJ (com ou sem formatação)", key="cnpj_input_sub")
                buscar_cnpj = st.button("🔍 Buscar Dados do CNPJ (sub-empresa)", key="buscar_cnpj_sub")
            with col2:
                cep_input = st.text_input("CEP da sub-empresa", max_chars=10, placeholder="Digite o CEP (com ou sem formatação)", key="cep_input_sub")
                buscar_cep = st.button("🔍 Buscar Dados do CEP (sub-empresa)", key="buscar_cep_sub")

            if buscar_cnpj and not st.session_state["buscar_cnpj_sub_clicked"]:
                st.session_state["buscar_cnpj_sub_clicked"] = True
                cnpj_limpo = cnpj_input.replace(".", "").replace("/", "").replace("-", "").replace(" ", "")
                if len(cnpj_limpo) == 14:
                    dados_cnpj = buscar_dados_cnpj(cnpj_limpo)
                    if dados_cnpj and not dados_cnpj.get("erro"):
                        st.success("Dados do CNPJ encontrados!")
                        st.session_state["dados_cnpj_sub"] = dados_cnpj
                    else:
                        st.error("CNPJ não encontrado ou inválido!")
                        st.session_state["dados_cnpj_sub"] = {}
                else:
                    st.error("CNPJ inválido! Certifique-se de que o CNPJ tem 14 dígitos.")
                st.session_state["buscar_cnpj_sub_clicked"] = False

            if buscar_cep and not st.session_state["buscar_cep_sub_clicked"]:
                st.session_state["buscar_cep_sub_clicked"] = True
                cep_limpo = cep_input.replace("-", "").replace(" ", "")
                if len(cep_limpo) == 8:
                    dados_cep = buscar_dados_cep(cep_limpo)
                    if dados_cep and not dados_cep.get("erro"):
                        st.success("Dados do CEP encontrados!")
                        st.session_state["dados_cep_sub"] = dados_cep
                    else:
                        st.error("CEP não encontrado ou inválido!")
                        st.session_state["dados_cep_sub"] = {}
                else:
                    st.error("CEP inválido! Certifique-se de que o CEP tem 8 dígitos.")
                st.session_state["buscar_cep_sub_clicked"] = False

        # Formulário de Cadastro de sub-empresa
        with st.form(key="form_cadastro_subempresa"):
            st.subheader("📃 Formulário de Cadastro de sub-empresa")

            # Linha 1: Empresa Matriz e Razão Social
            col1, col2 = st.columns(2)
            with col1:
                empresa_matriz = st.selectbox("Empresa Matriz *", options=opcoes_matriz, key="select_empresa_matriz")
            with col2:
                razao_social = st.text_input("Razão Social da sub-empresa *", value=st.session_state["dados_cnpj_sub"].get("nome", ""), key="input_razao_social_subempresa")

            # Linha 2: CNPJ e Telefone
            col3, col4 = st.columns(2)
            with col3:
                cnpj = st.text_input("CNPJ da sub-empresa *", value=cnpj_input, max_chars=18, key="input_cnpj_subempresa")
            with col4:
                fone = st.text_input("Telefone", value=st.session_state["dados_cnpj_sub"].get("telefone", ""), key="input_fone_subempresa")

            # Linha 3: Rua e Bairro
            col5, col6 = st.columns(2)
            with col5:
                rua = st.text_input("Rua", value=st.session_state["dados_cnpj_sub"].get("logradouro", st.session_state["dados_cep_sub"].get("logradouro", "")), key="input_rua_subempresa")
            with col6:
                bairro = st.text_input("Bairro", value=st.session_state["dados_cnpj_sub"].get("bairro", st.session_state["dados_cep_sub"].get("bairro", "")), key="input_bairro_subempresa")

            # Linha 4: Cidade, Estado e CEP
            col7, col8, col9 = st.columns(3)
            with col7:
                cidade = st.text_input("Cidade", value=st.session_state["dados_cnpj_sub"].get("municipio", st.session_state["dados_cep_sub"].get("localidade", "")), key="input_cidade_subempresa")
            with col8:
                estado = st.text_input("Estado", value=st.session_state["dados_cnpj_sub"].get("uf", st.session_state["dados_cep_sub"].get("uf", "")), key="input_estado_subempresa")
            with col9:
                cep = st.text_input("CEP", value=cep_input, max_chars=10, key="input_cep_subempresa")

            # Botão para cadastrar
            submit_sub = st.form_submit_button("Cadastrar sub-empresa")

            if submit_sub:
                if razao_social and cnpj and empresa_matriz:
                    matriz_cnpj = empresa_matriz.split("CNPJ: ")[-1].strip(")")
                    existing_subempresa = collection_subempresas.find_one({"cnpj": cnpj})
                    if existing_subempresa:
                        st.error("Sub-empresa já cadastrada com este CNPJ!")
                    else:
                        document = {
                            "empresa_matriz": matriz_cnpj,
                            "razao_social": razao_social,
                            "cnpj": cnpj,
                            "rua": rua,
                            "cep": cep,
                            "bairro": bairro,
                            "cidade": cidade,
                            "estado": estado,
                            "fone": fone,
                        }
                        collection_subempresas.insert_one(document)
                        # Atualizar lista de subempresas na matriz
                        collection_empresas.update_one(
                            {"cnpj": matriz_cnpj},
                            {"$push": {"subempresas": cnpj}}
                        )
                        st.success("Sub-empresa cadastrada e vinculada à matriz com sucesso!")
                        st.rerun()
                        
                        
                        
                else:
                    st.error("Preencha todos os campos obrigatórios (Razão Social, CNPJ, Empresa Matriz).")