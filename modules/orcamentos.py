import streamlit as st
from utils.database import get_collection
from datetime import datetime, timedelta
import pandas as pd
import datetime as dt
import calendar
import modules.gerar_orcamento as gro
import time
import os

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


def elaborar_orcamento(user):
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
    selected_empresa = st.selectbox("**Selecione a Empresa:**", opcoes_empresas, key="orcamento_empresa")
    # Extrair o nome da empresa (razao_social) a partir da string
    empresa_nome = selected_empresa

    # 2. Seleção do Negócio (Oportunidade) vinculado à empresa selecionada
    oportunidades = list(
        collection_oportunidades.find(
            {"cliente": empresa_nome},
            {"_id": 1, "nome_oportunidade": 1,'produtos': 1, "valor_estimado": 1, "data_criacao": 1, "data_fechamento": 1, "estagio": 1, 'aprovacao_gestor': 1, 'solicitacao_desconto': 1, 'desconto_aprovado': 1}
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
            st.subheader("Informações do Negócio para orçamento")
            
            st.text('Selecione o(s) produto(s) para o orçamento:')
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1: produtos_selecionado1 = st.multiselect("Produto 1:", options=nomes_produtos, key="select_produto_oportunidade1", placeholder='Selecione aqui...')
            with col2: produtos_selecionado2 = st.multiselect("Produto 2:", options=nomes_produtos, key="select_produto_oportunidade2", placeholder='Selecione aqui...')
            with col3: produtos_selecionado3 = st.multiselect("Produto 3:", options=nomes_produtos, key="select_produto_oportunidade3", placeholder='Selecione aqui...')
            with col4: produtos_selecionado4 = st.multiselect("Produto 4:", options=nomes_produtos, key="select_produto_oportunidade4", placeholder='Selecione aqui...')
            with col5: produtos_selecionado5 = st.multiselect("Produto 5:", options=nomes_produtos, key="select_produto_oportunidade5", placeholder='Selecione aqui...')

            col6, col7, col8, col9, col10 = st.columns(5)
            with col6: produtos_selecionado6 = st.multiselect("Produto 6:", options=nomes_produtos, key="select_produto_oportunidade6", placeholder='Selecione aqui...')
            with col7: produtos_selecionado7 = st.multiselect("Produto 7:", options=nomes_produtos, key="select_produto_oportunidade7", placeholder='Selecione aqui...')
            with col8: produtos_selecionado8 = st.multiselect("Produto 8:", options=nomes_produtos, key="select_produto_oportunidade8", placeholder='Selecione aqui...')
            with col9: produtos_selecionado9 = st.multiselect("Produto 9:", options=nomes_produtos, key="select_produto_oportunidade9", placeholder='Selecione aqui...')
            with col10: produtos_selecionado10 = st.multiselect("Produto 10:", options=nomes_produtos, key="select_produto_oportunidade10", placeholder='Selecione aqui...')

            produtos_selecionados = [p[0] for p in [produtos_selecionado1, produtos_selecionado2, produtos_selecionado3, produtos_selecionado4, produtos_selecionado5,
                                        produtos_selecionado6, produtos_selecionado7, produtos_selecionado8, produtos_selecionado9, produtos_selecionado10] if p]
            negocio_selecionado['produtos'] = produtos_selecionados

            if len(produtos_selecionados) > 0:
                #st.write(negocio_selecionado)
                produtos_selecionados_obj = [p for p in produtos if f"{p['nome']}" in negocio_selecionado['produtos']]
                total = sum(float(p["preco"]) for p in produtos_selecionados_obj)
                preco_produtos = [p["preco"] for p in produtos_selecionados_obj]
                #st.write(produtos_selecionados_obj, preco_produtos)
                valor_estimado_formatado = format_currency(total)
                desconto = st.number_input("Desconto (%)",0.0, 100.0)
        
                valor_negocio = total*(1-desconto/100)
                valor_negocio_formatado = format_currency(valor_negocio)
                col1, col2 = st.columns(2)
                with col1:  st.warning(f"**Preço total dos produtos selecionados:** {valor_estimado_formatado}")
                with col2:  st.warning(f"**Preço total com descontos:** {valor_negocio_formatado}")  
                #**Preço com o desconto aplicado:** {valor_negocio_formatado}")
                condicoes = calcular_parcelas_e_saldo(float(valor_negocio), 6000)
                
                condicao_pagamento = st.selectbox('Condições de pagamento:',condicoes)

                if float(valor_negocio) > 35000:
                    prazos = ['60 dias úteis após o recebimento da documentação completa.',
                            '30 dias úteis após o recebimento da documentação completa.',
                            '20 dias úteis após o recebimento da documentação completa.']
                
                else: prazos = ['60 dias úteis após o recebimento da documentação completa.',
                            '30 dias úteis após o recebimento da documentação completa.',
                            '20 dias úteis após o recebimento da documentação completa.',
                            '15 dias úteis após o recebimento da documentação completa.',
                            '10 dias úteis após o recebimento da documentação completa.']

                prazo = st.selectbox("Prazo de execução:", prazos)

                # 3. Seleção dos Contatos da Empresa (pode ser múltiplo)
                contatos = list(
                    collection_contatos.find(
                        {"empresa": empresa_nome},
                        {"_id": 0, "nome": 1, "email": 1}
                    )
                )
                if contatos:
                    opcoes_contatos = [f"{c.get('email', 'Sem email')}" for c in contatos]
                    nomes_contatos = [f"{c.get('nome', 'Sem nome')} {c.get('sobrenome', '')}" for c in contatos]
                    selected_contatos = st.multiselect("Selecione os contatos da empresa que receberão o orçamento:", opcoes_contatos, key="orcamento_contatos", placeholder='Selecione os contatos aqui...')
                    nome_contato_principal = st.selectbox("Selecione o contato principal (A/C):", nomes_contatos, key="orcamento_contato_principal")
                else:
                    st.error("Nenhum contato encontrado para essa empresa.")
                    selected_contatos = []
                    
                if st.button("Gerar o orçamento"):
                    if desconto <= negocio_selecionado['desconto_aprovado'] or negocio_selecionado['aprovacao_gestor']:  
                        inicio = time.time()
                        pdf_out_path = gro.generate_proposal_pdf2(selected_empresa, negocio_selecionado['_id'], selected_negocio, produtos_selecionados_obj, preco_produtos, valor_negocio, desconto, condicao_pagamento, prazo, nome_contato_principal)
                        versao_proposta = gro.upload_onedrive2(pdf_out_path)
                        #st.write(versao_proposta)
                        path_proposta_envio = pdf_out_path.replace('.pdf',f'_v0{versao_proposta}.pdf')
                        fim = time.time()
                        st.info(f"Tempo da operação: {round(fim-inicio,2)}s")
                        novo_nome_arquivo = os.path.basename(path_proposta_envio)
                        #st.error(f"**ALERTA:** Ao clicar no botão abaixo a proposta **'{novo_nome_arquivo}'** será para o(s) email(s) **{selected_contatos}**, você tem certeza?",icon='🚨')
                    else:
                        st.error('⚠️ Desconto ainda não aprovado pelo gestor. Solicite abaixo aprovação do desconto ou aguarde a decisão antes de gerar a proposta.')

                with st.expander('Solicitação de desconto adicional ao gestor', expanded=False):
                    st.error('⚠️ Descontos acima de 20% devem ser aprovados pelo gestor responsável.') 
                    
                    if negocio_selecionado['aprovacao_gestor']: 
                        st.markdown('🟩 Desconto aprovado.')

                    elif not negocio_selecionado['aprovacao_gestor']: 
                        st.markdown('🟥 Desconto não aprovado.')
                    
                    elif negocio_selecionado['solicitacao_desconto']: 
                        st.markdown('🟨 Em análise pelo gestor.')
                    else:
                        st.markdown('🟦 Sem solicitação de desconto.')
                        if st.button(f'Solicitar desconto de {desconto}%'):
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"desconto_aprovado": float(desconto)}})    
                            collection_oportunidades.update_one({"cliente": empresa_nome, "nome_oportunidade": selected_negocio}, {"$set": {"solicitacao_desconto": True}})
                            st.success('Solicitação de desconto enviada com sucesso.')



