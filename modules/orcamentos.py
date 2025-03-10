import streamlit as st
from utils.database import get_collection
from datetime import datetime, timedelta
import pandas as pd
import datetime as dt
import calendar
import modules.gerar_orcamento as gro
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import re
import hashlib

def base36encode(number):
    """Converte um número inteiro para uma string em base36 (0-9, A-Z)."""
    if number < 0:
        raise ValueError("Número deve ser não-negativo")
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if number == 0:
        return alphabet[0]
    base36 = ""
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36
    return base36

def gerar_hash_8(objid):
    """
    Gera um hash de 8 caracteres (números e letras maiúsculas) a partir do _id.
    """
    # Calcula o MD5 do _id
    md5_hash = hashlib.md5(objid.encode("utf-8")).hexdigest()
    # Converte o hash MD5 para inteiro
    hash_int = int(md5_hash, 16)
    # 36^8 define o espaço de 8 dígitos em base36
    mod_value = 36**8
    # Faz o módulo para limitar o número ao intervalo desejado
    hash_mod = hash_int % mod_value
    # Converte o número para base36 e preenche com zeros à esquerda, se necessário, para garantir 8 caracteres
    hash_base36 = base36encode(hash_mod).zfill(8)
    return hash_base36

def calcular_parcelas_e_saldo(amount, parcela_fixa):
    # Calcula o número máximo de parcelas possíveis
    
    # Cria uma lista para armazenar as combinações
    combinacoes = []
    texto_prop = ". à partir do aceite da proposta ou assinatura do contrato,"
    texto_prop1 = ". após a entrega do laudo diagnóstico,"

    # Adiciona a opção à vista
    
    combinacoes.append(f"Total à vista de R$ {amount:,.2f}{texto_prop}".replace(",", "X").replace(".", ",").replace("X", "."))
    combinacoes.append(f"Total à vista de R$ {amount:,.2f}{texto_prop1}".replace(",", "X").replace(".", ",").replace("X", "."))
    if amount >= 12000 and amount < 18000: 
        combinacoes.append(f"2x de R$ {amount/2:,.2f}{texto_prop}".replace(",", "X").replace(".", ",").replace("X", "."))
    elif amount >= 18000 and amount < 24000: 
        combinacoes.append(f"2x de R$ {amount/2:,.2f}{texto_prop}".replace(",", "X").replace(".", ",").replace("X", "."))
        combinacoes.append(f"3x de R$ {amount/3:,.2f}{texto_prop}".replace(",", "X").replace(".", ",").replace("X", "."))
    elif amount >= 24000 and amount <= 30000:
        combinacoes.append(f"2x de R$ {amount/2:,.2f}{texto_prop}".replace(",", "X").replace(".", ",").replace("X", "."))
        combinacoes.append(f"3x de R$ {amount/3:,.2f}{texto_prop}".replace(",", "X").replace(".", ",").replace("X", "."))
        combinacoes.append(f"4x de R$ {amount/4:,.2f}{texto_prop}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Calcular a entrada e verificar a condição
    if amount > 30000:
        entrada = amount * 0.2
        saldo_restante = amount - entrada
        
        # Encontrar o menor múltiplo da parcela fixa que seja maior que o saldo restante
        num_parcelas = 10
        if saldo_restante % parcela_fixa != 0:
            num_parcelas += 1
        
        for i in range(1, int(num_parcelas)):
            saldo_a_pagar = saldo_restante / i
            if saldo_a_pagar >= parcela_fixa:
                combinacoes.append(
                    f"Entrada de {entrada:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + 
                    f" e {i}x de R$ {saldo_a_pagar:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
                                    
    return combinacoes

def format_currency(value):
    """
    Formata um valor numérico no padrão brasileiro de moeda:
    Exemplo: 10900.0 -> "R$ 10.900,00"
    """
    return "R$ " + "{:,.2f}".format(value).replace(",", "X").replace(".", ",").replace("X", ".")

def gerenciamento_aceites(user, email, senha):
    # Obter as coleções necessárias
    collection_empresas = get_collection("empresas")
    collection_oportunidades = get_collection("oportunidades")
    collection_contatos = get_collection("contatos")  # Supondo que exista uma coleção de contatos
    collection_produtos = get_collection("produtos")

    # 1. Seleção da Empresa
    empresas = list(
        collection_empresas.find(
            {"proprietario": user}, 
            {"_id": 0, "razao_social": 1, "cnpj": 1}
        )
    )
    if not empresas:
        st.warning("Nenhuma empresa encontrada para o usuário.")
        return

    opcoes_empresas = [f"{empresa['razao_social']}" for empresa in empresas]
    
    st.subheader("🏢 Seleção da empresa e negócio")
    selected_empresa = st.selectbox("**Selecione a Empresa:**", opcoes_empresas, key="orcamento_empresa")
    # Extrair o nome da empresa (razao_social) a partir da string
    empresa_nome = selected_empresa

    # 2. Seleção do Negócio (Oportunidade) vinculado à empresa selecionada
    oportunidades = list(
        collection_oportunidades.find(
            {"cliente": empresa_nome},
            {"_id": 1, "cliente": 1, "nome_oportunidade": 1, "proprietario": 1, "produtos": 1, "valor_estimado": 1, "valor_orcamento": 1, "data_criacao": 1, "data_fechamento": 1, "estagio": 1, 'aprovacao_gestor': 1, 'solicitacao_desconto': 1, 'desconto_solicitado': 1, 'desconto_aprovado': 1, 'contatos_selecionados': 1, 'contato_principal': 1, 'condicoes_pagamento': 1, 'prazo_execucao': 1}
        )
    )
    if not oportunidades:
        st.warning("Nenhum negócio encontrado para essa empresa.")
    else:
        opcoes_negocios = [opp["nome_oportunidade"] for opp in oportunidades]
        selected_negocio = st.selectbox("**Selecione o Negócio:**", opcoes_negocios, key="orcamento_negocio")

        # Buscar os dados    do negócio selecionado
        negocio_selecionado = next((opp for opp in oportunidades if opp["nome_oportunidade"] == selected_negocio), None)

        st.write('----')
        if negocio_selecionado:
            produtos = list(collection_produtos.find({}, {"_id": 0, "nome": 1, "categoria": 1, "preco": 1, "base_desconto": 1}))
            nomes_produtos = [p["nome"] for p in produtos]
            st.subheader("ℹ️ Informações do Negócio para o envio do email de aceite")
            
            negocio_id = gerar_hash_8(negocio_selecionado['_id'])
            st.text('Produto(s) selecionado(s) para o orçamento:')

            # Recupera os produtos já cadastrados no negócio (se houver)
            defaults = negocio_selecionado.get('produtos', [])
            
            # Define os defaults para cada coluna (se existir o índice correspondente, caso contrário, [] vazio)
            default1 = [defaults[0]] if len(defaults) >= 1 else []
            default2 = [defaults[1]] if len(defaults) >= 2 else []
            default3 = [defaults[2]] if len(defaults) >= 3 else []
            default4 = [defaults[3]] if len(defaults) >= 4 else []
            default5 = [defaults[4]] if len(defaults) >= 5 else []
            default6 = [defaults[5]] if len(defaults) >= 6 else []
            default7 = [defaults[6]] if len(defaults) >= 7 else []
            default8 = [defaults[7]] if len(defaults) >= 8 else []
            default9 = [defaults[8]] if len(defaults) >= 9 else []
            default10 = [defaults[9]] if len(defaults) >= 10 else []

            if len(default1) > 0: nomes_produtos.append(default1[0])
            if len(default2) > 0: nomes_produtos.append(default2[0])
            if len(default3) > 0: nomes_produtos.append(default3[0])
            if len(default4) > 0: nomes_produtos.append(default4[0])
            if len(default5) > 0: nomes_produtos.append(default5[0])
            if len(default6) > 0: nomes_produtos.append(default6[0])
            if len(default7) > 0: nomes_produtos.append(default7[0])
            if len(default8) > 0: nomes_produtos.append(default8[0])
            if len(default9) > 0: nomes_produtos.append(default9[0])
            if len(default10) > 0: nomes_produtos.append(default10[0])
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                produtos_selecionado1 = st.multiselect(
                    "Produto 1:",
                    options=nomes_produtos,
                    default=default1,
                    key="select_produto_oportunidade1",
                    placeholder='Selecione aqui...',
                    disabled=True
                )
            with col2:
                produtos_selecionado2 = st.multiselect(
                    "Produto 2:",
                    options=nomes_produtos,
                    default=default2,
                    key="select_produto_oportunidade2",
                    placeholder='Selecione aqui...',
                    disabled=True
                )
            with col3:
                produtos_selecionado3 = st.multiselect(
                    "Produto 3:",
                    options=nomes_produtos,
                    default=default3,
                    key="select_produto_oportunidade3",
                    placeholder='Selecione aqui...',
                    disabled=True
                )
            with col4:
                produtos_selecionado4 = st.multiselect(
                    "Produto 4:",
                    options=nomes_produtos,
                    default=default4,
                    key="select_produto_oportunidade4",
                    placeholder='Selecione aqui...',
                    disabled=True
                )
            with col5:
                produtos_selecionado5 = st.multiselect(
                    "Produto 5:",
                    options=nomes_produtos,
                    default=default5,
                    key="select_produto_oportunidade5",
                    placeholder='Selecione aqui...',
                    disabled=True
                )
            
            col6, col7, col8, col9, col10 = st.columns(5)
            with col6:
                produtos_selecionado6 = st.multiselect(
                    "Produto 6:",
                    options=nomes_produtos,
                    default=default6,
                    key="select_produto_oportunidade6",
                    placeholder='Selecione aqui...',
                    disabled=True
                )
            with col7:
                produtos_selecionado7 = st.multiselect(
                    "Produto 7:",
                    options=nomes_produtos,
                    default=default7,
                    key="select_produto_oportunidade7",
                    placeholder='Selecione aqui...',
                    disabled=True
                )
            with col8:
                produtos_selecionado8 = st.multiselect(
                    "Produto 8:",
                    options=nomes_produtos,
                    default=default8,
                    key="select_produto_oportunidade8",
                    placeholder='Selecione aqui...',
                    disabled=True
                )
            with col9:
                produtos_selecionado9 = st.multiselect(
                    "Produto 9:",
                    options=nomes_produtos,
                    default=default9,
                    key="select_produto_oportunidade9",
                    placeholder='Selecione aqui...',
                    disabled=True
                )
            with col10:
                produtos_selecionado10 = st.multiselect(
                    "Produto 10:",
                    options=nomes_produtos,
                    default=default10,
                    key="select_produto_oportunidade10",
                    placeholder='Selecione aqui...',
                    disabled=True
                )

            produtos_selecionados = [p[0] for p in [produtos_selecionado1, produtos_selecionado2, produtos_selecionado3, produtos_selecionado4, produtos_selecionado5,
                                        produtos_selecionado6, produtos_selecionado7, produtos_selecionado8, produtos_selecionado9, produtos_selecionado10] if p]
            
            negocio_selecionado['produtos'] = produtos_selecionados

            if len(produtos_selecionados) > 0:
                #st.write(negocio_selecionado)
                produtos_dict = {p["nome"]: p for p in produtos}

                # Itera sobre a lista de produtos selecionados, adicionando o objeto correspondente para cada ocorrência
                produtos_selecionados_obj = [
                    produtos_dict[nome] for nome in negocio_selecionado['produtos'] if nome in produtos_dict
                ]
                
                valor_negocio_formatado = negocio_selecionado['valor_orcamento']
                valor_negocio = float(valor_negocio_formatado.replace('R$ ','').replace('.','').replace(',','.'))
                st.text_input('Valor do orçamento:', value=f"{valor_negocio_formatado}", disabled=True)
                #**Preço com o desconto aplicado:** {valor_negocio_formatado}")
                condicoes = calcular_parcelas_e_saldo(valor_negocio, 6000)
                
                # Valor salvo no banco para a condição de pagamento (se existir)
                default_condicao = negocio_selecionado.get('condicoes_pagamento', None)

                # Se existir e estiver na lista de opções, encontra o índice correspondente;
                # caso contrário, usa o índice 0 (primeira opção da lista)
                if default_condicao and default_condicao in condicoes:
                    default_index = condicoes.index(default_condicao)
                else:
                    default_index = 0

                condicao_pagamento = st.selectbox('Condições de pagamento:', condicoes, index=default_index, disabled=True)

                if float(valor_negocio) > 35000:
                    prazos = ['60 dias úteis após o recebimento da documentação completa.',
                            '30 dias úteis após o recebimento da documentação completa.',
                            '20 dias úteis após o recebimento da documentação completa.']
                
                else: prazos = ['60 dias úteis após o recebimento da documentação completa.',
                            '30 dias úteis após o recebimento da documentação completa.',
                            '20 dias úteis após o recebimento da documentação completa.',
                            '15 dias úteis após o recebimento da documentação completa.',
                            '10 dias úteis após o recebimento da documentação completa.']

                # 1. Prazo de execução
                default_prazo = negocio_selecionado.get('prazo_execucao', None)
                if default_prazo and default_prazo in prazos:
                    prazo_index = prazos.index(default_prazo)
                else:
                    prazo_index = 0
                prazo = st.selectbox("Prazo de execução:", prazos, index=prazo_index, disabled=True)

                # 2. Seleção dos Contatos da Empresa (pode ser múltiplo)
                contatos = list(
                    collection_contatos.find(
                        {"empresa": empresa_nome},
                        {"_id": 0, "nome": 1, "email": 1, "sobrenome": 1}  # Incluindo sobrenome para contato principal
                    )
                )
                if contatos:
                    opcoes_contatos = [f"{c.get('email', 'Sem email')}" for c in contatos]
                    nomes_contatos = [f"{c.get('nome', 'Sem nome')} {c.get('sobrenome', '')}" for c in contatos]

                    # Valor padrão para contatos selecionados (campo 'contatos_selecionados' da oportunidade)
                    default_contatos = negocio_selecionado.get("contatos_selecionados", [])
                    # Filtra os defaults para que estejam entre as opções disponíveis
                    default_contatos = [d for d in default_contatos if d in opcoes_contatos]

                    selected_contatos = st.multiselect(
                        "Selecione os contatos da empresa que receberão o orçamento:",
                        opcoes_contatos,
                        key="orcamento_contatos",
                        placeholder='Selecione os contatos aqui...',
                        default=default_contatos
                    )

                    # Valor padrão para o contato principal (campo 'contato_principal' da oportunidade)
                    default_contato_principal = negocio_selecionado.get("contato_principal", None)
                    if default_contato_principal and default_contato_principal in nomes_contatos:
                        contato_index = nomes_contatos.index(default_contato_principal)
                    else:
                        contato_index = 0
                    nome_contato_principal = st.selectbox(
                        "Selecione o contato principal (A/C):",
                        nomes_contatos,
                        key="orcamento_contato_principal",
                        index=contato_index
                    )

                else:
                    st.error("Nenhum contato encontrado para essa empresa.")
                    selected_contatos = []


                st.write('----')

                st.subheader("🤝 Informações relevantes para o técnico/financeiro")
                st.info('Preencha todos os campos com "*" para habilitar a etapa de criação de pastas e envio de email.')

                col1, col2, col3 = st.columns(3)
                with col1: tipo_contrato_answ = st.selectbox('Contrato ou somente proposta?*',options=['-','Contrato', 'Somente proposta'])
                with col2: resp_contrato_answ = st.selectbox('Quem é responsável pelo contrato?*',options=['-','HYGGE','Contratante','Não definido'])
                with col3: nro_parcelas_answ = st.selectbox('Número de parcelas?*',options=['-','1x','2x','3x','4x','5x','6x','Não definido'])
   
                col1, col2, col3 = st.columns(3)
                with col1: parceria_answ = st.selectbox('Tem parceria?*', options=['-','Sim, Scala','Não'])
                with col2: entrada_answ = st.selectbox('Haverá o pagamento de entrada?*',options=['-','Sim','Não'])
                with col3: parcelas_vinc_ent_answ = st.selectbox('Demais parcelas vinculadas às entregas?*',options=['-','Sim','Não'])
                
                col1, col2, col3 = st.columns(3)
                with col1: comentarios_answ = st.text_area('Comentários relevantes (condições acordadas):*')
                with col2: contato_financeiro_answ = st.text_area('Contato financeiro (nome e email) *')
                with col3: contatos_answ = st.text_area('Contatos adicionais')


                # escopo (produtos) no email;
                # prazo informado para entrega - automatico no email;

                # Adicionar as informações completas no email. 

                st.write('---')

                if tipo_contrato_answ != '-' and nro_parcelas_answ != '-' and parcelas_vinc_ent_answ != '-' and resp_contrato_answ != '-' and entrada_answ != '-' and len(parceria_answ) > 0 and len(comentarios_answ) > 0 and len(contato_financeiro_answ) > 0: 
                    
                    st.subheader("📨 Envio do email de aceite para o cliente")
                    
                    st.error(f"**ALERTA:** Ao clicar no botão abaixo o e-mail de aceite de proposta será enviado para o(s) cliente(s) (**{selected_contatos}**) e a pasta será gerada no servidor, você tem certeza?",icon='🚨')

                    if st.button("Criar pasta no servidor e enviar email de aceite para o cliente"):
                        with st.spinner('Espere a conclusão da operação...'):

                            # Atualiza o documento da oportunidade com as novas informações
                            collection_oportunidades.update_one(
                                {"cliente": empresa_nome, "nome_oportunidade": selected_negocio},
                                {"$set": {
                                    "contrato_proposta": tipo_contrato_answ,
                                    "responsavel_contrato": resp_contrato_answ,
                                    "nro_parcelas": nro_parcelas_answ,
                                    "parceria": parceria_answ,
                                    "entrada": entrada_answ,
                                    "parcelas_vinc_ent": parcelas_vinc_ent_answ,
                                    "contato_financeiro": contato_financeiro_answ,
                                    "comentarios_relevantes": comentarios_answ,
                                    "contatos_adicionais": contatos_answ
                                }}
                            )

                            # Configuração do email
                            #receivers = ['paula@hygge.eco.br','financeiro@hygge.eco.br', 'rodrigo@hygge.eco.br','alexandre@hygge.eco.br','fabricio@hygge.eco.br', email]
                            receivers = ['rodrigokarinileitzke@gmail.com']
                            message = MIMEMultipart()
                            message["From"] = email
                            message["To"] = ", ".join(receivers)
                            message["Subject"] = f'[Hygge & {selected_empresa}] Informações adicionais - {selected_negocio} (EMAIL INTERNO)'

                            # Corpo do email original
                            body = f"""<p>Olá a todos, espero que estejam bem.<br></p>
                            <p>A respeito do fechamento {selected_negocio} (em anexo):<br></p>
                            <p>Contrato ou somente proposta? {tipo_contrato_answ}<br></p>
                            <p>Quem é responsável pelo contrato? {resp_contrato_answ}<br></p>
                            <p>Nro. de parcelas: {nro_parcelas_answ}<br></p>
                            <p>Parceria? {parceria_answ}<br></p>
                            <p>Entrada? {entrada_answ}<br></p>
                            <p>Demais parcelas vinculadas à entrega? {parcelas_vinc_ent_answ}<br></p>
                            <p>Valor do orçamento: {valor_negocio_formatado}<br></p>
                            <p>Condições de pagamento: {condicao_pagamento}<br></p>
                            <p>Prazo informado para entrega: {prazo}<br></p>
                            <p>Comentários relevantes: {comentarios_answ}<br></p>
                            <p>Contato financeiro: {contato_financeiro_answ}<br></p>
                            <p>Contatos adicionais: {contatos_answ}<br></p>

                            <p>Atenciosamente,</p>"""

                            if email == 'comercial2@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/thiago-lecheta.html"
                            elif email == 'matheus@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/matheus-duarte.html"
                            elif email == 'fabricio@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/fabricio-lucchesi.html"
                            elif email == 'alexandre@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/alexandre-castagini.html"
                            elif email == 'comercial8@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/renan-bertolini-rozov.html"
                            elif email == 'comercial6@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/maria-eduarda-ferreira.html"  
                            elif email == 'comercial5@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/matheus-rodrigues.html"  
                            elif email == 'comercial4@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/alceu-junior.html"   
                            elif email == 'comercial3@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/victor-oliveira.html"
                            elif email == 'comercial1@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/fernando-tohme.html"
                            elif email == 'rodrigo@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/rodrigo-leitzke.html"
                            elif email == 'admin@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/alexandre-castagini.html"

                                
                            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                            response = requests.get(url, headers=headers)
                            html_signature = response.text

                            # Concatena o corpo do email com a assinatura HTML
                            full_body = body + html_signature

                            # Anexa o corpo do email completo no formato HTML
                            message.attach(MIMEText(full_body, "html"))

                            path_proposta_envio = gro.get_versao(f"{selected_negocio}_{negocio_id}")
            
                            if path_proposta_envio:
                                novo_nome_arquivo = os.path.basename(path_proposta_envio)
                            else:
                                st.error("Erro ao encontrar o arquivo da proposta.")
                                return

                            # Attach the PDF file
                            with open(path_proposta_envio, 'rb') as attachment:
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(attachment.read())
                                encoders.encode_base64(part)
                                part.add_header('Content-Disposition', 'attachment', filename=novo_nome_arquivo)
                                message.attach(part)

                                # Sending the email
                            try:
                                server = smtplib.SMTP('smtp.office365.com', 587)
                                server.starttls()
                                server.login(email, senha)
                                server.sendmail(email, receivers, message.as_string())
                                server.quit()
                                st.success("Etapa 1 de 3 - Email 1 enviado com sucesso para a equipe interna!")

                            except Exception as e:
                                st.error(f"Falha no envio do email: {e}")

                            # Configuração do email
                            #receivers = selected_contatos + ['fabricio@hygge.eco.br','alexandre@hygge.eco.br','rodrigo@hygge.eco.br','paula@hygge.eco.br','financeiro@hygge.eco.br', email]
                            receivers = ['rodrigo@hygge.eco.br']
                            message = MIMEMultipart()
                            message["From"] = email
                            message["To"] = ", ".join(receivers)
                            message["Subject"] = f'[Hygge & {selected_empresa}] Proposta Técnico-Comercial ACEITA - {selected_negocio}'

                            # Corpo do email original
                            body = f"""<p>Olá a todos, espero que estejam bem.<br></p>
                            <p>Conforme tratativas entre {nome_contato_principal} e {user}, recebemos o aceite da proposta {selected_negocio} (em anexo).<br></p>
                            <p>Portanto, é com grande satisfação que se inicia nossa parceria para o empreendimento {selected_negocio}!<br></p>
                            <p>Entro em contato para adicionar a Vanessa Godoi do setor financeiro da Hygge (financeiro@hygge.eco.br), a qual entrará em contato para dar continuidade às tratativas referentes à contratos e pagamentos.<br></p>
                            <p>Também incluo a Paula Alano (paula@hygge.eco.br), sócia e coordenadora de projetos, que liderará a equipe técnica da Hygge e será a sua ponte de comunicação para assuntos técnicos.
                            A Paula entrará em contato solicitando as informações necessárias para darmos início ao processo da Análise Hygge.<br></p>
                            <p>Agradecemos a confiança em nosso trabalho e destaco nosso comprometimento total para que nossa parceria seja bem-sucedida.<br></p>
                            <p>Atenciosamente,</p>"""

                            if email == 'comercial2@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/thiago-lecheta.html"
                            elif email == 'matheus@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/matheus-duarte.html"
                            elif email == 'fabricio@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/fabricio-lucchesi.html"
                            elif email == 'alexandre@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/alexandre-castagini.html"
                            elif email == 'comercial8@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/renan-bertolini-rozov.html"
                            elif email == 'comercial6@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/maria-eduarda-ferreira.html"  
                            elif email == 'comercial5@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/matheus-rodrigues.html"  
                            elif email == 'comercial4@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/alceu-junior.html"   
                            elif email == 'comercial3@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/victor-oliveira.html"
                            elif email == 'comercial1@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/fernando-tohme.html"
                            elif email == 'rodrigo@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/rodrigo-leitzke.html"
                            elif email == 'admin@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/alexandre-castagini.html"

                                
                            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                            response = requests.get(url, headers=headers)
                            html_signature = response.text

                            # Concatena o corpo do email com a assinatura HTML
                            full_body = body + html_signature

                            # Anexa o corpo do email completo no formato HTML
                            message.attach(MIMEText(full_body, "html"))

                            path_proposta_envio = gro.get_versao(f"{selected_negocio}_{negocio_id}")
            
                            if path_proposta_envio:
                                novo_nome_arquivo = os.path.basename(path_proposta_envio)
                            else:
                                st.error("Erro ao encontrar o arquivo da proposta.")
                                return

                            # Attach the PDF file
                            with open(path_proposta_envio, 'rb') as attachment:
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(attachment.read())
                                encoders.encode_base64(part)
                                part.add_header('Content-Disposition', 'attachment', filename=novo_nome_arquivo)
                                message.attach(part)

                                # Sending the email
                            try:
                                server = smtplib.SMTP('smtp.office365.com', 587)
                                server.starttls()
                                server.login(email, senha)
                                server.sendmail(email, receivers, message.as_string())
                                server.quit()
                                st.success("Etapa 2 de 3 - Email 2 enviado com sucesso para a equipe interna e para o cliente!")
                                for i in range(10):
                                    st.balloons()
                                    time.sleep(1)
                            except Exception as e:
                                st.error(f"Falha no envio do email: {e}")
                            
                            gro.upload_to_3projetos_v02(f'{selected_negocio}'.upper())
                            
                            st.success("Etapa 3 de 3 - Parabéns pela venda! Informações atualizadas no servidor e pastas criadas.")
                            for i in range(10):
                                st.balloons()
                                time.sleep(1)

                    st.write('------')

                    st.subheader("📨 Envio do email de aceite interno")

                    st.error(f"**ALERTA:** Ao clicar no botão abaixo a pasta será gerada no servidor **e um email de notificação será enviado para a equipe interna da Hygge, sem o envio do email para o cliente**, você tem certeza?",icon='🚨')
                    if st.button("Criar pasta no servidor e enviar email interno"):#, #disabled=st.session_state['button_disabled']):
                        with st.spinner('Espere a conclusão da operação...'):
                            
                            # Atualiza o documento da oportunidade com as novas informações
                            collection_oportunidades.update_one(
                                {"cliente": empresa_nome, "nome_oportunidade": selected_negocio},
                                {"$set": {
                                    "contrato_proposta": tipo_contrato_answ,
                                    "responsavel_contrato": resp_contrato_answ,
                                    "nro_parcelas": nro_parcelas_answ,
                                    "parceria": parceria_answ,
                                    "entrada": entrada_answ,
                                    "parcelas_vinc_ent": parcelas_vinc_ent_answ,
                                    "contato_financeiro": contato_financeiro_answ,
                                    "comentarios_relevantes": comentarios_answ,
                                    "contatos_adicionais": contatos_answ
                                }}
                            )
                            
                            # st.session_state['button_disabled'] = True
                            # Configuração do email
                            #receivers = ['paula@hygge.eco.br','financeiro@hygge.eco.br', 'rodrigo@hygge.eco.br','alexandre@hygge.eco.br','fabricio@hygge.eco.br', selected_email]
                            receivers = ['rodrigokarinileitzke@gmail.com']
                            message = MIMEMultipart()
                            message["From"] = email
                            message["To"] = ", ".join(receivers)
                            message["Subject"] = f'[Hygge & {selected_empresa}] Informações adicionais - {selected_negocio} (EMAIL INTERNO)'

                            # Corpo do email original
                            body = f"""<p>Olá a todos, espero que estejam bem.<br></p>
                            <p>A respeito do fechamento {selected_negocio} (em anexo):<br></p>
                            <p>Contrato ou somente proposta? {tipo_contrato_answ}<br></p>
                            <p>Quem é responsável pelo contrato? {resp_contrato_answ}<br></p>
                            <p>Nro. de parcelas: {nro_parcelas_answ}<br></p>
                            <p>Parceria? {parceria_answ}<br></p>
                            <p>Entrada? {entrada_answ}<br></p>
                            <p>Demais parcelas vinculadas à entrega? {parcelas_vinc_ent_answ}<br></p>
                            <p>Valor do orçamento: {valor_negocio_formatado}<br></p>
                            <p>Condições de pagamento: {condicao_pagamento}<br></p>
                            <p>Prazo informado para entrega: {prazo}<br></p>
                            <p>Comentários relevantes: {comentarios_answ}<br></p>
                            <p>Contato financeiro: {contato_financeiro_answ}<br></p>
                            <p>Contatos adicionais: {contatos_answ}<br></p>

                            <p>Atenciosamente,</p>"""

                            if email == 'comercial2@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/thiago-lecheta.html"
                            elif email == 'matheus@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/matheus-duarte.html"
                            elif email == 'fabricio@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/fabricio-lucchesi.html"
                            elif email == 'alexandre@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/alexandre-castagini.html"
                            elif email == 'comercial8@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/renan-bertolini-rozov.html"
                            elif email == 'comercial6@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/maria-eduarda-ferreira.html"  
                            elif email == 'comercial5@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/matheus-rodrigues.html"  
                            elif email == 'comercial4@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/alceu-junior.html"   
                            elif email == 'comercial3@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/victor-oliveira.html"
                            elif email == 'comercial1@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/fernando-tohme.html"
                            elif email == 'rodrigo@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/rodrigo-leitzke.html"
                            elif email == 'admin@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/alexandre-castagini.html"

                                
                            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                            response = requests.get(url, headers=headers)
                            html_signature = response.text

                            # Concatena o corpo do email com a assinatura HTML
                            full_body = body + html_signature

                            # Anexa o corpo do email completo no formato HTML
                            message.attach(MIMEText(full_body, "html"))

                            path_proposta_envio = gro.get_versao(f"{selected_negocio}_{negocio_id}")
                            
                            if path_proposta_envio:
                                novo_nome_arquivo = os.path.basename(path_proposta_envio)
                            else:
                                st.error("Erro ao encontrar o arquivo da proposta.")
                                return

                            # Attach the PDF file
                            with open(path_proposta_envio, 'rb') as attachment:
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(attachment.read())
                                encoders.encode_base64(part)
                                part.add_header('Content-Disposition', 'attachment', filename=novo_nome_arquivo)
                                message.attach(part)

                                # Sending the email
                            try:
                                server = smtplib.SMTP('smtp.office365.com', 587)
                                server.starttls()
                                server.login(email, senha)
                                server.sendmail(email, receivers, message.as_string())
                                server.quit()
                                st.success("Etapa 1 de 3 - Email 1 enviado com sucesso para a equipe interna!")

                            except Exception as e:
                                st.error(f"Falha no envio do email: {e}")


                            # Configuração do email
                            #receivers = ['fabricio@hygge.eco.br','admin@hygge.eco.br','rodrigo@hygge.eco.br','paula@hygge.eco.br','financeiro@hygge.eco.br', email]
                            receivers = ['rodrigokarinileitzke@gmail.com']
                            message = MIMEMultipart()
                            message["From"] = email
                            message["To"] = ", ".join(receivers)
                            message["Subject"] = f'[Hygge & {selected_empresa}] Proposta Técnico-Comercial ACEITA - {selected_negocio} (EMAIL INTERNO)'

                            # Corpo do email original
                            body = f"""<p>Olá a todos, espero que estejam bem.<br></p>
                            <p>Conforme tratativas entre {nome_contato_principal} e {user}, recebemos o aceite da proposta {selected_negocio} (em anexo).<br></p>
                            <p>Atenciosamente,</p>"""

                            if email == 'comercial2@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/thiago-lecheta.html"
                            elif email == 'matheus@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/matheus-duarte.html"
                            elif email == 'fabricio@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/fabricio-lucchesi.html"
                            elif email == 'alexandre@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/alexandre-castagini.html"
                            elif email == 'comercial8@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/renan-bertolini-rozov.html"
                            elif email == 'comercial6@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/maria-eduarda-ferreira.html"  
                            elif email == 'comercial5@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/matheus-rodrigues.html"  
                            elif email == 'comercial4@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/alceu-junior.html"   
                            elif email == 'comercial3@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/victor-oliveira.html"
                            elif email == 'comercial1@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/fernando-tohme.html"
                            elif email == 'rodrigo@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/rodrigo-leitzke.html"
                            elif email == 'admin@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/alexandre-castagini.html"

                                
                            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                            response = requests.get(url, headers=headers)
                            html_signature = response.text

                            # Concatena o corpo do email com a assinatura HTML
                            full_body = body + html_signature

                            # Anexa o corpo do email completo no formato HTML
                            message.attach(MIMEText(full_body, "html"))

                            # Attach the PDF file
                            with open(path_proposta_envio, 'rb') as attachment:
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(attachment.read())
                                encoders.encode_base64(part)
                                part.add_header('Content-Disposition', 'attachment', filename=novo_nome_arquivo)
                                message.attach(part)

                                # Sending the email
                            try:
                                server = smtplib.SMTP('smtp.office365.com', 587)
                                server.starttls()
                                server.login(email, senha)
                                server.sendmail(email, receivers, message.as_string())
                                server.quit()
                                st.success("Etapa 2 de 3 - Email 2 enviado com sucesso para a equipe interna!")
                                for i in range(10):
                                    st.balloons()
                                    time.sleep(1)

                            except Exception as e:
                                st.error(f"Falha no envio do email: {e}")
                            
                            gro.upload_to_3projetos_v02(f'{selected_negocio}'.upper())
                            st.success("Etapa 3 de 3 - Parabéns pela venda! Informações atualizadas no servidor e pastas criadas.")
                            for i in range(10):
                                st.balloons()
                                time.sleep(1)
                    
                    
                    
                
def elaborar_orcamento(user, email, senha):
    # Obter as coleções necessárias
    collection_empresas = get_collection("empresas")
    collection_oportunidades = get_collection("oportunidades")
    collection_contatos = get_collection("contatos")  # Supondo que exista uma coleção de contatos
    collection_produtos = get_collection("produtos")

    # 1. Seleção da Empresa
    empresas = list(
        collection_empresas.find(
            {"proprietario": user}, 
            {"_id": 0, "razao_social": 1, "cnpj": 1}
        )
    )
    if not empresas:
        st.warning("Nenhuma empresa encontrada para o usuário.")
        return

    opcoes_empresas = [f"{empresa['razao_social']}" for empresa in empresas]
    
    st.subheader("🏢 Seleção da empresa e negócio")
    selected_empresa = st.selectbox("**Selecione a Empresa:**", opcoes_empresas, key="orcamento_empresa")
    # Extrair o nome da empresa (razao_social) a partir da string
    empresa_nome = selected_empresa

    # 2. Seleção do Negócio (Oportunidade) vinculado à empresa selecionada
    oportunidades = list(
        collection_oportunidades.find(
            {"cliente": empresa_nome},
            {"_id": 1, "cliente": 1, "nome_oportunidade": 1, "proprietario": 1, "produtos": 1, "valor_estimado": 1,"valor_orcamento": 1, "data_criacao": 1, "data_fechamento": 1, "estagio": 1, 'aprovacao_gestor': 1, 'solicitacao_desconto': 1, 'desconto_solicitado': 1, 'desconto_aprovado': 1, 'contatos_selecionados': 1, 'contato_principal': 1, 'condicoes_pagamento': 1, 'prazo_execucao': 1}
        )
    )
    if not oportunidades:
        st.warning("Nenhum negócio encontrado para essa empresa.")
    else:
        opcoes_negocios = [opp["nome_oportunidade"] for opp in oportunidades]
        selected_negocio = st.selectbox("**Selecione o Negócio:**", opcoes_negocios, key="orcamento_negocio")

        # Buscar os dados    do negócio selecionado
        negocio_selecionado = next((opp for opp in oportunidades if opp["nome_oportunidade"] == selected_negocio), None)

        st.write('----')
        if negocio_selecionado:
            produtos = list(collection_produtos.find({}, {"_id": 0, "nome": 1, "categoria": 1, "preco": 1, "base_desconto": 1}))
            nomes_produtos = [p["nome"] for p in produtos]
            st.subheader("ℹ️ Informações do Negócio para orçamento")

            negocio_id = gerar_hash_8(negocio_selecionado['_id'])
            st.text('Selecione o(s) produto(s) para o orçamento:')

            # Recupera os produtos já cadastrados no negócio (se houver)
            defaults = negocio_selecionado.get('produtos', [])
            
            # Define os defaults para cada coluna (se existir o índice correspondente, caso contrário, [] vazio)
            default1 = [defaults[0]] if len(defaults) >= 1 else []
            default2 = [defaults[1]] if len(defaults) >= 2 else []
            default3 = [defaults[2]] if len(defaults) >= 3 else []
            default4 = [defaults[3]] if len(defaults) >= 4 else []
            default5 = [defaults[4]] if len(defaults) >= 5 else []
            default6 = [defaults[5]] if len(defaults) >= 6 else []
            default7 = [defaults[6]] if len(defaults) >= 7 else []
            default8 = [defaults[7]] if len(defaults) >= 8 else []
            default9 = [defaults[8]] if len(defaults) >= 9 else []
            default10 = [defaults[9]] if len(defaults) >= 10 else []
            
            if len(default1) > 0: nomes_produtos.append(default1[0])
            if len(default2) > 0: nomes_produtos.append(default2[0])
            if len(default3) > 0: nomes_produtos.append(default3[0])
            if len(default4) > 0: nomes_produtos.append(default4[0])
            if len(default5) > 0: nomes_produtos.append(default5[0])
            if len(default6) > 0: nomes_produtos.append(default6[0])
            if len(default7) > 0: nomes_produtos.append(default7[0])
            if len(default8) > 0: nomes_produtos.append(default8[0])
            if len(default9) > 0: nomes_produtos.append(default9[0])
            if len(default10) > 0: nomes_produtos.append(default10[0])
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                produtos_selecionado1 = st.multiselect(
                    "Produto 1:",
                    options=nomes_produtos,
                    default=default1,
                    key="select_produto_oportunidade1",
                    placeholder='Selecione aqui...'
                )
            with col2:
                produtos_selecionado2 = st.multiselect(
                    "Produto 2:",
                    options=nomes_produtos,
                    default=default2,
                    key="select_produto_oportunidade2",
                    placeholder='Selecione aqui...'
                )
            with col3:
                produtos_selecionado3 = st.multiselect(
                    "Produto 3:",
                    options=nomes_produtos,
                    default=default3,
                    key="select_produto_oportunidade3",
                    placeholder='Selecione aqui...'
                )
            with col4:
                produtos_selecionado4 = st.multiselect(
                    "Produto 4:",
                    options=nomes_produtos,
                    default=default4,
                    key="select_produto_oportunidade4",
                    placeholder='Selecione aqui...'
                )
            with col5:
                produtos_selecionado5 = st.multiselect(
                    "Produto 5:",
                    options=nomes_produtos,
                    default=default5,
                    key="select_produto_oportunidade5",
                    placeholder='Selecione aqui...'
                )
            
            col6, col7, col8, col9, col10 = st.columns(5)
            with col6:
                produtos_selecionado6 = st.multiselect(
                    "Produto 6:",
                    options=nomes_produtos,
                    default=default6,
                    key="select_produto_oportunidade6",
                    placeholder='Selecione aqui...'
                )
            with col7:
                produtos_selecionado7 = st.multiselect(
                    "Produto 7:",
                    options=nomes_produtos,
                    default=default7,
                    key="select_produto_oportunidade7",
                    placeholder='Selecione aqui...'
                )
            with col8:
                produtos_selecionado8 = st.multiselect(
                    "Produto 8:",
                    options=nomes_produtos,
                    default=default8,
                    key="select_produto_oportunidade8",
                    placeholder='Selecione aqui...'
                )
            with col9:
                produtos_selecionado9 = st.multiselect(
                    "Produto 9:",
                    options=nomes_produtos,
                    default=default9,
                    key="select_produto_oportunidade9",
                    placeholder='Selecione aqui...'
                )
            with col10:
                produtos_selecionado10 = st.multiselect(
                    "Produto 10:",
                    options=nomes_produtos,
                    default=default10,
                    key="select_produto_oportunidade10",
                    placeholder='Selecione aqui...'
                )

            produtos_selecionados = [p[0] for p in [produtos_selecionado1, produtos_selecionado2, produtos_selecionado3, produtos_selecionado4, produtos_selecionado5,
                                        produtos_selecionado6, produtos_selecionado7, produtos_selecionado8, produtos_selecionado9, produtos_selecionado10] if p]
            
            negocio_selecionado['produtos'] = produtos_selecionados

            if len(produtos_selecionados) > 0:
                #st.write(negocio_selecionado)
                produtos_dict = {p["nome"]: p for p in produtos}

                # Itera sobre a lista de produtos selecionados, adicionando o objeto correspondente para cada ocorrência
                produtos_selecionados_obj = [
                    produtos_dict[nome] for nome in negocio_selecionado['produtos'] if nome in produtos_dict
                ]
                total = sum(float(p["preco"]) for p in produtos_selecionados_obj)
                preco_produtos = [p["preco"] for p in produtos_selecionados_obj]
                
                valor_estimado_formatado = format_currency(total)
                desconto = st.number_input("Desconto (%)",0.0, 100.0)
                desconto_total = total*(desconto/100)
                valor_negocio = total - desconto_total
                valor_negocio_formatado = format_currency(valor_negocio)
                col1, col2 = st.columns(2)
                with col1:  st.warning(f"**Preço total dos produtos selecionados:** {valor_estimado_formatado}")
                with col2:  st.warning(f"**Preço total com descontos:** {valor_negocio_formatado}")
                #**Preço com o desconto aplicado:** {valor_negocio_formatado}")
                condicoes = calcular_parcelas_e_saldo(float(valor_negocio), 6000)
                
                # Valor salvo no banco para a condição de pagamento (se existir)
                default_condicao = negocio_selecionado.get('condicoes_pagamento', None)

                # Se existir e estiver na lista de opções, encontra o índice correspondente;
                # caso contrário, usa o índice 0 (primeira opção da lista)
                if default_condicao and default_condicao in condicoes:
                    default_index = condicoes.index(default_condicao)
                else:
                    default_index = 0

                condicao_pagamento = st.selectbox('Condições de pagamento:', condicoes, index=default_index)

                if float(valor_negocio) > 35000:
                    prazos = ['60 dias úteis após o recebimento da documentação completa.',
                            '30 dias úteis após o recebimento da documentação completa.',
                            '20 dias úteis após o recebimento da documentação completa.']
                
                else: prazos = ['60 dias úteis após o recebimento da documentação completa.',
                            '30 dias úteis após o recebimento da documentação completa.',
                            '20 dias úteis após o recebimento da documentação completa.',
                            '15 dias úteis após o recebimento da documentação completa.',
                            '10 dias úteis após o recebimento da documentação completa.']

                # 1. Prazo de execução
                default_prazo = negocio_selecionado.get('prazo_execucao', None)
                if default_prazo and default_prazo in prazos:
                    prazo_index = prazos.index(default_prazo)
                else:
                    prazo_index = 0
                prazo = st.selectbox("Prazo de execução:", prazos, index=prazo_index)

                # 2. Seleção dos Contatos da Empresa (pode ser múltiplo)
                contatos = list(
                    collection_contatos.find(
                        {"empresa": empresa_nome},
                        {"_id": 0, "nome": 1, "email": 1, "sobrenome": 1}  # Incluindo sobrenome para contato principal
                    )
                )
                if contatos:
                    opcoes_contatos = [f"{c.get('email', 'Sem email')}" for c in contatos]
                    nomes_contatos = [f"{c.get('nome', 'Sem nome')} {c.get('sobrenome', '')}" for c in contatos]

                    # Valor padrão para contatos selecionados (campo 'contatos_selecionados' da oportunidade)
                    default_contatos = negocio_selecionado.get("contatos_selecionados", [])
                    # Filtra os defaults para que estejam entre as opções disponíveis
                    default_contatos = [d for d in default_contatos if d in opcoes_contatos]

                    selected_contatos = st.multiselect(
                        "Selecione os contatos da empresa que receberão o orçamento:",
                        opcoes_contatos,
                        key="orcamento_contatos",
                        placeholder='Selecione os contatos aqui...',
                        default=default_contatos
                    )

                    # Valor padrão para o contato principal (campo 'contato_principal' da oportunidade)
                    default_contato_principal = negocio_selecionado.get("contato_principal", None)
                    if default_contato_principal and default_contato_principal in nomes_contatos:
                        contato_index = nomes_contatos.index(default_contato_principal)
                    else:
                        contato_index = 0
                    nome_contato_principal = st.selectbox(
                        "Selecione o contato principal (A/C):",
                        nomes_contatos,
                        key="orcamento_contato_principal",
                        index=contato_index
                    )
                else:
                    st.error("Nenhum contato encontrado para essa empresa.")
                    selected_contatos = []

                st.write('-----')
                
                st.subheader("📄 Geração de um orçamento convencional")
                if st.button("Gerar o orçamento"):
                    if desconto <= negocio_selecionado['desconto_aprovado']:  
                        inicio = time.time()
                        pdf_out_path = gro.generate_proposal_pdf2(selected_empresa, negocio_id, selected_negocio, produtos_selecionados_obj, preco_produtos, valor_negocio, desconto_total, condicao_pagamento, prazo, nome_contato_principal)
                        if pdf_out_path:
                            versao_proposta = gro.upload_onedrive2(pdf_out_path)
                            #st.write(versao_proposta)
                            path_proposta_envio = pdf_out_path.replace('.pdf',f'_v0{versao_proposta}.pdf')
                            fim = time.time()
                            st.info(f"Tempo da operação: {round(fim-inicio,2)}s")
                            novo_nome_arquivo = os.path.basename(path_proposta_envio)

                            # Atualiza o documento da oportunidade com as novas informações
                            collection_oportunidades.update_one(
                                {"cliente": empresa_nome, "nome_oportunidade": selected_negocio},
                                {"$set": {
                                    "produtos": produtos_selecionados,
                                    "valor_orcamento": valor_negocio_formatado,
                                    "condicoes_pagamento": condicao_pagamento,
                                    "prazo_execucao": prazo,
                                    "contato_principal": nome_contato_principal,
                                    "contatos_selecionados": selected_contatos
                                }}
                            )
                        else: st.error('Erro na geração do orçamento, fale com o seu gestor.')
                      
                    else:
                        st.error('⚠️ Desconto ainda não aprovado pelo gestor. Solicite abaixo aprovação do desconto ou aguarde a decisão antes de gerar a proposta.')
                
                st.write('-----')
                st.subheader("📝 Geração de um orçamento com aprovação de desconto adicional")
                with st.expander('Solicitação de desconto adicional ao gestor', expanded=False):
                    st.error('⚠️ Descontos acima de 20% devem ser aprovados pelo gestor responsável.') 
                    
                    if negocio_selecionado['aprovacao_gestor']: 
                        st.markdown(f'🟩 Desconto aprovado pelo gestor de até {negocio_selecionado['desconto_aprovado']}%.')
                        justificativa = st.text_area("Justificativa para solicitação de novo desconto adicional:")
                        if st.button(f'Solicitar novo desconto de {desconto}%'):
                            #receivers = ['rodrigo@hygge.eco.br','alexandre@hygge.eco.br','rodrigo@hygge.eco.br','paula@hygge.eco.br',selected_email]
                            receivers = ['rodrigo@hygge.eco.br']
                            
                            message = MIMEMultipart()
                            message["From"] = email
                            message["To"] = ", ".join(receivers)
                            message["Subject"] = f'Solicitação de desconto adicional - {selected_negocio}'
                            
                            body = f"""<p>Vendedor: {negocio_selecionado['proprietario']}</p>
                                        <p>Empresa: {negocio_selecionado['cliente']}</p>
                                        <p>Projeto: {negocio_selecionado['nome_oportunidade']}</p>
                                        <p>Produto(s): {produtos_selecionados}</p>
                                        <p>Desconto solicitado: {desconto}%</p>
                                        <p>Valor do orçamento inicial: {valor_estimado_formatado}</p>
                                        <p>Novo valor do orçamento: {valor_negocio_formatado}</p>
                                        <p>Justificativa: {justificativa}</p>
                                        <p>Acesse a plataforma integrada para aprovar ou reprovar a solicitação.</p>"""

                            # Concatena o corpo do email com a assinatura HTML
                            full_body = body

                            # Anexa o corpo do email completo no formato HTML
                            message.attach(MIMEText(full_body, "html"))

                            # Sending the email
                            try:
                                server = smtplib.SMTP('smtp.office365.com', 587)
                                server.starttls()
                                server.login(email, senha)
                                server.sendmail(email, receivers, message.as_string())
                                server.quit()
                            except Exception as e:
                                st.error(f"Falha no envio do email: {e}")

                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"desconto_solicitado": float(desconto)}})    
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"solicitacao_desconto": True}})    
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"aprovacao_gestor": False}})
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"condicoes_pagamento": condicao_pagamento}})
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"prazo_execucao": prazo}})
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"contato_principal": nome_contato_principal}})
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"contatos_selecionados": selected_contatos}})
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"produtos": produtos_selecionados}})
                            st.success('Solicitação de desconto enviada com sucesso.')
                            st.rerun()

                    elif negocio_selecionado['solicitacao_desconto']: 
                        st.markdown(f"🟨 Em análise pelo gestor a solicitação de um desconto de {negocio_selecionado['desconto_solicitado']}%.")
                    
                    elif not negocio_selecionado['solicitacao_desconto']:
                        st.markdown('🟦 Sem solicitação de desconto.')
                        justificativa = st.text_area("Justificativa para solicitação de desconto adicional:")
                        if st.button(f'Solicitar desconto de {desconto}%'):
                        
                            #receivers = ['rodrigo@hygge.eco.br','alexandre@hygge.eco.br','rodrigo@hygge.eco.br','paula@hygge.eco.br',selected_email]
                            receivers = ['rodrigo@hygge.eco.br']
                            
                            message = MIMEMultipart()
                            message["From"] = email
                            message["To"] = ", ".join(receivers)
                            message["Subject"] = f'Solicitação de desconto adicional - {selected_negocio}'
                            
                            body = f"""<p>Vendedor: {negocio_selecionado['proprietario']}</p>
                                        <p>Empresa: {negocio_selecionado['cliente']}</p>
                                        <p>Projeto: {negocio_selecionado['nome_oportunidade']}</p>
                                        <p>Produto(s): {produtos_selecionados}</p>
                                        <p>Desconto solicitado: {desconto}%</p>
                                        <p>Valor do orçamento inicial: {valor_estimado_formatado}</p>
                                        <p>Novo valor do orçamento: {valor_negocio_formatado}</p>
                                        <p>Justificativa: {justificativa}</p>
                                        <p>Acesse a plataforma integrada para aprovar ou reprovar a solicitação.</p>"""

                            # Concatena o corpo do email com a assinatura HTML
                            full_body = body

                            # Anexa o corpo do email completo no formato HTML
                            message.attach(MIMEText(full_body, "html"))

                            # Sending the email
                            try:
                                server = smtplib.SMTP('smtp.office365.com', 587)
                                server.starttls()
                                server.login(email, senha)
                                server.sendmail(email, receivers, message.as_string())
                                server.quit()
                            except Exception as e:
                                st.error(f"Falha no envio do email: {e}")
                            
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"desconto_solicitado": float(desconto)}})    
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"solicitacao_desconto": True}})    
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"aprovacao_gestor": False}})
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"condicoes_pagamento": condicao_pagamento}})
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"prazo_execucao": prazo}})
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"contato_principal": nome_contato_principal}})
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"contatos_selecionados": selected_contatos}})
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"produtos": produtos_selecionados}})
                            st.success('Solicitação de desconto enviada com sucesso.')
                            st.rerun()

                    elif not negocio_selecionado['aprovacao_gestor']: 
                        st.markdown('🟥 Desconto não aprovado.')
                
                if st.button("Gerar o orçamento com o desconto adicional aprovado"):
                    if desconto <= negocio_selecionado['desconto_aprovado']:  
                        inicio = time.time()
                        pdf_out_path = gro.generate_proposal_pdf2(selected_empresa, negocio_id, selected_negocio, produtos_selecionados_obj, preco_produtos, valor_negocio, desconto_total, condicao_pagamento, prazo, nome_contato_principal)
                        if pdf_out_path:
                            versao_proposta = gro.upload_onedrive2(pdf_out_path)
                            #   versao_proposta)
                            path_proposta_envio = pdf_out_path.replace('.pdf',f'_v0{versao_proposta}.pdf')
                            fim = time.time()
                            st.info(f"Tempo da operação: {round(fim-inicio,2)}s")
                            novo_nome_arquivo = os.path.basename(path_proposta_envio)

                            # Atualiza o documento da oportunidade com as novas informações
                            collection_oportunidades.update_one(
                                {"cliente": empresa_nome, "nome_oportunidade": selected_negocio},
                                {"$set": {
                                    "produtos": produtos_selecionados,
                                    "valor_orcamento": valor_negocio_formatado,
                                    "condicoes_pagamento": condicao_pagamento,
                                    "prazo_execucao": prazo,
                                    "contato_principal": nome_contato_principal,
                                    "contatos_selecionados": selected_contatos
                                }}
                            )
                        else: st.error('Erro na geração do orçamento.')
                    
                    else:
                        st.error('⚠️ Desconto ainda não aprovado pelo gestor. Solicite abaixo aprovação do desconto ou aguarde a decisão antes de gerar a proposta.')
                
                st.write('-----')
                
                st.subheader("📨 Envio da proposta para o cliente")

                if st.button('Enviar orçamento para o cliente'):
                    #receivers = selected_contatos + [email,'fabricio@hygge.eco.br','alexandre@hygge.eco.br','rodrigo@hygge.eco.br','paula@hygge.eco.br']
                    receivers = selected_contatos + ['rodrigo@hygge.eco.br']
                    
                    message = MIMEMultipart()
                    message["From"] = email
                    message["To"] = ", ".join(receivers)
                    message["Subject"] = f'Proposta Técnico-Comercial Hygge - {selected_negocio}'

                    # Corpo do email original
                    body = f"""<p>Olá {nome_contato_principal},</p>
                    <p>Conforme solicitado, segue em anexo a proposta técnico comercial da Hygge para o empreendimento {selected_negocio}.</p>
                    <p>Estamos à disposição para quaisquer dúvidas ou esclarecimentos.</p>
                    <p>Atenciosamente,</p>"""
                    
                    if email == 'comercial2@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/thiago-lecheta.html"
                    elif email == 'matheus@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/matheus-duarte.html"
                    elif email == 'fabricio@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/fabricio-lucchesi.html"
                    elif email == 'alexandre@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/alexandre-castagini.html"
                    #elif email == 'comercial6@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/maria-eduarda-ferreira.html"  
                    elif email == 'comercial5@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/matheus-rodrigues.html"  
                    elif email == 'comercial4@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/alceu-junior.html"   
                    elif email == 'comercial3@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/victor-oliveira.html"
                    #elif email == 'comercial1@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/fernando-tohme.html"
                    elif email == 'rodrigo@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/rodrigo-leitzke.html"
                    elif email == 'admin@hygge.eco.br': url = "https://www.hygge.eco.br/assinatura-email/2024/rodrigo-leitzke.html"

                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                    response = requests.get(url, headers=headers)
                    html_signature = response.text

                    # Concatena o corpo do email com a assinatura HTML
                    full_body = body + html_signature

                    # Anexa o corpo do email completo no formato HTML
                    message.attach(MIMEText(full_body, "html"))

                    path_proposta_envio = gro.get_versao(f"{selected_negocio}_{negocio_id}")
                    if path_proposta_envio:
                        novo_nome_arquivo = os.path.basename(path_proposta_envio)
                        
                        # Attach the PDF file
                        with open(path_proposta_envio, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header('Content-Disposition', 'attachment', filename=novo_nome_arquivo)
                            message.attach(part)

                        # Sending the email
                        try:
                            server = smtplib.SMTP('smtp.office365.com', 587)
                            server.starttls()
                            server.login(email, senha)
                            server.sendmail(email, receivers, message.as_string())
                            server.quit()
                            st.success(f'Etapa 1 de 1 - Email enviado com sucesso com a proposta {novo_nome_arquivo}!')
                        except Exception as e:
                            st.error(f"Falha no envio do email: {e}")
                    
                    else: st.error("Arquivo não localizado na pasta '11. Orçamentos', gere um orçamento para enviá-lo ao cliente.")

                st.write('-----')
                
                


