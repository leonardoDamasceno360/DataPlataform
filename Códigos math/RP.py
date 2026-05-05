"""                             READ ME
    Este código fará a tratativa da base de Lista de interjornada(RP)
    Ele removerá as seguinte colunas:
    B - J, L, N

    Trocar o tipo de data de:
    Data/Hora -> Data

    Arredondar as casas decimais das hora da interjornada para 2
"""
import pandas as pd

def Executar():
    # Caminho do arquivo xlsx a ser tratado
    WsOrigem = pd.read_excel("C:/Users/2977429/OneDrive - TCS COM PROD/Desktop/Automações/Bases modelo/Bases/Lista InterJornada.xlsx")

    # lista das colunas que serão removidas
    colunas_remover = list(WsOrigem.columns[1:10]) + [WsOrigem.columns[11]] + [WsOrigem.columns[13]]

    # Trocar o tipo de dados de data/hora para apenas data
    WsOrigem['Data do Dia (Data/Hora)'] = pd.to_datetime(WsOrigem['Data do Dia (Data/Hora)'], dayfirst= True)
    WsOrigem['Data do Dia (Data/Hora)'] = WsOrigem['Data do Dia (Data/Hora)'].dt.date

    # Arredondar o Interjornada Praticada para 2 casas decimais
    WsOrigem['Interjornada Praticada'] = pd.to_numeric(WsOrigem['Interjornada Praticada'])
    WsOrigem['Interjornada Praticada'] = WsOrigem['Interjornada Praticada'].round(2)

    # remove as coluanas da lista
    WsUpdate = WsOrigem.drop(colunas_remover, axis=1)

    # Salva o novo arquivo tratado
    WsUpdate.to_excel("C:/Users/2977429/OneDrive - TCS COM PROD/Desktop/Automações/Bases modelo/Bases/Bases_Tratadas/Lista InterJornada_Tratada.xlsx", index=False) 
    print("RP concluído")