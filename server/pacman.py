import heapq
from common.enums import EntityType, ItemType
from common.game_state import GameState

class PacmanIA:
    # -----------------------------------------------------------
    # 1. Modo Normal: Foge de fantasmas e busca dots
    # 2. Frightened: Caça fantasmas ativamente
    # 3. Heatmap p fugir de áreas perigosas
    # 4. Fuga do loop de travamento
    # -----------------------------------------------------------


    DIST_PERIGO = 4  # Distância considerada perigosa
    FANTASMAS = [EntityType.BLINKY, EntityType.PINKY, EntityType.INKY, EntityType.CLYDE]
    
    def __init__(self):
        self.ultima_posicao = None
        self.historico_posicoes = []  # Últimas N posições
        self.MAX_HISTORICO = 5
        self.contador_travamento = 0
        self.heatmap = {}  # Mapa de calor de perigo
        self.ultima_atualizacao_heatmap = 0
        self.INTERVALO_HEATMAP = 3  # Atualiza heatmap a cada 3 updates

    # -----------------------------------------------------------
    # HEATMAP DE PERIGO
    # -----------------------------------------------------------
    def atualizar_heatmap(self, matriz):
        """Gera mapa de calor baseado apenas nos fantasmas ATIVOS"""
        self.heatmap.clear()
        
        for y in range(matriz.height()):
            for x in range(matriz.width()):
                cell = matriz.get_cell(x, y)
                if not cell or not cell.is_walkable():
                    continue
                
                perigo = 0
                for fantasma in self.FANTASMAS:
                    pos_f = matriz.get_entity_position(fantasma)
                    pos_inicial = matriz.initial_positions.get(fantasma)
                    
                    # Só considera fantasmas que saíram da posição inicial (estão em jogo)
                    if pos_f and pos_f != pos_inicial:
                        dist = self.manhattan((x, y), pos_f)
                        if dist <= self.DIST_PERIGO:
                            # Perigo exponencial: quanto mais perto, muito mais perigoso
                            perigo += (self.DIST_PERIGO - dist + 1) ** 2
                
                self.heatmap[(x, y)] = perigo
        
        self.ultima_atualizacao_heatmap = 0

    def obter_perigo(self, pos):
        """Retorna o nível de perigo de uma posição"""
        return self.heatmap.get(pos, 0)

    # -----------------------------------------------------------
    # DETECÇÃO E RESOLUÇÃO DE TRAVAMENTO
    # -----------------------------------------------------------
    def detectar_travamento(self, pos_atual):
        """Detecta se o Pac-Man está preso em loop"""
        self.historico_posicoes.append(pos_atual)
        
        if len(self.historico_posicoes) > self.MAX_HISTORICO:
            self.historico_posicoes.pop(0)
        
        if len(self.historico_posicoes) >= self.MAX_HISTORICO:
            # Verifica se está oscilando entre 2-3 posições
            posicoes_unicas = len(set(self.historico_posicoes))
            if posicoes_unicas <= 2:
                self.contador_travamento += 1
                return self.contador_travamento > 3
        
        self.contador_travamento = 0
        return False

    def movimento_aleatorio_seguro(self, matriz, pos_pac):
        """Escolhe um movimento aleatório para sair de travamento"""
        vizinhos = self.vizinhos(matriz, pos_pac)
        if not vizinhos:
            return None
        
        # Filtra vizinhos que não estão no histórico recente
        vizinhos_novos = [v for v in vizinhos if v not in self.historico_posicoes[-3:]]
        
        if vizinhos_novos:
            # Escolhe o mais seguro dos novos
            return min(vizinhos_novos, key=lambda v: self.obter_perigo(v))
        
        # Se todos estão no histórico, escolhe o menos perigoso
        return min(vizinhos, key=lambda v: self.obter_perigo(v))

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
            (x, y - 1),  # UP
            (x, y + 1),  # DOWN
            (x - 1, y),  # LEFT
            (x + 1, y),  # RIGHT
        ]

        validos = []
        for nx, ny in candidatos:
            cell = matriz.get_cell(nx, ny)
            if cell and cell.is_walkable():
                validos.append((nx, ny))

        return validos

    # -----------------------------------------------------------
    # A* COM HEATMAP
    # -----------------------------------------------------------
    def astar(self, matriz, inicio, destino, modo_caca=False):
        """
        A* que considera:
        - Heatmap de perigo (modo normal)
        - Prioriza proximidade no modo caça
        """
        fila = []
        heapq.heappush(fila, (0, inicio))

        veio_de = {}
        gscore = {inicio: 0}

        while fila:
            _, atual = heapq.heappop(fila)

            if atual == destino:
                return self.reconstruir_caminho(veio_de, atual)

            for viz in self.vizinhos(matriz, atual):
                custo = 1
                
                # No modo caça, ignora perigo; no modo normal, adiciona peso
                if not modo_caca:
                    perigo = self.obter_perigo(viz)
                    custo += perigo * 1.5
                
                novo_g = gscore[atual] + custo

                if novo_g < gscore.get(viz, 999999):
                    veio_de[viz] = atual
                    gscore[viz] = novo_g
                    fscore = novo_g + self.manhattan(viz, destino)
                    heapq.heappush(fila, (fscore, viz))

        return None

    # -----------------------------------------------------------
    # OBJETIVOS - MODO NORMAL
    # -----------------------------------------------------------
    def fantasmas_proximos(self, matriz, pos_pac):
        """Retorna lista de fantasmas ATIVOS próximos ordenados por distância"""
        fantasmas = []
        for fantasma in self.FANTASMAS:
            pos = matriz.get_entity_position(fantasma)
            # Verifica se o fantasma está em jogo (posição diferente da inicial)
            pos_inicial = matriz.initial_positions.get(fantasma)
            if pos and pos != pos_inicial:
                dist = self.manhattan(pos, pos_pac)
                fantasmas.append((fantasma, pos, dist))
        
        return sorted(fantasmas, key=lambda x: x[2])

    def ponto_fuga(self, matriz, pos_pac):
        """Encontra ponto de fuga otimizado usando heatmap"""
        melhor_pos = None
        menor_perigo = 999999
        
        # Busca em raio expandido ao redor do Pac-Man
        raio = 6
        x_pac, y_pac = pos_pac
        
        for dy in range(-raio, raio + 1):
            for dx in range(-raio, raio + 1):
                x, y = x_pac + dx, y_pac + dy
                cell = matriz.get_cell(x, y)
                
                if not cell or not cell.is_walkable():
                    continue
                
                perigo = self.obter_perigo((x, y))
                dist_atual = self.manhattan((x, y), pos_pac)
                
                # Prioriza locais com baixo perigo e não muito longe
                score = perigo + (dist_atual * 0.5)
                
                if score < menor_perigo:
                    menor_perigo = score
                    melhor_pos = (x, y)
        
        return melhor_pos

    def dot_mais_proximo(self, matriz, pos):
        """Encontra o pac-dot mais próximo considerando segurança"""
        melhor = None
        menor_score = 999999

        for y, linha in enumerate(matriz.matrix):
            for x, cell in enumerate(linha):
                if cell.has_pac_dot():
                    dist = self.manhattan((x, y), pos)
                    perigo = self.obter_perigo((x, y))
                    
                    # Score balanceado: distância + perigo
                    score = dist + (perigo * 0.3)
                    
                    if score < menor_score:
                        menor_score = score
                        melhor = (x, y)

        return melhor

    def power_pellet_mais_proximo(self, matriz, pos):
        """Encontra a power pellet mais próxima"""
        melhor = None
        menor_dist = 999999

        for y, linha in enumerate(matriz.matrix):
            for x, cell in enumerate(linha):
                if cell.has_power_pellet():
                    dist = self.manhattan((x, y), pos)
                    if dist < menor_dist:
                        menor_dist = dist
                        melhor = (x, y)

        return melhor

    # -----------------------------------------------------------
    # OBJETIVOS - MODO CAÇA (FRIGHTENED)
    # -----------------------------------------------------------
    def fantasma_mais_proximo_caca(self, matriz, pos_pac):
        """Encontra o fantasma ATIVO mais próximo para caçar (sem limite de distância)"""
        melhor_fantasma = None
        melhor_pos = None
        menor_dist = 999999

        for fantasma in self.FANTASMAS:
            pos = matriz.get_entity_position(fantasma)
            pos_inicial = matriz.initial_positions.get(fantasma)
            
            # Só considera fantasmas que saíram da posição inicial (estão em jogo)
            if pos and pos != pos_inicial:
                dist = self.manhattan(pos, pos_pac)
                if dist < menor_dist:
                    menor_dist = dist
                    melhor_fantasma = fantasma
                    melhor_pos = pos

        return melhor_fantasma, melhor_pos, menor_dist

    # -----------------------------------------------------------
    # EXECUÇÃO DE MOVIMENTO
    # -----------------------------------------------------------
    def executar_movimento(self, matriz, game_state, pos_pac, destino, modo_caca=False):
        """Executa movimento para o destino usando A*"""
        if not destino:
            return False
        
        caminho = self.astar(matriz, pos_pac, destino, modo_caca)
        
        if caminho and len(caminho) > 1:
            proximo = caminho[1]
            
            # Evita voltar imediatamente
            if proximo == self.ultima_posicao and len(caminho) > 2:
                proximo = caminho[2]
            
            nx, ny = proximo
            dx, dy = nx - pos_pac[0], ny - pos_pac[1]
            
            self.ultima_posicao = pos_pac
            collected_item = matriz.move_entity(EntityType.PACMAN, dx, dy)
            
            # Ativa modo frightened se coletou power pellet
            if collected_item == ItemType.POWER_PELLET:
                game_state.activate_frightened_mode()
            
            return True
        
        return False

    # -----------------------------------------------------------
    # UPDATE PRINCIPAL
    # -----------------------------------------------------------
    def update(self, game_state: GameState):
        matriz = game_state.matrix
        pos_pac = matriz.get_entity_position(EntityType.PACMAN)
        
        if not pos_pac:
            return

        # Atualiza heatmap periodicamente
        self.ultima_atualizacao_heatmap += 1
        if self.ultima_atualizacao_heatmap >= self.INTERVALO_HEATMAP:
            self.atualizar_heatmap(matriz)

        # Verifica travamento
        if self.detectar_travamento(pos_pac):
            destino = self.movimento_aleatorio_seguro(matriz, pos_pac)
            if destino:
                nx, ny = destino
                dx, dy = nx - pos_pac[0], ny - pos_pac[1]
                self.ultima_posicao = pos_pac
                collected_item = matriz.move_entity(EntityType.PACMAN, dx, dy)
                if collected_item == ItemType.POWER_PELLET:
                    game_state.activate_frightened_mode()
                self.historico_posicoes.clear()
            return

        # -----------------------------------------------------------
        # MODO FRIGHTENED: CAÇA FANTASMAS
        # -----------------------------------------------------------
        if game_state.is_frightened_mode():
            fantasma, pos_fantasma, dist = self.fantasma_mais_proximo_caca(matriz, pos_pac)
            
            if fantasma and pos_fantasma:
                # SEMPRE caça o fantasma mais próximo, não importa a distância
                if self.executar_movimento(matriz, game_state, pos_pac, pos_fantasma, modo_caca=True):
                    return
            
            # Fallback apenas se não conseguir calcular caminho para o fantasma
            # (possivelmente nunca vai acontecer, mas só para ter certeza)
            destino = self.dot_mais_proximo(matriz, pos_pac)
            if self.executar_movimento(matriz, game_state, pos_pac, destino, modo_caca=True):
                return

        # -----------------------------------------------------------
        # MODO NORMAL
        # -----------------------------------------------------------
        else:
            fantasmas_prox = self.fantasmas_proximos(matriz, pos_pac)
            
            # 1) PERIGO IMINENTE: FOGE
            if fantasmas_prox and fantasmas_prox[0][2] <= self.DIST_PERIGO:
                # Verifica se há power pellet próxima e alcançável
                power_pellet = self.power_pellet_mais_proximo(matriz, pos_pac)
                
                if power_pellet:
                    dist_pellet = self.manhattan(power_pellet, pos_pac)
                    dist_fantasma = fantasmas_prox[0][2]
                    
                    # Se power pellet está mais perto que o fantasma, vai pegá-la
                    if dist_pellet < dist_fantasma - 1:
                        if self.executar_movimento(matriz, game_state, pos_pac, power_pellet):
                            return
                
                # Caso contrário, foge
                destino = self.ponto_fuga(matriz, pos_pac)
                if self.executar_movimento(matriz, game_state, pos_pac, destino):
                    return
            
            # 2) PERIGO MODERADO: PRIORIZA POWER PELLET
            elif fantasmas_prox and fantasmas_prox[0][2] <= self.DIST_PERIGO + 2:
                power_pellet = self.power_pellet_mais_proximo(matriz, pos_pac)
                
                if power_pellet:
                    if self.executar_movimento(matriz, game_state, pos_pac, power_pellet):
                        return
                
                # Se não há power pellet, busca dots seguros
                destino = self.dot_mais_proximo(matriz, pos_pac)
                if self.executar_movimento(matriz, game_state, pos_pac, destino):
                    return
            
            # 3) SEGURO: BUSCA DOTS
            else:
                destino = self.dot_mais_proximo(matriz, pos_pac)
                if self.executar_movimento(matriz, game_state, pos_pac, destino):
                    return

        # 4) ÚLTIMO RECURSO: MOVIMENTO SEGURO QUALQUER
        vizinhos = self.vizinhos(matriz, pos_pac)
        if vizinhos:
            melhor = min(vizinhos, key=lambda v: (
                self.obter_perigo(v),
                v == self.ultima_posicao  # Penaliza voltar
            ))
            
            nx, ny = melhor
            dx, dy = nx - pos_pac[0], ny - pos_pac[1]
            self.ultima_posicao = pos_pac
            collected_item = matriz.move_entity(EntityType.PACMAN, dx, dy)
            if collected_item == ItemType.POWER_PELLET:
                game_state.activate_frightened_mode()
