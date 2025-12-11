import pygame

class SmoothEntity:
    def __init__(self, start_grid_x, start_grid_y, tile_size, lerp_factor=0.3):
        self.tile_size = tile_size
        self.lerp_factor = lerp_factor # Define uma "suavidade"

        # Posição visual atual
        self.x = start_grid_x * tile_size
        self.y = start_grid_y * tile_size

        # Posição alvo
        self.target_x = self.x
        self.target_y = self.y

    def update_target(self, grid_x, grid_y):
        """
            Atualiza o destino baseado na grade recebida do servidor.
        """
        self.target_x = grid_x * self.tile_size
        self.target_y = grid_y * self.tile_size

        """
            TODO: Quando o tunel estiver implementado realizar a correção dessa função para animação
            não ficar bugada.
        """

    def update(self):
        """
            Calcula o próximo frame da animação.
        """
        # Fórmula LERP
        self.x += (self.target_x - self.x) * self.lerp_factor
        self.y += (self.target_y - self.y) * self.lerp_factor

        # Garantindo que a entidade esteja perfeitamente centralizada # TODO: ajustar levemente (fantasma está entrando levemente na parede nas curvas)
        epsilon = 0.5 

        if abs(self.target_x - self.x) < epsilon:
            self.x = self.target_x
        
        if abs(self.target_y - self.y) < epsilon:
            self.y = self.target_y
    
    def get_pos(self):
        """ 
            Retorna a tupla (x,y) inteira para desenhar.
        """
        return int(self.x), int(self.y)