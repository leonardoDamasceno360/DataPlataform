"""                                READ ME
 Este código faz o tratamento da base de Colaboradores Demitidos Geral,
 remove as seguintes colunas:
 B - S e V
"""
import pandas as pd

def Executar():
# Origem da base não tratada
    WsOrigem = pd.read_excel("C:/Users/2977429/OneDrive - TCS COM PROD/Desktop/Automações/Bases modelo/Bases/Colaboradores Demitidos Geral.xlsx")

# Cria uma lista da colunas de B - S e a V
    colunas_remover = list(WsOrigem.columns[1:19]) + [WsOrigem.columns[21]]
# Remove as colunas indicadas na lista
    WsUpdate = WsOrigem.drop(colunas_remover, axis=1)

# Salva as alterações como um novo arquivo
    WsUpdate.to_excel('C:/Users/2977429/OneDrive - TCS COM PROD/Desktop/Automações/Bases modelo/Bases/Bases_Tratadas/Demitidos_Tratado.xlsx', index=False)
    print("Desligados Geral concluído")

