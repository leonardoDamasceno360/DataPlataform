"""                                READ ME
 Este código faz o tratamento da base de Assinutara de Documentos,
 remove as seguintes colunas:
 B - J, M - O
"""
import pandas as pd

def Executar():
# Caminho do arquivo xlsx a ser tratado
    WsOrigem = pd.read_excel("C:/Users/2977429/OneDrive - TCS COM PROD/Desktop/Automações/Bases modelo/Bases/Assinatura de Documentos.xlsx")

# lista das colunas que serão removidas
    colunas_remover = list(WsOrigem.columns[1:10]) + list(WsOrigem.columns[12:15])
    WsUpdate = WsOrigem.drop(colunas_remover, axis=1)

# filtro para remover as já assinadas
    filtro = WsUpdate['Status da Assinatura Digital do Documento'] = "Pendente"
    WsUpdate["Status da Assinatura Digital do Documento"] = filtro

# salva o arquivo
    WsUpdate.to_excel("C:/Users/2977429/OneDrive - TCS COM PROD/Desktop/Automações/Bases modelo/Bases/Bases_Tratadas/Assinatura de Documentos_Tratado.xlsx",index=False)
    print("Documentos concluído")