import pandas as pd
import numpy as np
import networkx as nx
import unidecode
import re

def separar_cnpj_nome(credor):
    match = re.match(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{3}\.\d{3}\.\d{3}-\d{2})\s*-\s*(.*)', credor)
    if match:
        cnpj_cpf = match.group(1)
        nome_empresa = match.group(2).strip()
        return pd.Series([cnpj_cpf, nome_empresa])
    return pd.Series([None, credor])

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

        if cnpj_cpf:
            if cnpj_cpf not in nomes_empresas:
                nomes_empresas[cnpj_cpf] = empresa
                print(f"Armazenando: {cnpj_cpf} -> {empresa}")  # Debug: Armazenando o CNPJ/CPF e nome da empresa

            grafo.add_node(cnpj_cpf, color='green', nome_empresa=nomes_empresas[cnpj_cpf])

            valor = row['CtValorTotal']

            if (cnpj_cpf, secretaria) in total_por_empresa_secretaria:
                total_por_empresa_secretaria[(cnpj_cpf, secretaria)] += valor
            else:
                total_por_empresa_secretaria[(cnpj_cpf, secretaria)] = valor

            if secretaria in total_secretaria:
                total_secretaria[secretaria] += valor
            else:
                total_secretaria[secretaria] = valor

    for (cnpj_cpf, secretaria), valor_total in total_por_empresa_secretaria.items():
        grafo.add_edge(secretaria, cnpj_cpf, weight=valor_total)

    for secretaria, valor_total in total_secretaria.items():
        grafo.add_edge('Governo Estadual', secretaria, weight=valor_total)

    return grafo

def grauEntradaEmpresas(grafo):
    grau_entrada = {}
    
    for cnpj_cpf in nomes_empresas.keys():
        grau = grafo.in_degree(cnpj_cpf)

        nome_empresa = grafo.nodes[cnpj_cpf].get('nome_empresa')
        grau_entrada[cnpj_cpf] = {
            'nome': nome_empresa,
            'grau': grau
        }
    grau_entrada = dict(sorted(grau_entrada.items(), key=lambda item: item[1]['grau'], reverse=False))
    return grau_entrada

df = pd.read_csv("ListaContratos.csv", sep=';')

df_tratado = df[['OrNome', 'Credor', 'ObNome', 'CtValorTotal']]

df_tratado.loc[:, 'CtValorTotal'] = df_tratado['CtValorTotal'].str.replace('.', '', regex=False)
df_tratado.loc[:, 'CtValorTotal'] = df_tratado['CtValorTotal'].str.replace(',', '.', regex=False)
df_tratado = df_tratado.replace({np.nan: 0.01})
df_tratado.loc[:, 'CtValorTotal'] = df_tratado['CtValorTotal'].astype(float)


df_tratado[['CNPJ_CPF', 'Nome_Empresa']] = df_tratado['Credor'].apply(separar_cnpj_nome)

df_tratado = df_tratado.drop(columns=['Credor'])

df_tratado['Nome_Empresa'] = df_tratado['Nome_Empresa'].apply(lambda x: unidecode.unidecode(str(x).strip()).upper())

nomes_empresas = {}

grafo_pesado = criaGrafoPesado(df_tratado)

grau_empresas = grauEntradaEmpresas(grafo_pesado)

for cnpj_cpf, info in grau_empresas.items():
    print(f"CNPJ/CPF: {cnpj_cpf}, Nome da Empresa: {info['nome']}, Grau de Entrada: {info['grau']}")

nx.write_graphml(grafo_pesado, "meu_grafo_pesado.graphml")