"""                 READ ME
    Este código fará o tratamento da base de separation forms
    removendo as colunas:

    A - B, D - E, G, J - M
    
    Tratativa dos dados da coluna de Separation Type:
    Termination e Death -> Involuntary
    Retirement e Resignation -> Voluntary
"""
import pandas as pd

def Executar():
    # Caminho do arquivo xlsx a ser tratado
    WsOrigem = pd.read_excel("C:/Users/2977429/OneDrive - TCS COM PROD/Desktop/Automações/Bases modelo/Bases/Separation Forms.xlsx")

        # lista das colunas que serão removidas
    colunas_remover = list(WsOrigem.columns[0:2]) + list(WsOrigem.columns[3:5]) + [WsOrigem.columns[6]] + list(WsOrigem.columns[8:15])
    # remover as colunas
    WsUpdate = WsOrigem.drop(colunas_remover,axis=1)

    """
        Tratativa dos dados da coluna de Separation Type,
        Termination e Death -> Involuntary
        Retirement e Resignation -> Voluntary
    """
    WsUpdate['\nSeparation type '] = WsOrigem['\nSeparation type '].replace({"Termination":"Involuntary",
                                                                        "Death":"Involuntary", 
                                                                        "Retirement":"Voluntary",
                                                                        "Resignation":"Voluntary"})

    # Salvar o arquivo tratado
    WsUpdate.to_excel('C:/Users/2977429/OneDrive - TCS COM PROD/Desktop/Automações/Bases modelo/Bases/Bases_Tratadas/Separation Forms_Tratado.xlsx', index=False)
    print("Separation forms concluído")