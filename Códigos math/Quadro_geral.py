"""                                READ ME
 Este código faz o tratamento da base de Quadro Geral,
 remove as seguintes colunas:
    C - X, AA - AF, AH - AI, AK - AP, AS - AW, AY - AZ, BE - BL, BN - BS, BX - BY

Tratativa da coluna de Segment Head
Tushar Parikh	BFSI
Sangram Sahoo	CBG
Bruno Folly CMI	CMI
Jorge Banharo	EnR
Ximena Jofre	HR
Bruno Folly LSHC	LSHC
Sol Besprosvan	MFG
Ashok Kumar	Nearshore
NA	Other
Cyril John K	Other
RMG	Other
Bruno Rocha	Other
Latesh Sewani	Other
Amol Wadikar	Other
Renzo Parodi	Other
V Sathya	Other
ESU	Other
Bruno Folly - ESU	Other
Dhanasekhar V	Other
Alma Leal	Other
Nenhum	Other
ILP	Other
Pace Port	Other
Sabyasachi Chandra	Utilities

Tratativa da coluna de Horizontal Line
Replace:
Business Process Services	BPS
Enterprise Solutions	ESU
NA	Other
Application Development & Maint.	Other
Asset Leverage Solutions	Other
Infrastructure Services	Other
IoT & Digital Engineering	Other
Global Consulting Practice	Other
Quality Engineering and Transformation	Other
Cognitive Business Operation	Other
Other	Other
Nenhum	Other
Data & Analytics	Other
Digital Interactive	Other
Analytics & Insights	Other
Amazon Web Services	Other
Cyber Security	Other
Google Business Unit	Other
Microsoft Business Unit	Other
Cloud Apps, Microservices & APIfication	Other
AI Transformation	Other

Tratativa da coluna de sindicato
Replace:
SINDPD/SP - SIND TRAB EMP PROC DADOS EST SP	SP
SINDPD/RJ - Sind Trab Emp e Serv Pub e Priv de Inf Internet e Sim RJ	RJ
Nenhum	Other
SINTINORP/Londrina-Sind Trab Empr Cursos Inf Con S I D P A Bco Dados M	Londrina
SINDPD/DF - Sind dos Trab em Empr e Órgãos Publ Proc Dados S I S do DF	Other
SINDADOS/MG - Sind dos Empreg Emp de Proc Dados, Serv de Info Simil MG	Other
SINDPD/MA - Sind dos Empregados Proc Dados no Est do Maranhão	Other
SINDPD/PA - Sind Trabalhadores e Trabalhadoras em Tecn Informação Pará	Other
SINDPD/ES - Sind Empreg Emp Proc Dados e Trab em Inform do Est ES	Other
SPPD/MS - Sind Profissionais de Proc de Dados e Tec Informação de MS	Other
SINDPD/PR - Sind dos Trab em Empr de Processamento do Estado do Paraná	Other
SINDPD/PE - Sind Trab em Proc de Dados, Informat Tecn da Inform do PE	Other
SINDPD/RS - Sind dos Trabalhadores em Processamento de Dados no Est RS	Other
SINDPD/JOINVILLE - Sind Empreg em Empr Proc Dados Inform Simil Joinv	Other
SITEPD - Sind dos Trab Empr Priv de Proc de Dados de Curitiba e Região	Other
SINDADOS/BA - Sind Trab Empr e Órgãos Publ Proc Dados S I TI Com BA	Other

Tratativa da coluna situação
Replace:
Demitido em Meses Anteriores	Separated
Em Atividade Normal	Active
Gozando Férias	Active
Auxílio-Doença	Afastado
Suspensão Contratual (Art. 476-A da CLT)	Afastado
Licença-Maternidade	Afastado
Afastado sem Remuneração	Afastado
Demitido no Mês	Separated
Afastado por Aposentadoria Invalidez	Afastado
Afastado Pré-Auxílio-Doença	Afastado
""" 
import pandas as pd
import numpy as np
import warnings


