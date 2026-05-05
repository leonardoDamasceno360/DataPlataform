"""                                READ ME
 Este código faz o tratamento da base de Colaboradores Demitidos Geral,
 remove as seguintes colunas:
 B - K, M, P - Q, U - Z
"""
import pandas as pd
import numpy as np

def Executar():
    WsOrigem = pd.read_excel("C:/Users/2977429/OneDrive - TCS COM PROD/Desktop/Automações/Bases modelo/Bases/OT Balance.xlsx")

    colunas_remover = (
    list(WsOrigem.columns[1:11]) +      
    [WsOrigem.columns[12]] +            
    list(WsOrigem.columns[15:17]) +     
    list(WsOrigem.columns[20:26])       
    )

    WsUpdate = WsOrigem.drop(colunas_remover, axis=1)


    WsUpdate["Compliance as per MN1"] = np.where((WsUpdate["Type of Day"] == "Regular Day") & (WsUpdate["Total OT Hours Done"] >= 4.0), "Non-Compliant", "Compliant")

    WsUpdate["Request Status"] = np.where(WsUpdate["Last OT Request Status"] ==  "Non Requested", "Not requested", "Requested")

    WsUpdate["Last OT Request Status"] = WsUpdate["Last OT Request Status"].replace({"Aprovado" : "Approved",
                                                                                 "Reprovado" : "Rejected",
                                                                                 "Em Andamento" : "In progress"})

    WsUpdate.loc[WsUpdate["Total OT Hours Done"]  <= 0.5, "OT Classification"] = "up to 30min"
    WsUpdate.loc[(WsUpdate["Total OT Hours Done"] > 0.5) & (WsUpdate["Total OT Hours Done"] < 2.0)  , "OT Classification"] = "30 min to 2 hours"

    WsUpdate['OT Hours Compliance Classification'] = WsUpdate['OT Hours Compliance Classification'].replace({
                                                     'Compliance' : 'Compliant',
                                                     'Non compliance' : 'Non-compliant'})

    WsUpdate['OT Classification'] = WsUpdate['OT Classification'].replace({
                                                     'De 2 até 4 Hrs' : '2 hours to 4 hours',
                                                     'Mais de 4 Hrs' : 'over 4 hours'})

    WsUpdate.to_excel(
    "C:/Users/2977429/OneDrive - TCS COM PROD/Desktop/Automações/Bases modelo/Bases/Bases_Tratadas/OT_Balance_Tratado.xlsx",
    index=False
)
    print("OT concluído")