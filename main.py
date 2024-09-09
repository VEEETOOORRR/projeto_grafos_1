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

exportaGrafo(df_tratado.head(100))

