import heapq
from common.enums import EntityType

   # -----------------------------------------------------------
   # A SER IMPLEMENTADO:
   # Lógica da powerball
   # Lógica para tentar pegar os fantasmas após powerball. (?)
   # Ordem das prioridades? Powerball > Fuga > Dot ou Fuga > Powerball > Dot?
   # Colisão, etc
   # -----------------------------------------------------------


class PacmanIA:

   # -----------------------------------------------------------
   # PRIORIDADES
   # 1) FUGIR de fantasmas próximos (usa A* para fugir)
   # 2) COMER dots quando está seguro (usa A* para buscar)
   # 3) Evita ficar preso em loops (memória de última posição, quando a distância do fantasma era a mesma em duas posições e não tinha
   #    mais dots, o Pacman ficava piscando entre elas. Quando a lógica de encerrar o jogo for adicionada, não vamos precisar mais disso.)
   # -----------------------------------------------------------

    DIST_PERIGO = 3  # Distância considerada perigosa, coloquei 3 casas mas pode ser mudado.
    FANTASMAS = [EntityType.BLINKY, EntityType.PINKY, EntityType.INKY, EntityType.CLYDE]
    
    def __init__(self):
        self.ultima_posicao = None  # Para evitar loops

    # -----------------------------------------------------------
    # DISTÂNCIAS E AUXILIARES
    # -----------------------------------------------------------
    @staticmethod
    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def reconstruir_caminho(veio_de, atual):
        caminho = [atual]
        while atual in veio_de:
            atual = veio_de[atual]
            caminho.append(atual)
        return caminho[::-1]

    def vizinhos(self, matriz, pos):
        x, y = pos
        candidatos = [
            (x, y - 1),
            (x, y + 1),
            (x - 1, y),
            (x + 1, y),
        ]

        validos = []
        for nx, ny in candidatos:
            cell = matriz.get_cell(nx, ny)
            if cell and cell.is_walkable():
                validos.append((nx, ny))

        return validos

    # -----------------------------------------------------------
    # A* COM AVALIAÇÃO DE PERIGO
    # -----------------------------------------------------------
    def calcular_perigo_posicao(self, matriz, pos):
        # Calcula o perigo de uma posição baseado em todos os fantasmas 
        perigo = 0
        for fantasma in self.FANTASMAS:
            pos_fantasma = matriz.get_entity_position(fantasma)
            if not pos_fantasma:
                continue
            
            dist = self.manhattan(pos, pos_fantasma)
            if dist <= self.DIST_PERIGO:
                perigo += (self.DIST_PERIGO - dist + 1) * 3
        
        return perigo

    def astar(self, matriz, inicio, destino, fugindo=False):
        
        # A* que considera perigo dos fantasmas
        # Se fugindo=True, prioriza caminhos mais seguros

        fila = []
        heapq.heappush(fila, (0, inicio))

        veio_de = {}
        gscore = {inicio: 0}

        while fila:
            _, atual = heapq.heappop(fila)

            if atual == destino:
                return self.reconstruir_caminho(veio_de, atual)

            for viz in self.vizinhos(matriz, atual):
                # Custo base
                custo = 1
                
                # Se estamos fugindo, adiciona peso alto em áreas perigosas
                if fugindo:
                    perigo = self.calcular_perigo_posicao(matriz, viz)
                    custo += perigo * 2
                
                novo_g = gscore[atual] + custo

                if novo_g < gscore.get(viz, 999999):
                    veio_de[viz] = atual
                    gscore[viz] = novo_g
                    fscore = novo_g + self.manhattan(viz, destino)
                    heapq.heappush(fila, (fscore, viz))

        return None

    # -----------------------------------------------------------
    # OBJETIVOS
    # -----------------------------------------------------------
    def fantasma_mais_proximo(self, matriz, pos_pac):
        # Retorna posição e distância do fantasma mais próximo 
        mais_perto = None
        melhor_dist = 999999

        for fantasma in self.FANTASMAS:
            pos = matriz.get_entity_position(fantasma)
            if not pos:
                continue

            dist = self.manhattan(pos, pos_pac)
            if dist < melhor_dist:
                melhor_dist = dist
                mais_perto = pos

        return mais_perto, melhor_dist

    def ponto_fuga(self, matriz, pos_pac):
        # -----------------------------------------------------------
        # Encontra o ponto  mais longe de todos os fantasmas (que não seja muro)
        # -----------------------------------------------------------
        melhor_pos = None
        melhor_dist = -1
        
        for y, linha in enumerate(matriz.matrix):
            for x, cell in enumerate(linha):
                if not cell.is_walkable():
                    continue
                
                # Calcula distância total de todos os fantasmas
                dist_total = 0
                for fantasma in self.FANTASMAS:
                    pos_f = matriz.get_entity_position(fantasma)
                    if pos_f:
                        dist_total += self.manhattan((x, y), pos_f)
                
                if dist_total > melhor_dist:
                    melhor_dist = dist_total
                    melhor_pos = (x, y)
        
        return melhor_pos

    def dot_mais_proximo(self, matriz, pos):
        """Encontra o pac-dot mais próximo"""
        melhor = None
        menor_dist = 999999

        for y, linha in enumerate(matriz.matrix):
            for x, cell in enumerate(linha):
                if cell.has_pac_dot():
                    dist = self.manhattan((x, y), pos)
                    if dist < menor_dist:
                        menor_dist = dist
                        melhor = (x, y)

        return melhor

    # -----------------------------------------------------------
    # UPDATE PRINCIPAL
    # -----------------------------------------------------------
    def update(self, matriz):
        pos_pac = matriz.get_entity_position(EntityType.PACMAN)
        if not pos_pac:
            return

        # 1) Verifica perigo
        pos_fantasma, dist_fantasma = self.fantasma_mais_proximo(matriz, pos_pac)

        # 2) Se fantasma está MUITO perto → FOGE!
        if dist_fantasma <= self.DIST_PERIGO:
            destino = self.ponto_fuga(matriz, pos_pac)
            if destino:
                caminho = self.astar(matriz, pos_pac, destino, fugindo=True)
                if caminho and len(caminho) > 1:
                    proximo = caminho[1]
                    
                    # Evita voltar para onde estava (anti-loop)
                    if proximo != self.ultima_posicao:
                        nx, ny = proximo
                        self.ultima_posicao = pos_pac
                        matriz.move_entity(EntityType.PACMAN, nx - pos_pac[0], ny - pos_pac[1])
                        return
                    elif len(caminho) > 2:  # Tenta o próximo no caminho
                        proximo = caminho[2]
                        nx, ny = proximo
                        self.ultima_posicao = pos_pac
                        matriz.move_entity(EntityType.PACMAN, nx - pos_pac[0], ny - pos_pac[1])
                        return

        # 3) Está seguro → busca dots
        destino = self.dot_mais_proximo(matriz, pos_pac)
        if destino:
            caminho = self.astar(matriz, pos_pac, destino, fugindo=False)
            if caminho and len(caminho) > 1:
                proximo = caminho[1]
                
                # Evita voltar (anti-loop)
                if proximo != self.ultima_posicao:
                    nx, ny = proximo
                    self.ultima_posicao = pos_pac
                    matriz.move_entity(EntityType.PACMAN, nx - pos_pac[0], ny - pos_pac[1])
                    return

        # 4) Último recurso: move para qualquer vizinho seguro
        vizinhos = self.vizinhos(matriz, pos_pac)
        if vizinhos:
            # Escolhe o vizinho com menor perigo que não seja a última posição
            melhor = None
            menor_perigo = 999999
            
            for v in vizinhos:
                if v == self.ultima_posicao:
                    continue
                perigo = self.calcular_perigo_posicao(matriz, v)
                if perigo < menor_perigo:
                    menor_perigo = perigo
                    melhor = v
            
            # Se todos os vizinhos são a última posição, aceita voltar
            if not melhor and vizinhos:
                melhor = vizinhos[0]
            
            if melhor:
                nx, ny = melhor
                self.ultima_posicao = pos_pac
                matriz.move_entity(EntityType.PACMAN, nx - pos_pac[0], ny - pos_pac[1])
