from bibgrafo.grafo_matriz_adj_dir import *
from bibgrafo.grafo_exceptions import *

class MeuGrafo(GrafoMatrizAdjacenciaDirecionado):

    def vertices_nao_adjacentes(self):
        '''
        Provê uma lista de vértices não adjacentes no grafo. A lista terá o seguinte formato: [X-Z, X-W, ...]
        Onde X, Z e W são vértices no grafo que não tem uma aresta entre eles.
        :return: Uma lista com os pares de vértices não adjacentes
        '''
        pass

    def ha_laco(self):
        '''
        Verifica se existe algum laço no grafo.
        :return: Um valor booleano que indica se existe algum laço.
        '''
        pass


    def grau(self, V=''):
        '''
        Provê o grau do vértice passado como parâmetro
        :param V: O rótulo do vértice a ser analisado
        :return: Um valor inteiro que indica o grau do vértice
        :raises: VerticeInvalidoException se o vértice não existe no grafo
        '''
        pass

    def ha_paralelas(self):
        '''
        Verifica se há arestas paralelas no grafo
        :return: Um valor booleano que indica se existem arestas paralelas no grafo.
        '''
        pass

    def arestas_sobre_vertice(self, V):
        '''
        Provê uma lista que contém os rótulos das arestas que incidem sobre o vértice passado como parâmetro
        :param V: O vértice a ser analisado
        :return: Uma lista os rótulos das arestas que incidem sobre o vértice
        :raises: VerticeInvalidoException se o vértice não existe no grafo
        '''
        if not self.existe_rotulo_vertice(V):
            raise VerticeInvalidoError
        
        vertice = self.get_vertice(V)
        index_v = self.indice_do_vertice(vertice)
        arestas = set()

        for i in range(len(self.vertices)):
            atual = self.arestas[index_v][i]
            for a in atual:
                arestas.add(a)

        return arestas


    def eh_completo(self):
        '''
        Verifica se o grafo é completo.
        :return: Um valor booleano que indica se o grafo é completo
        '''
        pass

    def warshall(self):
        '''
        Provê a matriz de alcançabilidade de Warshall do grafo
        :return: Uma lista de listas que representa a matriz de alcançabilidade de Warshall associada ao grafo
        '''
        
        def matriz(n_linhas, n_colunas):
            matriz = [] # Matriz
            linha = [] # Linha

            while len(matriz) != n_linhas: # Quando o número de elementos da matriz(linhas) forem diferentes da quantidade máxima definida pelo usuário, ele ficará rodando.
                linha.append(0) # Adiciono n à linha

                if len(linha) == n_colunas: # Se a quantidade de elementos for igual à quantidade de colunas definida pelo usuário :
                    matriz.append(linha) # Adiciono a linha à matriz
                    linha = [] # E zero a "linha" para adicionar outra à matriz
            return matriz # Retorno a mesma

        n = len(self.vertices)
        matriz_warshall = matriz(n,n)
        for i in range(n):
            for j in range(n):
                if len(self.arestas[i][j]) > 0:
                    matriz_warshall[i][j] = 1

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    matriz_warshall[i][j] = matriz_warshall[i][j] or (matriz_warshall[i][k] and matriz_warshall[k][j])

        return matriz_warshall
    
    
    def dijkstra(self, u, v):
        if not self.existe_rotulo_vertice(u):
            raise VerticeInvalidoError
        
        if not self.existe_rotulo_vertice(v):
            raise VerticeInvalidoError
        
        rotulos = {}
        vertices_visitados = set()

        rotulos[u] = [0, '']

        while len(vertices_visitados) != len(rotulos):
            menor_rotulo = None
            menor_distancia = float('inf')

            for vertice, (distancia, _) in rotulos.items():
                if vertice not in vertices_visitados and distancia < menor_distancia:
                    menor_distancia = distancia
                    menor_rotulo = vertice

            if menor_rotulo is None:
                break

            vertices_visitados.add(menor_rotulo)

            for aresta in self.arestas_sobre_vertice(menor_rotulo):
                aresta = self.get_aresta(aresta)
                if aresta.v1.rotulo == menor_rotulo:
                    vizinho = aresta.v2.rotulo
                    nova_distancia = rotulos[menor_rotulo][0] + aresta.peso

                    if vizinho not in rotulos or nova_distancia < rotulos[vizinho][0]:
                        rotulos[vizinho] = [nova_distancia, menor_rotulo]

        if v in rotulos:
            caminho = []
            atual = v
            while atual != '':
                caminho.append(atual)
                atual = rotulos[atual][1]
            caminho.reverse()
            return caminho, rotulos[v][0]
        else:
            return False
        
    def bellmanFord(self, u, v):
        if not self.existe_rotulo_vertice(u):
            raise VerticeInvalidoError
        
        if not self.existe_rotulo_vertice(v):
            raise VerticeInvalidoError
        
        rotulos = {}
        vertices_visitados = set()
        iteracao = 0
        rotulos[u] = [0, '']


        while iteracao < (len(self.vertices)-2):

            menor_rotulo = None
            menor_distancia = float('inf')

            for vertice, (distancia, _) in rotulos.items():
                if vertice not in vertices_visitados and distancia < menor_distancia:
                    menor_distancia = distancia
                    menor_rotulo = vertice

            if menor_rotulo is None:
                break

            vertices_visitados.add(menor_rotulo)

            for aresta in self.arestas_sobre_vertice(menor_rotulo):
                aresta = self.get_aresta(aresta)
                if aresta.v1.rotulo == menor_rotulo:
                    vizinho = aresta.v2.rotulo
                    nova_distancia = rotulos[menor_rotulo][0] + aresta.peso

                    if vizinho not in rotulos or nova_distancia < rotulos[vizinho][0]:
                        rotulos[vizinho] = [nova_distancia, menor_rotulo]
            
            iteracao += 1

        if v in rotulos:
            caminho = []
            atual = v
            while atual != '':
                caminho.append(atual)
                atual = rotulos[atual][1]
            caminho.reverse()
            return caminho, rotulos[v][0]
        else:
            return False