import streamlit as st
import pandas as pd
import plotly.express as px
from gerenciamento_reservas import GerenciamentoReservas
from datetime import date, timedelta

def dashboard():
    st.title("Gerenciamento de Reservas")

    # Inicializa a classe de gerenciamento com múltiplas planilhas
    reservas = GerenciamentoReservas("reservas.xlsx", "parceiros.xlsx", "proprietarios.xlsx")
    
    # Botão para recarregar os dados da planilha
    if st.button("Recarregar Dados", key="botao_recarregar_dados"):
        reservas.df_reservas = reservas.load_data(reservas.reservas_path)
        reservas.df_parceiros = reservas.load_data(reservas.parceiros_path)
        reservas.df_proprietarios = reservas.load_data(reservas.proprietarios_path)
        st.success("Dados recarregados com sucesso!")

    # Relatório semanal
    exibir_relatorio_semanal(reservas)

    # Relatório de parceiros
    exibir_relatorio_parceiros(reservas)

    # Detalhamento semanal
    exibir_detalhamento_reservas(reservas)

    # Filtros interativos
    exibir_filtros(reservas)

    # Exportação de dados
    exportar_dados(reservas)

    # Edição de reservas
    editar_reservas(reservas)

    # Edição de parceiros e proprietários
    editar_parceiros(reservas)
    editar_proprietarios(reservas)

    # Adicionar nova reserva, parceiro, e proprietário
    adicionar_nova_reserva(reservas)
    adicionar_novo_parceiro(reservas)
    adicionar_novo_proprietario(reservas)

# Definição das funções necessárias

def exibir_relatorio_semanal(reservas):
    st.subheader("Relatório Semanal")
    reservas.calcular_saldos()
    df_semanal, total_hospedagem, total_a_pagar, total_a_receber_parceiros, apartamentos_ocupados = reservas.calcular_totais_semanal()
    
    st.write("**Valor total da hospedagem:**", total_hospedagem)
    st.write("**Total a pagar ao proprietário:**", total_a_pagar)
    st.write("**Total a receber dos parceiros:**", total_a_receber_parceiros)
    st.write("**Número de apartamentos ocupados na semana:**", apartamentos_ocupados)

    grafico_df = pd.DataFrame({
        'Descrição': ['Total Hospedagem', 'Total a Pagar', 'Total a Receber'],
        'Valores': [total_hospedagem, total_a_pagar, total_a_receber_parceiros]
    })
    fig = px.bar(grafico_df, x='Descrição', y='Valores', title="Totais Semanais")
    st.plotly_chart(fig)

def exibir_relatorio_parceiros(reservas):
    st.subheader("Relatório de Parceiros")
    df_parceiros, total_a_receber, total_a_pagar = reservas.gerar_relatorio_parceiros()

    st.write("**Total a receber dos parceiros:**", total_a_receber)
    st.write("**Total a pagar aos parceiros:**", total_a_pagar)
    st.write("**Resumo por Parceiro:**")
    st.dataframe(df_parceiros)

    fig = px.bar(df_parceiros, x='Parceiro', y=['A receber', 'A pagar'], title="Valores a Receber e Pagar por Parceiro")
    st.plotly_chart(fig)

def exibir_detalhamento_reservas(reservas):
    st.subheader("Detalhes das Reservas Semanais")
    df_semanal, *_ = reservas.calcular_totais_semanal()
    st.dataframe(df_semanal[['Nome do hóspede', 'Data de entrada', 'Data de saída', 
                             'Número do apartamento', 'Valor da hospedagem',
                             'Nome do Condomínio', 'Bloco', 'Endereço']])

