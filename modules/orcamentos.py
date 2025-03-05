import streamlit as st
from utils.database import get_collection
from datetime import datetime
import pandas as pd
import datetime as dt
import calendar


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
            {"_id": 0, "nome_oportunidade": 1,'produtos': 1, "valor_estimado": 1, "data_criacao": 1, "data_fechamento": 1, "estagio": 1}
        )
    )
    if not oportunidades:
        st.warning("Nenhum negócio encontrado para essa empresa.")
    else:
        opcoes_negocios = [opp["nome_oportunidade"] for opp in oportunidades]
        selected_negocio = st.selectbox("**Selecione o Negócio:**", opcoes_negocios, key="orcamento_negocio")

        # Buscar os dados    do negócio selecionado
        negocio_selecionado = next((opp for opp in oportunidades if opp["nome_oportunidade"] == selected_negocio), None)
        if negocio_selecionado:
            produtos = list(collection_produtos.find({}, {"_id": 0, "nome": 1, "categoria": 1, "preco": 1, "base_desconto": 1}))

            produtos_selecionados_obj = [p for p in produtos if f"{p['nome']}" in negocio_selecionado['produtos']]
            total = sum(float(p["preco"]) for p in produtos_selecionados_obj)
            valor_estimado_formatado = format_currency(total)
            st.subheader("Informações do Negócio para orçamento")
            st.multiselect("**Produtos:**", negocio_selecionado['produtos'], default=negocio_selecionado['produtos'], disabled=True)
            valor_negocio_formatado = st.text_input("**Valor do negócio:**", valor_estimado_formatado)
            valor_negocio = valor_negocio_formatado.replace("R$ ", "").replace(".", "").replace(",", ".")

            condicoes = calcular_parcelas_e_saldo(float(valor_negocio), 6000)
            
            condicao_pagamento = st.selectbox('**Condições de pagamento:**',condicoes)

            if float(valor_negocio) > 35000:
                  prazos = ['60 dias úteis após o recebimento da documentação completa.',
                        '30 dias úteis após o recebimento da documentação completa.',
                        '20 dias úteis após o recebimento da documentação completa.']
            
            else: prazos = ['60 dias úteis após o recebimento da documentação completa.',
                        '30 dias úteis após o recebimento da documentação completa.',
                        '20 dias úteis após o recebimento da documentação completa.',
                        '15 dias úteis após o recebimento da documentação completa.',
                        '10 dias úteis após o recebimento da documentação completa.']


            # 3. Seleção dos Contatos da Empresa (pode ser múltiplo)
            contatos = list(
                collection_contatos.find(
                    {"empresa": empresa_nome},
                    {"_id": 0, "nome": 1, "email": 1}
                )
            )
            if contatos:
                opcoes_contatos = [f"{c.get('email', 'Sem email')}" for c in contatos]
                selected_contatos = st.multiselect("**Selecione os contatos da empresa que receberão o orçamento:**", opcoes_contatos, key="orcamento_contatos")
            else:
                st.error("Nenhum contato encontrado para essa empresa.")
                selected_contatos = []

    # Exemplo: ação para gerar o orçamento
    if st.button("Gerar Orçamento"):
        # Aqui você pode implementar a lógica para salvar o orçamento ou processá-lo conforme necessário
        st.success("Orçamento gerado com sucesso!")





