import pandas as pd
import numpy as np
import networkx as nx
import unidecode  # Para remover acentos e padronizar
import re

# Função para separar CNPJ/CPF e Nome da Empresa
def separar_cnpj_nome(credor):
    match = re.match(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{3}\.\d{3}\.\d{3}-\d{2})\s*-\s*(.*)', credor)
    if match:
        cnpj_cpf = match.group(1)
        nome_empresa = match.group(2).strip()
        return pd.Series([cnpj_cpf, nome_empresa])
    return pd.Series([None, credor])

# Carregar o arquivo CSV
df = pd.read_csv("ListaContratos.csv", sep=';')

# Selecionar colunas relevantes
df_tratado = df[['OrNome', 'Credor', 'ObNome', 'CtValorTotal']]

# Tratamento de valores monetários e conversão
df_tratado.loc[:, 'CtValorTotal'] = df_tratado['CtValorTotal'].str.replace('.', '', regex=False)
df_tratado.loc[:, 'CtValorTotal'] = df_tratado['CtValorTotal'].str.replace(',', '.', regex=False)
df_tratado = df_tratado.replace({np.nan: 0.01})
df_tratado.loc[:, 'CtValorTotal'] = df_tratado['CtValorTotal'].astype(float)


# Aplicar a função e criar novas colunas
df_tratado[['CNPJ_CPF', 'Nome_Empresa']] = df_tratado['Credor'].apply(separar_cnpj_nome)

# Remover a coluna original de 'Credor', se necessário
df_tratado = df_tratado.drop(columns=['Credor'])

# Padronizando a coluna 'Nome_Empresa' para eliminar duplicatas
df_tratado['Nome_Empresa'] = df_tratado['Nome_Empresa'].apply(lambda x: unidecode.unidecode(str(x).strip()).upper())

# Exibir o DataFrame tratado
print(df_tratado.head())

# Criar um dicionário para armazenar os nomes das empresas a partir do CNPJ/CPF
nomes_empresas = {}

# Função para criar o grafo pesado (com pesos)
def criaGrafoPesado(df):
    grafo = nx.DiGraph()
    total_secretaria = {}
    total_por_empresa_secretaria = {}

    for index, row in df.iterrows():
        secretaria = row['OrNome']
        grafo.add_node(secretaria, color='red')

        # Use o CNPJ/CPF como o identificador da empresa
        cnpj_cpf = row['CNPJ_CPF']
        empresa = row['Nome_Empresa']

        # Verifique se o CNPJ/CPF é válido antes de armazenar
        if cnpj_cpf:
            # Armazenar o nome da empresa pelo CNPJ/CPF (apenas a primeira ocorrência)
            if cnpj_cpf not in nomes_empresas:
                nomes_empresas[cnpj_cpf] = empresa
                print(f"Armazenando: {cnpj_cpf} -> {empresa}")  # Debug: Armazenando o CNPJ/CPF e nome da empresa

            # Adiciona o CNPJ/CPF ao grafo
            grafo.add_node(cnpj_cpf, color='green', nome_empresa=nomes_empresas[cnpj_cpf])

            valor = row['CtValorTotal']

            # Acumular valores por secretaria-empresa
            if (cnpj_cpf, secretaria) in total_por_empresa_secretaria:
                total_por_empresa_secretaria[(cnpj_cpf, secretaria)] += valor
            else:
                total_por_empresa_secretaria[(cnpj_cpf, secretaria)] = valor

            # Acumular valores por secretaria
            if secretaria in total_secretaria:
                total_secretaria[secretaria] += valor
            else:
                total_secretaria[secretaria] = valor

    # Criar as arestas com os pesos correspondentes
    for (cnpj_cpf, secretaria), valor_total in total_por_empresa_secretaria.items():
        grafo.add_edge(secretaria, cnpj_cpf, weight=valor_total)

    for secretaria, valor_total in total_secretaria.items():
        grafo.add_edge('Governo Estadual', secretaria, weight=valor_total)

    return grafo

# Função para calcular o grau de entrada das empresas
def grauEntradaEmpresas(grafo):
    grau_entrada = {}
    
    # Iterar sobre as chaves (CNPJ/CPF) armazenadas
    for cnpj_cpf in nomes_empresas.keys():
        # Pega o grau de entrada do vértice da empresa
        grau = grafo.in_degree(cnpj_cpf)

        # Atualiza o grau de entrada e o nome da empresa
        nome_empresa = grafo.nodes[cnpj_cpf].get('nome_empresa')
        grau_entrada[cnpj_cpf] = {
            'nome': nome_empresa,
            'grau': grau
        }
    grau_entrada = dict(sorted(grau_entrada.items(), key=lambda item: item[1]['grau'], reverse=False))
    return grau_entrada

# Criar o grafo pesado
grafo_pesado = criaGrafoPesado(df_tratado)

# Obter o grau de entrada das empresas
grau_empresas = grauEntradaEmpresas(grafo_pesado)

for cnpj_cpf, info in grau_empresas.items():
    print(f"CNPJ/CPF: {cnpj_cpf}, Nome da Empresa: {info['nome']}, Grau de Entrada: {info['grau']}")

nx.write_graphml(grafo_pesado, "meu_grafo_pesado.graphml")