def exibir_filtros(reservas):
    st.sidebar.header("Filtros de Reservas")
    nome_hospede = st.sidebar.text_input("Nome do Hóspede", key="filtro_nome_hospede")
    numero_apartamento = st.sidebar.number_input("Número do Apartamento", min_value=0, step=1, key="filtro_numero_apartamento")
    data_inicial = st.sidebar.date_input("Data de Entrada (inicial)", date.today() - timedelta(days=30), key="filtro_data_inicial")
    data_final = st.sidebar.date_input("Data de Entrada (final)", date.today(), key="filtro_data_final")

    df_filtrado = reservas.df_reservas.copy()
    if nome_hospede:
        df_filtrado = df_filtrado[df_filtrado['Nome do hóspede'].str.contains(nome_hospede, case=False)]
    if numero_apartamento > 0:
        df_filtrado = df_filtrado[df_filtrado['Número do apartamento'] == numero_apartamento]
    df_filtrado = df_filtrado[(df_filtrado['Data de entrada'] >= pd.Timestamp(data_inicial)) & 
                              (df_filtrado['Data de entrada'] <= pd.Timestamp(data_final))]

    st.subheader("Reservas Filtradas")
    st.dataframe(df_filtrado[['Nome do hóspede', 'Data de entrada', 'Data de saída', 
                              'Número do apartamento', 'Valor da hospedagem',
                              'Nome do Condomínio', 'Bloco', 'Endereço']])

def exportar_dados(reservas):
    if st.button("Exportar Relatório Semanal para CSV", key="exportar_relatorio_semanal"):
        reservas.exportar_csv(reservas.df_reservas, "relatorio_semanal.csv")
        st.success("Relatório semanal exportado como relatorio_semanal.csv")

    if st.button("Exportar Reservas Filtradas para CSV", key="exportar_reservas_filtradas"):
        reservas.exportar_csv(reservas.df_reservas, "reservas_filtradas.csv")
        st.success("Reservas filtradas exportadas como reservas_filtradas.csv")

def editar_reservas(reservas):
    st.subheader("Editar Reservas")
    id_reserva = st.selectbox("Selecione a Reserva para Editar", reservas.df_reservas.index, key="select_reserva_editar")
    reserva_selecionada = reservas.df_reservas.loc[id_reserva]

    nome = st.text_input("Nome do Hóspede", reserva_selecionada['Nome do hóspede'], key="editar_nome_hospede")
    data_entrada = st.date_input("Data de Entrada", reserva_selecionada['Data de entrada'], key="editar_data_entrada")
    data_saida = st.date_input("Data de Saída", reserva_selecionada['Data de saída'], key="editar_data_saida")
    numero_apartamento = st.number_input("Número do Apartamento", value=int(reserva_selecionada['Número do apartamento']), key="editar_numero_apartamento")
    valor_hospedagem = st.number_input("Valor da Hospedagem", value=float(reserva_selecionada['Valor da hospedagem']), key="editar_valor_hospedagem")
    condominio = st.text_input("Nome do Condomínio", reserva_selecionada.get('Nome do Condomínio', ''), key="editar_condominio")
    bloco = st.text_input("Bloco", reserva_selecionada.get('Bloco', ''), key="editar_bloco")
    endereco = st.text_input("Endereço", reserva_selecionada.get('Endereço', ''), key="editar_endereco")

    if st.button("Salvar Alterações", key="salvar_alteracoes_reserva"):
        reservas.atualizar_reserva(id_reserva, nome, data_entrada, data_saida, numero_apartamento, valor_hospedagem, condominio, bloco, endereco)
        st.success("Reserva atualizada com sucesso!")

# Funções para editar e adicionar parceiros e proprietários
def editar_parceiros(reservas):
    st.subheader("Editar Parceiros")
    id_parceiro = st.selectbox("Selecione o Parceiro para Editar", reservas.df_parceiros.index, key="select_parceiro_editar")
    parceiro_selecionado = reservas.df_parceiros.loc[id_parceiro]

    parceiro = st.text_input("Nome do Parceiro", parceiro_selecionado['Parceiro'], key="editar_nome_parceiro")
    a_receber = st.number_input("A Receber", value=float(parceiro_selecionado['A receber']), key="editar_a_receber")
    a_pagar = st.number_input("A Pagar", value=float(parceiro_selecionado['A pagar']), key="editar_a_pagar")

    if st.button("Salvar Alterações no Parceiro", key="salvar_alteracoes_parceiro"):
        reservas.atualizar_parceiro(id_parceiro, parceiro, a_receber, a_pagar)
        st.success("Parceiro atualizado com sucesso!")