def Executar():
    # Caminho do arquivo xlsx a ser tratado
    WsOrigem = pd.read_excel("C:/Users/2977429/OneDrive - TCS COM PROD/Desktop/Automações/Bases modelo/Bases/Quadro Geral.xlsx")
    warnings.filterwarnings("ignore", category=UserWarning)
    # lista das colunas que serão removidas
    colunas_remover = list(WsOrigem.columns[2:24]) + list(WsOrigem.columns[26:32]) + list(WsOrigem.columns[33:35]) + list(WsOrigem.columns[36:42]) + list(WsOrigem.columns[44:49]) + list(WsOrigem.columns[36:42]) + list(WsOrigem.columns[50:52]) + list(WsOrigem.columns[56:64]) + list(WsOrigem.columns[65:71]) + list(WsOrigem.columns[75:77])
    # Remove as colunas da lista
    WsUpdate = WsOrigem.drop(colunas_remover, axis=1)

    """
    Tratativa da coluna de Segment Head
    Replace(foi dividido em duas partes para facilitar o entendimento, no caso os específicos e other):
    """
    WsUpdate['Segment HEAD'] = WsUpdate['Segment HEAD'].replace({'Tushar Parikh' : 'BFSI',
                                                                'Sangram Sahoo': 'CBG',
                                                                'Bruno Folly CMI' : 'CMI',
                                                                'Jorge Banharo' : 'EnR',
                                                                'Ximena Jofre' : 'HR',
                                                                'Bruno Folly LSHC' :  'LSHC',
                                                                'Sol Besprosvan' : 'MFG',
                                                                'Ashok Kumar' : 'Nearshore',
                                                                'Sabyasachi Chandra' : 'Utilities'})

    WsUpdate['Segment HEAD'] = WsUpdate['Segment HEAD'].replace({'NA': 'ESU',
                                                                'Cyril John K': 'ESU',
                                                                'RMG': 'ESU',
                                                                'Bruno Rocha': 'ESU',
                                                                'Latesh Sewani': 'ESU',
                                                                'Amol Wadikar': 'ESU',
                                                                'Renzo Parodi': 'ESU',
                                                                'V Sathya': 'ESU',
                                                                'ESU': 'ESU',
                                                                'Bruno Folly - ESU': 'ESU',
                                                                'Dhanasekhar V': 'ESU',
                                                                'Alma Leal': 'ESU',
                                                                'Nenhum': 'ESU',
                                                                'ILP': 'ESU',
                                                                'Pace Port': 'ESU',
                                                                np.nan : 'ESU'})

    """
    Tratativa da coluna de Horizontal Line
    """
    WsUpdate['Horizontal Line'] = WsUpdate['Horizontal Line'].replace({'Business Process Services' : 'BPS',
                                                                    'Enterprise Solutions' : 'ESU',
                                                                    'NA': 'Other',
                                                                    'Application Development & Maint.': 'Other',
                                                                    'Application Development &amp; Maint.': 'Other',
                                                                    'Asset Leverage Solutions': 'Other',
                                                                    'Infrastructure Services': 'Other',
                                                                    'IoT & Digital Engineering': 'Other',
                                                                    'IoT &amp; Digital Engineering': 'Other',
                                                                    'Global Consulting Practice': 'Other',
                                                                    'Quality Engineering and Transformation': 'Other',
                                                                    'Cognitive Business Operation': 'Other',
                                                                    'Other': 'Other',
                                                                    'Nenhum': 'Other',
                                                                    'Data & Analytics': 'Other',
                                                                    'Data &amp; Analytics': 'Other',
                                                                    'Digital Interactive': 'Other',
                                                                    'Analytics & Insights': 'Other',
                                                                    'Analytics &amp; Insights': 'Other',
                                                                    'Amazon Web Services': 'Other',
                                                                    'Cyber Security': 'Other',
                                                                    'Google Business Unit': 'Other',
                                                                    'Microsoft Business Unit': 'Other',
                                                                    'Cloud Apps, Microservices & APIfication': 'Other',
                                                                    'Cloud Apps, Microservices & APIfication': 'Other',
                                                                    'AI Transformation': 'Other',
                                                                    np.nan : 'Other'})

    """
    Tratativa da coluna de sindicato
    """
    WsUpdate['Sindicato'] = WsUpdate['Sindicato'].replace({'SINDPD/SP - SIND TRAB EMP PROC DADOS EST SP' : 'SP',
                                                        'SINDPD/RJ - Sind Trab Emp e Serv Pub e Priv de Inf Internet e Sim RJ' : 'RJ',
                                                        'SINTINORP/Londrina-Sind Trab Empr Cursos Inf Con S I D P A Bco Dados M' : 'Londrina',
                                                        'Nenhum' : 'Other',                                          
                                                        'SINDPD/DF - Sind dos Trab em Empr e Órgãos Publ Proc Dados S I S do DF': 'Other',
                                                        'SINDADOS/MG - Sind dos Empreg Emp de Proc Dados, Serv de Info Simil MG': 'Other',
                                                        'SINDPD/MA - Sind dos Empregados Proc Dados no Est do Maranhão': 'Other',
                                                        'SINDPD/PA - Sind Trabalhadores e Trabalhadoras em Tecn Informação Pará': 'Other',
                                                        'SINDPD/ES - Sind Empreg Emp Proc Dados e Trab em Inform do Est ES': 'Other',
                                                        'SPPD/MS - Sind Profissionais de Proc de Dados e Tec Informação de MS': 'Other',
                                                        'SINDPD/PR - Sind dos Trab em Empr de Processamento do Estado do Paraná': 'Other',
                                                        'SINDPD/PE - Sind Trab em Proc de Dados, Informat Tecn da Inform do PE': 'Other',
                                                        'SINDPD/RS - Sind dos Trabalhadores em Processamento de Dados no Est RS': 'Other',
                                                        'SINDPD/JOINVILLE - Sind Empreg em Empr Proc Dados Inform Simil Joinv': 'Other',
                                                        'SITEPD - Sind dos Trab Empr Priv de Proc de Dados de Curitiba e Região': 'Other',
                                                        'SINDADOS/BA - Sind Trab Empr e Órgãos Publ Proc Dados S I TI Com BA': 'Other'})

    """
    Tratativa da coluna situação
    """
    WsUpdate['Situação'] = WsUpdate['Situação'].replace({'Demitido em Meses Anteriores' : 'Separated',
                                                        'Demitido no Mês' : 'Separated',
                                                        'Em Atividade Normal' : 'Active',
                                                        'Gozando Férias' : 'Active',
                                                        'Auxílio-Doença' : 'Afastado',
                                                        'Suspensão Contratual (Art. 476-A da CLT)' : 'Afastado',
                                                        'Licença-Maternidade' : 'Afastado',
                                                        'Afastado sem Remuneração' : 'Afastado',
                                                        'Afastado por Aposentadoria Invalidez' : 'Afastado',
                                                        'Afastado Pré-Auxílio-Doença' : 'Afastado'})

    # Salva o novo arquivo tratado
    WsUpdate.to_excel('C:/Users/2977429/OneDrive - TCS COM PROD/Desktop/Automações/Bases modelo/Bases/Bases_Tratadas/Quadro_Geral_Tratado.xlsx', index=False)
    print("Quadro Geral concluído")