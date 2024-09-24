import pandas as pd
import numpy as np
import networkx as nx
import unidecode  # Para remover acentos e padronizar
import re

# Carregar o arquivo CSV
df = pd.read_csv("ListaContratos.csv", sep=';')

# Selecionar colunas relevantes
df_tratado = df[['OrNome', 'Credor', 'ObNome', 'CtValorTotal']]

# Tratamento de valores monetários e conversão
df_tratado.loc[:, 'CtValorTotal'] = df_tratado['CtValorTotal'].str.replace('.', '', regex=False)
df_tratado.loc[:, 'CtValorTotal'] = df_tratado['CtValorTotal'].str.replace(',', '.', regex=False)
df_tratado = df_tratado.replace({np.nan: 0.01})
df_tratado.loc[:, 'CtValorTotal'] = df_tratado['CtValorTotal'].astype(float)

# Função para extrair CNPJ/CPF do nome da empresa e limpar o nome
def extrair_cnpj(nome):
    match = re.match(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{3}\.\d{3}\.\d{3}-\d{2})', nome)
    return match.group(0) if match else None

# Adicionar uma nova coluna 'CNPJ_CPF' ao DataFrame e limpar a coluna 'Credor'
df_tratado['CNPJ_CPF'] = df_tratado['Credor'].apply(extrair_cnpj)
df_tratado['Credor'] = df_tratado['Credor'].str.replace(r'\s*\-\s*.*', '', regex=True).str.strip()  # Remove o CNPJ/CPF do nome

# Padronizando a coluna 'Credor' para eliminar duplicatas causadas por diferenças de acentuação e maiúsculas/minúsculas
df_tratado['Credor'] = df_tratado['Credor'].apply(lambda x: unidecode.unidecode(str(x).strip()).upper())

# Função para exportar o grafo simples (sem pesos)
def exportaGrafo(df):
    grafo = nx.Graph()
    for index, row in df.iterrows():
        grafo.add_edge(row['OrNome'], row['Credor'])
        grafo.add_edge(row['Credor'], '(' + row['Credor'] + ') ' + row['ObNome'])
        grafo.add_edge("Governo Estadual", row['OrNome'])

    nx.write_graphml(grafo, "meu_grafo.graphml")

# Função para criar o grafo pesado (com pesos)
def criaGrafoPesado(df):
    grafo = nx.DiGraph()

    total_secretaria = {}
    total_por_empresa_secretaria = {}

    for index, row in df.iterrows():
        secretaria = row['OrNome']
        grafo.add_node(secretaria, color='red')
        
        empresa = row['Credor']
        grafo.add_node(empresa, color='green')

        valor = row['CtValorTotal']

        # Acumular valores por secretaria-empresa
        if (empresa, secretaria) in total_por_empresa_secretaria:
            total_por_empresa_secretaria[(empresa, secretaria)] += valor
        else:
            total_por_empresa_secretaria[(empresa, secretaria)] = valor

        # Acumular valores por secretaria
        if secretaria in total_secretaria:
            total_secretaria[secretaria] += valor
        else:
            total_secretaria[secretaria] = valor

    # Criar as arestas com os pesos correspondentes
    for (empresa, secretaria), valor_total in total_por_empresa_secretaria.items():
        grafo.add_edge(secretaria, empresa, weight=valor_total)

    for secretaria, valor_total in total_secretaria.items():
        grafo.add_edge('Governo Estadual', secretaria, weight=valor_total)

    return grafo

# Função para analisar a centralidade das empresas
def analiseDados(g):
    # Calcula a centralidade de grau para todos os nós no grafo
    centralidade = nx.degree_centrality(g)

    # Dicionário para armazenar a centralidade das empresas
    centralidade_empresas = {}

    # Itera pelos nós do grafo e suas respectivas centralidades
    for node, cent in centralidade.items():
        # Verifica se o nó representa uma empresa (nós com cor 'green')
        if g.nodes[node].get('color') == 'green':
            centralidade_empresas[node] = cent

    # Retorna o dicionário de centralidade das empresas, ordenado em ordem decrescente
    return dict(sorted(centralidade_empresas.items(), key=lambda item: item[1], reverse=True))

# Função para calcular o grau de entrada das empresas
def grauEntradaEmpresas(grafo, df):
    grau_entrada = {}
    
    # Iterar sobre as empresas no dataframe
    for index, row in df.iterrows():
        empresa = row['Credor']
        # Pega o grau de entrada do vértice da empresa
        grau = grafo.in_degree(empresa)
        # Atualiza o grau de entrada
        grau_entrada[empresa] = grau
    
    return grau_entrada

# Criar o grafo pesado
grafo_pesado = criaGrafoPesado(df_tratado)

# Obter o grau de entrada das empresas
grau_empresas = grauEntradaEmpresas(grafo_pesado, df_tratado)

# Ordenar o dicionário em ordem decrescente de grau de entrada
grau_empresas_ordenado = dict(sorted(grau_empresas.items(), key=lambda item: item[1], reverse=False))

# Exibir os resultados
for empresa, grau in grau_empresas_ordenado.items():
    print(f"Empresa: {empresa}, Grau de Entrada: {grau}")

# Exemplo de uso para análise de centralidade
#resultado_centralidade = analiseDados(grafo_pesado)

# Exibir os resultados da centralidade
# for empresa, centralidade in resultado_centralidade.items():
#    print(f"Empresa: {empresa}, Centralidade: {centralidade}")