def editar_proprietarios(reservas):
    st.subheader("Editar Proprietários")
    id_proprietario = st.selectbox("Selecione o Proprietário para Editar", reservas.df_proprietarios.index, key="select_proprietario_editar")
    proprietario_selecionado = reservas.df_proprietarios.loc[id_proprietario]

    nome = st.text_input("Nome Completo", proprietario_selecionado['Nome Completo'], key="editar_nome_proprietario")
    email = st.text_input("Email", proprietario_selecionado['Email'], key="editar_email_proprietario")
    telefone = st.text_input("Telefone", proprietario_selecionado['Telefone'], key="editar_telefone_proprietario")
    documento = st.text_input("Documento", proprietario_selecionado['Documento'], key="editar_documento_proprietario")

    if st.button("Salvar Alterações no Proprietário", key="salvar_alteracoes_proprietario"):
        reservas.atualizar_proprietario(id_proprietario, nome, email, telefone, documento)
        st.success("Proprietário atualizado com sucesso!")

def adicionar_novo_parceiro(reservas):
    st.subheader("Adicionar Novo Parceiro")
    parceiro = st.text_input("Nome do Parceiro", key="novo_nome_parceiro")
    a_receber = st.number_input("A Receber", min_value=0.0, step=0.01, key="novo_a_receber_parceiro")
    a_pagar = st.number_input("A Pagar", min_value=0.0, step=0.01, key="novo_a_pagar_parceiro")

    if st.button("Adicionar Parceiro", key="botao_adicionar_parceiro"):
        reservas.adicionar_parceiro(parceiro, a_receber, a_pagar)
        st.success("Novo parceiro adicionado com sucesso!")
        reservas.df_parceiros = reservas.load_data(reservas.parceiros_path)

def adicionar_novo_proprietario(reservas):
    st.subheader("Adicionar Novo Proprietário")
    nome = st.text_input("Nome Completo", key="novo_nome_proprietario")
    email = st.text_input("Email", key="novo_email_proprietario")
    telefone = st.text_input("Telefone", key="novo_telefone_proprietario")
    documento = st.text_input("Documento", key="novo_documento_proprietario")

    if st.button("Adicionar Proprietário", key="botao_adicionar_proprietario"):
        reservas.adicionar_proprietario(nome, email, telefone, documento)
        st.success("Novo proprietário adicionado com sucesso!")
        reservas.df_proprietarios = reservas.load_data(reservas.proprietarios_path)

def adicionar_nova_reserva(reservas):
    st.subheader("Adicionar Nova Reserva")
    
    nome = st.text_input("Nome do Hóspede", key="nome_hospede")
    data_entrada = st.date_input("Data de Entrada", date.today(), key="data_entrada")
    data_saida = st.date_input("Data de Saída", date.today() + timedelta(days=1), key="data_saida")
    numero_apartamento = st.number_input("Número do Apartamento", min_value=1, step=1, key="numero_apartamento")
    valor_hospedagem = st.number_input("Valor da Hospedagem", min_value=0.0, step=0.01, key="valor_hospedagem")
    condominio = st.text_input("Nome do Condomínio", key="condominio")
    bloco = st.text_input("Bloco", key="bloco")
    endereco = st.text_input("Endereço", key="endereco")

    if st.button("Adicionar Reserva", key="botao_adicionar_reserva"):
        reservas.adicionar_reserva(nome, data_entrada, data_saida, numero_apartamento, valor_hospedagem, condominio, bloco, endereco)
        st.success("Nova reserva adicionada com sucesso!")
        reservas.df_reservas = reservas.load_data(reservas.reservas_path)

if __name__ == "__main__":
    dashboard()
