import pandas as pd
from meu_grafo_matriz_adj_dir import *

df = pd.read_csv("ListaContratos.csv",sep=';') # Disponível em: https://transparencia.pb.gov.br/compras/contratos

#print(df.head())

#print(df['CtNumero'])

teste = MeuGrafo()

for i in range(2, len(df)+1):
    if not teste.existe_vertice("Teste"):
        