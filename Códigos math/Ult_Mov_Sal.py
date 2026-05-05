"""                             READ ME
Este código fará o tratamento da base de Última movimentação salárial,
Remove as seguintes colunas:
B - F e H - J
"""
import pandas as pd

def Executar():
    # define a origem da base de dados
    WsOrigem = pd.read_excel("C:/Users/2977429/OneDrive - TCS COM PROD/Desktop/Automações/Bases modelo/Bases/Ultima Movimentação Salarial.xlsx")

    # Cria a lista com todas as colunas que serão removidas
    colunas_remover = list(WsOrigem.columns[1:5]) + list(WsOrigem.columns[6:11])
    # Remove as colunas
    WsUpdate = WsOrigem.drop(colunas_remover,axis=1)

    # Salva as alterações como um novo arquivo
    WsUpdate.to_excel('C:/Users/2977429/OneDrive - TCS COM PROD/Desktop/Automações/Bases modelo/Bases/Bases_Tratadas/Ultima_Mov_Sal_Tratado.xlsx', index=False)
    print("Última movimentção salarial concluído")