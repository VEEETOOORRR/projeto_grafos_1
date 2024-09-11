import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

df = pd.read_csv("ListaContratos.csv", sep=';')

df_tratado = df[['OrNome', 'Credor', 'ObNome', 'CtValorTotal']]

df_tratado.loc[:, 'CtValorTotal'] = df_tratado['CtValorTotal'].str.replace('.', '', regex=False)
df_tratado.loc[:, 'CtValorTotal'] = df_tratado['CtValorTotal'].str.replace(',', '.', regex=False)
df_tratado.loc[:, 'CtValorTotal'] = df_tratado['CtValorTotal'].astype(float)


def exportaGrafo(df):
    grafo = nx.Graph()
    for index, row in df.iterrows():
        grafo.add_edge(row['OrNome'], row['Credor'])
        grafo.add_edge(row['Credor'], '(' + row['Credor'] + ') ' + row['ObNome'])
        grafo.add_edge("Governo Estadual", row['OrNome'])

    nx.write_graphml(grafo, "meu_grafo.graphml")


def exportaGrafoPesado(df):
    grafo = nx.DiGraph()

    total_secretaria = {}
    total_por_empresa_secretaria = {}

    for index, row in df.iterrows():
        secretaria = row['OrNome']
        grafo.add_node(secretaria, color='red')
        
        empresa = row['Credor']
        grafo.add_node(empresa, color='green')

        servico = f'({row["Credor"]}) {row["ObNome"]}'
        grafo.add_node(servico, color='blue')
        
        valor = row['CtValorTotal']

        grafo.add_node(servico)
        grafo.add_edge(empresa, servico, weight=valor)

        if (empresa, secretaria) in total_por_empresa_secretaria:
            total_por_empresa_secretaria[(empresa, secretaria)] += valor
        else:
            total_por_empresa_secretaria[(empresa, secretaria)] = valor

        # Acumulando valores por secretaria
        if secretaria in total_secretaria:
            total_secretaria[secretaria] += valor
        else:
            total_secretaria[secretaria] = valor

    for (empresa, secretaria), valor_total in total_por_empresa_secretaria.items():
        grafo.add_edge(secretaria, empresa, weight=valor_total)

    for secretaria, valor_total in total_secretaria.items():
        grafo.add_edge('Governo Estadual', secretaria, weight=valor_total)

    nx.write_graphml(grafo, "meu_grafo_pesado.graphml")


exportaGrafoPesado(df_tratado)
