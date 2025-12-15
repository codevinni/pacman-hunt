import pygame
import os
from typing import Dict, Optional

class SoundManager:
   
    def __init__(self, assets_path: str, volume: float = 0.7):
        #inicializa gerenciador de 0.0 a 1.0
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        self.assets_path = assets_path
        self.volume = volume
        self.music_volume = 0.3  # Música de fundo mais baixa
        
        # dict de som
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_playing = None
        
        # Estado do jogo para controle de sons
        self.frightened_mode_active = False
        self.game_started = False
        
        # Carrega todos os sons
        self._load_sounds()
    

     
    def _load_sounds(self):
        """Carrega todos os arquivos de som disponíveis"""
        sound_files = {
            'eat_dot': ['eat_dot_0.wav', 'eat_dot_1.wav'], 
            'eat_fruit': 'eat_fruit.wav',
            'eat_ghost': 'eat_ghost.wav',
            'death': ['death_0.wav', 'death_1.wav'], 
            'eyes': 'eyes.wav',  
            'fright': 'fright.wav',  
            'fright_firstloop': 'fright_firstloop.wav', 
            'extend': 'extend.wav',  
            'intermission': 'intermission.wav',
            'siren': ['siren0.wav', 'siren1.wav', 'siren2.wav', 'siren3.wav', 'siren4.wav'],
            'siren_firstloop': ['siren0_firstloop.wav', 'siren1_firstloop.wav', 
                               'siren2_firstloop.wav', 'siren3_firstloop.wav', 
                               'siren4_firstloop.wav'],
            'start': 'start.wav',
            'credit': 'credit.wav'
        }
        
        for sound_name, files in sound_files.items():
            if isinstance(files, list):
                # Múltiplos arquivos para o mesmo som
                self.sounds[sound_name] = []
                for file in files:
                    sound = self._load_sound_file(file)
                    if sound:
                        self.sounds[sound_name].append(sound)
            else:
                # Arquivo único
                sound = self._load_sound_file(files)
                if sound:
                    self.sounds[sound_name] = sound
    
    def _load_sound_file(self, filename: str) -> Optional[pygame.mixer.Sound]:
        """Carrega um arquivo de som individual"""
        filepath = os.path.join(self.assets_path, filename)
        try:
            if os.path.exists(filepath):
                sound = pygame.mixer.Sound(filepath)
                sound.set_volume(self.volume)
                return sound
            else:
                print(f"Aviso: Som não encontrado: {filepath}")
                return None
        except Exception as e:
            print(f"Erro ao carregar som {filename}: {e}")
            return None
    
    # ===================================================================
    # SONS DE EVENTOS DE JOGO
    # ===================================================================
    
    def play_start(self):
        """Som de início do jogo"""
        self.stop_all_sounds()
        self.game_started = False
        self._play_sound('start')
        # Após 4.2 segundos (duração aproximada), inicia sirene
        pygame.time.set_timer(pygame.USEREVENT + 1, 4200, 1)
    
    def play_eat_dot(self, alternate: bool = True):
        """
        Som de comer pac-dot (alterna entre 2 sons para naturalidade)
        
        Args:
            alternate: Se True, alterna entre eat_dot_0 e eat_dot_1
        """
        sounds = self.sounds.get('eat_dot', [])
        if sounds and isinstance(sounds, list):
            import random
            sound = random.choice(sounds) if not alternate else sounds[0]
            self._play_sound_direct(sound, volume=0.4)
    
    def play_eat_power_pellet(self):
        """Som de comer power pellet - inicia modo frightened"""
        self.frightened_mode_active = True
        self.stop_siren()
        
        # Toca som inicial do frightened
        fright_first = self.sounds.get('fright_firstloop')
        if fright_first:
            fright_first.play()
        
        # Após o primeiro loop, toca o loop contínuo
        pygame.time.set_timer(pygame.USEREVENT + 2, 500, 1)
    
    def play_eat_ghost(self):
        """Som de comer fantasma"""
        self._play_sound('eat_ghost', volume=0.8)
    
    def play_eat_fruit(self):
        """Som de comer fruta"""
        self._play_sound('eat_fruit', volume=0.6)
    
    def play_death(self):
        """Som de morte do Pac-Man"""
        self.stop_all_sounds()
        sounds = self.sounds.get('death', [])
        if sounds and isinstance(sounds, list):
            import random
            sound = random.choice(sounds)
            self._play_sound_direct(sound)
    
    def play_intermission(self):
        """Som entre rounds/fases"""
        self.stop_all_sounds()
        self._play_sound('intermission')
    
    def play_extend(self):
        """Som de vida extra (se implementar)"""
        self._play_sound('extend', volume=0.5)
    
    # ===================================================================
    # SONS CONTÍNUOS (LOOPS)
    # ===================================================================
    
    def play_siren(self, level: int = 0):
        """
        Toca sirene (som de perseguição dos fantasmas)
        
        Args:
            level: Nível da sirene (0-4), aumenta conforme menos dots restam
        """
        if self.frightened_mode_active:
            return
        
        self.game_started = True
        
        # Limita nível
        level = max(0, min(4, level))
        
        sirens = self.sounds.get('siren', [])
        if sirens and isinstance(sirens, list) and level < len(sirens):
            siren = sirens[level]
            if not pygame.mixer.get_busy() or self.music_playing != f'siren_{level}':
                siren.play(loops=-1)  # Loop infinito
                self.music_playing = f'siren_{level}'
    
    def play_fright_loop(self):
        """Loop contínuo do modo frightened"""
        if self.frightened_mode_active:
            fright = self.sounds.get('fright')
            if fright:
                fright.play(loops=-1)
                self.music_playing = 'fright'
    
    def play_eyes(self):
        """Som de fantasma morto voltando para casa"""
        eyes = self.sounds.get('eyes')
        if eyes and not pygame.mixer.Channel(1).get_busy():
            pygame.mixer.Channel(1).play(eyes, loops=-1)
    
    def stop_eyes(self):
        """Para o som dos olhos"""
        pygame.mixer.Channel(1).stop()
    
    def stop_fright_mode(self):
        """Para o modo frightened e volta à sirene"""
        self.frightened_mode_active = False
        self.stop_all_sounds()
        self.play_siren()
    
    def stop_siren(self):
        """Para a sirene"""
        pygame.mixer.stop()
        self.music_playing = None
    
    def stop_all_sounds(self):
        """Para todos os sons"""
        pygame.mixer.stop()
        self.music_playing = None
    
    # ===================================================================
    # UTILITÁRIOS
    # ===================================================================
    
    def _play_sound(self, sound_name: str, volume: Optional[float] = None):
        #tocar som por nome
        sound = self.sounds.get(sound_name)
        if sound:
            if isinstance(sound, list):
                sound = sound[0]  # Pega primeiro se for lista
            self._play_sound_direct(sound, volume)
    
    def _play_sound_direct(self, sound: pygame.mixer.Sound, volume: Optional[float] = None):
        #tocar som por path direto
        if sound:
            if volume is not None:
                original_vol = sound.get_volume()
                sound.set_volume(volume)
                sound.play()
                sound.set_volume(original_vol)
            else:
                sound.play()
    
    def set_volume(self, volume: float):
        #volume de 0.0 até 1.0
        self.volume = max(0.0, min(1.0, volume))
        for sound_name, sound in self.sounds.items():
            if isinstance(sound, list):
                for s in sound:
                    s.set_volume(self.volume)
            else:
                sound.set_volume(self.volume)
    
    def set_music_volume(self, volume: float):
        #música 0.0 a 1.0
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def toggle_mute(self):
        if self.volume > 0:
            self._previous_volume = self.volume
            self.set_volume(0.0)
        else:
            self.set_volume(getattr(self, '_previous_volume', 0.7))
    
    def update(self, game_state):
       
        # Inicia/para frightened mode
        if game_state.is_frightened_mode() and not self.frightened_mode_active:
            self.play_eat_power_pellet()
        elif not game_state.is_frightened_mode() and self.frightened_mode_active:
            self.stop_fright_mode()
        
        # Ajusta nível da sirene baseado em dots restantes
        if self.game_started and not self.frightened_mode_active:
            # Conta dots restantes (implementar lógica se necessário)
            # self.play_siren(level=nivel_calculado)
            pass
    
    def cleanup(self):
        self.stop_all_sounds()
        pygame.mixer.quit()
