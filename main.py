import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

df = pd.read_csv("ListaContratos.csv",sep=';') # Disponível em: https://transparencia.pb.gov.br/compras/contratos

#print(df.head())

#print(df['CtNumero'])

df_tratado = df[['OrNome','Credor','ObNome','CtValorTotal']]

df_tratado.loc[:,'CtValorTotal'] = df_tratado['CtValorTotal'].str.replace('.','', regex=False)
df_tratado.loc[:,'CtValorTotal'] = df_tratado['CtValorTotal'].str.replace(',','.', regex=False)
df_tratado.loc[:,'CtValorTotal'] = df_tratado['CtValorTotal'].astype(float)

#print(df_tratado['CtValorTotal'].head())


def exportaGrafo(df):
    grafo = nx.Graph()
    for index, row in df.iterrows():
        
        grafo.add_edge(row['OrNome'], row['Credor'])
        grafo.add_edge(row['Credor'], '('+ row['Credor'] + ') ' + row['ObNome'])
        grafo.add_edge("Governo Estadual", row['OrNome'])

    #nx.draw(grafo,node_color="red",node_size=20)
    #plt.show()
    nx.write_graphml(grafo, "meu_grafo.graphml")

#exportaGrafo(df_tratado.head(100))


def exportaGrafoPesado(df):
    grafo = nx.Graph()

    total_secretaria = {}
    total_por_empresa_secretaria = {}

    for index, row in df.iterrows():
        secretaria = row['OrNome']
        empresa = row['Credor']
        servico = f'({row['Credor']}) {row['ObNome']}'  
        valor = row['CtValorTotal']

        grafo.add_node(servico)
        grafo.add_edge(servico,empresa,weight=valor)

        if(empresa,secretaria) in total_por_empresa_secretaria:
            total_por_empresa_secretaria[(empresa,secretaria)] += valor

        else:
            total_por_empresa_secretaria[(empresa,secretaria)] = valor

    for (cnpj, secretaria), valor_total in total_por_empresa_secretaria.items():
        grafo.add_edge(secretaria, cnpj, weight=valor_total)

        if secretaria in total_secretaria:
            total_secretaria[secretaria] += valor
        
        else:
            total_secretaria[secretaria] = valor

    #for secretaria, valor_total in total_secretaria.items():
    #    grafo.add_edge('governo estadual', secretaria, weight=valor_total)

        '''grafo.add_edge(row['OrNome'], row['Credor'])
        grafo.add_edge(row['Credor'], '('+ row['Credor'] + ') ' + row['ObNome'])
        grafo.add_edge("Governo Estadual", row['OrNome'])'''

    #nx.draw(grafo,node_color="red",node_size=20)
    #plt.show()
    nx.write_graphml(grafo, "meu_grafo.graphml")

exportaGrafoPesado(df_tratado.head(500))
#exportaGrafo(df_tratado.head(10))