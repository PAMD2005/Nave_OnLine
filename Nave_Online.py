

import tkinter as tk  
import tkinter.font as tkFont  # Alterar o Font
import random  
import os  
import urllib.request  # Requisições HTTP
import json # API precisa 
from PIL import Image, ImageTk  
import pygame  # Reprodução de áudio (apenas usei para audio)


width = 1000
height = 800
base_speed_planet = 10  # Velocidade base dos planetas
max_durability = 10  # Usos máximos da rede
max_vidas = 5  # Número máximo de vidas da nave
# Pontuação necessária para entrar no nível final
final_score = 100
# URL da API
EXOPLANET_API = (
    "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    "?query=select+pl_name+from+ps&format=json"
)


# Lista com nomes das imagens dos planetas
ordem_planetas = [
    "mercury", "venus", "earth", "mars",
    "jupiter", "saturn", "uranus", "neptune",
    "random_planet_1","random_planet_2","random_planet_3",
    "random_planet_4","random_planet_5","random_planet_6", 
    "random_planet_7", "random_planet_8"
]


class JogoNave:
    def __init__(self, root):
        self.root = root
        self.root.title("Nave OnLine 🚀")  

        # Tamanhos diferentes de Font para usar ao longo do condigo
        self.futuro_10 = ("Orbitron", 10)
        self.futuro_12 = ("Orbitron", 12)
        self.futuro_16 = ("Orbitron", 16)
        self.futuro_24 = ("Orbitron", 24)
        self.futuro_40 = ("Orbitron", 40)

        # Obtem os nomes de exoplanetas da API
        try:
            req = urllib.request.Request(EXOPLANET_API, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                dados = json.load(resp)
            self.nomes_exo = list({item["pl_name"] for item in dados})
        except:
            # Lista reserva caso a API falhe
            self.nomes_exo = ["Kepler-22b", "Proxima Centauri b", "TRAPPIST-1e", "HD 209458 b"]

        # Caminhos para arquivos
        self.script_dir = os.path.dirname(os.path.abspath(__file__))  # Para obter o Path Abs do .py \\ o dirname para fazer .. a path
        self.img_path = os.path.join(self.script_dir, 'Imgs') 
        self.audio_path = os.path.join(self.script_dir, 'Audio') 

        pygame.mixer.init()
        # Prepara os audios
        self.som_captura = pygame.mixer.Sound(os.path.join(self.audio_path, "capture.mp3"))
        self.som_impacto = pygame.mixer.Sound(os.path.join(self.audio_path, "impact.mp3"))
        self.som_rede = pygame.mixer.Sound(os.path.join(self.audio_path, "net_rip.mp3"))
        self.som_reparar_nave = pygame.mixer.Sound(os.path.join(self.audio_path, "repair_ship.mp3"))
        self.som_game_over = pygame.mixer.Sound(os.path.join(self.audio_path, "game_over.mp3"))
        self.som_next_level = pygame.mixer.Sound(os.path.join(self.audio_path, "next_level.mp3"))
        self.som_victory = pygame.mixer.Sound(os.path.join(self.audio_path, "victory.mp3"))

        # Prepara a musica de fundo
        pygame.mixer.music.load(os.path.join(self.audio_path, "bg_music.mp3"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1) # -1 Repete Infinito


        self.canvas = tk.Canvas(root, width=width, height=height)
        self.canvas.pack()

        # imagens de background
        fundos = ['bg_space.jpg', 'bg_space_2.jpg', 'bg_space_3.jpg', 'bg_space_4.jpg', 
                 'bg_space_5.jpg', 'bg_space_3.png', 'bg_space_4.png', 'bg_space_5.png']
        self.bg_images = []
        for f in fundos:
            p = os.path.join(self.img_path, f)
            if os.path.exists(p):
                img = Image.open(p).resize((width, height), Image.LANCZOS)
                self.bg_images.append(ImageTk.PhotoImage(img))

        self.bg_image_id = self.canvas.create_image(0, 0, anchor='nw', image=self.bg_images[0])

        # imagem do buraco negro (nivel final) 
        bh_path = os.path.join(self.img_path, 'black_hole.png')
        if os.path.exists(bh_path):
            bh = Image.open(bh_path)
            # Tamanho da img 
            ratio = 700 / bh.width
            bh = bh.resize((700, int(bh.height * ratio)), Image.LANCZOS).rotate(90, expand=True)
            self.bh_img = ImageTk.PhotoImage(bh)
        else:
            self.bh_img = None

        self.nave_x = 75  # Posicao inicial X da nave
        self.nave_y = height // 2  # Posicao inicial Y da nave
        self.rede_ativa = False  # Estado da rede (ativa ou nao)
        self.durabilidade_rede = max_durability  # Durabilidade inicial da rede
        self.vidas = 3  # Vidas iniciais da nave
        self.pontuacao = 0  # Pontuacao inicial
        self.nivel = 0  # Nivel inicial (0 a 10)
        self.final_round = False  # Valida se esta no nivel final
        self.meteor_count = 0  # Contador de meteoros criados no nivel final

        # Listas para armazenar objetos do jogo
        self.planetas = []
        self.objetos_recarga = []
        self.meteoros = []
        self.objetos_vida = []
        self.net_img = None
        self.string_images = []
        self.planeta_images = []

        # Prepara a imagem dos planetas
        self.pil_planetas = {}
        for nome in ordem_planetas:
            foto_planeta = os.path.join(self.img_path, f"{nome}.png")
            if os.path.exists(foto_planeta):
                self.pil_planetas[nome] = Image.open(foto_planeta)

        # Prepara a imagem da nave
        ship = Image.open(os.path.join(self.img_path, 'spaceship.png'))
        self.nave_img = ImageTk.PhotoImage(ship.resize((50, 50), Image.LANCZOS).rotate(270, expand=True))
        self.nave = self.canvas.create_image(self.nave_x, self.nave_y + 25, image=self.nave_img, anchor='center')

        # Texto para a pontuacao e nivel 
        self.texto_pontuacao = self.canvas.create_text(width - 200, 30, text="Pontos: 0", fill="white", font=self.futuro_16)
        self.texto_nivel = self.canvas.create_text(width - 80, 30, text="Nível: 1", fill="lightgreen", font=self.futuro_16)

        # Barra de vida e durabilidade (rede)
        self.canvas.create_text(20, 20, text="Vida", anchor="nw", fill="white", font=self.futuro_12)
        self.canvas.create_text(20, 60, text="Usos da Rede", anchor="nw", fill="white", font=self.futuro_12)
        self.barra_vida_quadrados = []
        self.barra_durabilidade_quadrados = []
        self.desenhar_barra_vida()  # Desenha barra de vida
        self.desenhar_barra_durabilidade()  # Desenha barra de durabilidade

        # Controlos
        self.root.bind("<Up>", self.mover_cima)
        self.root.bind("<Down>", self.mover_baixo)
        self.root.bind("<Left>", self.mover_esquerda)
        self.root.bind("<Right>", self.mover_direita)
        self.root.bind("w", self.mover_cima)
        self.root.bind("s", self.mover_baixo)
        self.root.bind("a", self.mover_esquerda)
        self.root.bind("d", self.mover_direita)
        self.root.bind("W", self.mover_cima)
        self.root.bind("S", self.mover_baixo)
        self.root.bind("A", self.mover_esquerda)
        self.root.bind("D", self.mover_direita)
        self.root.bind("<space>", self.alternar_rede)

        # Imagens dos meteoros e item de regarda
        met = Image.open(os.path.join(self.img_path, 'meteor.png'))
        self.img_meteor = ImageTk.PhotoImage(met.resize((40, 40), Image.LANCZOS))
        self.img_meteor_big = ImageTk.PhotoImage(met.resize((80, 80), Image.LANCZOS))
        wh = Image.open(os.path.join(self.img_path, 'wrench.png'))
        self.img_wrench = ImageTk.PhotoImage(wh.resize((30, 30), Image.LANCZOS))
        met2 = Image.open(os.path.join(self.img_path, 'meteor2.png'))
        self.img_meteor2 = ImageTk.PhotoImage(met2.resize((40, 40), Image.LANCZOS))
        self.img_meteor_big2 = ImageTk.PhotoImage(met2.resize((80, 80), Image.LANCZOS))

        # Comeca o jogo e mostra primeiros as "instrucoes"
        self.canvas.focus_set()
        self.mostrar_instrucoes()

    # Movimentação da Nave
    def mover_cima(self, e):
        if self.nave_y > 0:
            self.nave_y -= 20
            self.canvas.move(self.nave, 0, -20)
            if self.rede_ativa:
                self.canvas.move(self.rede, 0, -20)

    def mover_baixo(self, e):
        if self.nave_y < height - 50:
            self.nave_y += 20
            self.canvas.move(self.nave, 0, 20)
            if self.rede_ativa:
                self.canvas.move(self.rede, 0, 20)

    def mover_esquerda(self, e):
        if self.nave_x > 25:
            self.nave_x -= 20
            self.canvas.move(self.nave, -20, 0)
            if self.rede_ativa:
                self.canvas.move(self.rede, -20, 0)

    def mover_direita(self, e):
        if self.nave_x < width - 25:
            self.nave_x += 20
            self.canvas.move(self.nave, 20, 0)
            if self.rede_ativa:
                self.canvas.move(self.rede, 20, 0)

    # Controlo da Rede 
    def alternar_rede(self, e):
        if self.rede_ativa:
            self.recolher_rede()
        elif self.durabilidade_rede > 0:
            self.soltar_rede()

    def soltar_rede(self):
        self.rede_ativa = True
        np = os.path.join(self.img_path, 'net.png')
        self.net_img = ImageTk.PhotoImage(Image.open(np).resize((40,40), Image.LANCZOS))
        self.rede = self.canvas.create_image(self.nave_x+50, self.nave_y+25, image=self.net_img, anchor='center')

    def recolher_rede(self):
        self.rede_ativa = False
        if hasattr(self, 'rede'):
            self.canvas.delete(self.rede)

    # Barra de Vida e Durabilidades (rede)
    def desenhar_barra_vida(self):
        for r in self.barra_vida_quadrados:
            self.canvas.delete(r)
        self.barra_vida_quadrados.clear()
        x0, y0, largura, distancia = 20, 40, 20, 5
        for i in range(self.vidas):
            r = self.canvas.create_rectangle(x0 + i*(largura+distancia), y0, x0 + i*(largura+distancia) + largura, y0 + largura, fill="red", outline="white")
            self.barra_vida_quadrados.append(r)

    def desenhar_barra_durabilidade(self):
        for r in self.barra_durabilidade_quadrados:
            self.canvas.delete(r)
        self.barra_durabilidade_quadrados.clear()
        x0, y0, largura, distancia = 20, 80, 20, 5
        for i in range(self.durabilidade_rede):
            r = self.canvas.create_rectangle(x0 + i*(largura+distancia), y0, x0 + i*(largura+distancia) + largura, y0 + largura, fill="lightblue", outline="white")
            self.barra_durabilidade_quadrados.append(r)

    def atualizar_barra_vida(self):
        self.desenhar_barra_vida()

    def atualizar_barra_durabilidade(self):
        self.desenhar_barra_durabilidade()

    def reparar_rede(self, e):
        if not self.rede_ativa and self.durabilidade_rede < max_durability:
            self.durabilidade_rede = max_durability
            self.atualizar_barra_durabilidade()

    # Cria Planetas 
    def criar_planeta(self):
        if self.final_round:
            return  # nao cria planetas no nivel final
        nome_img = ordem_planetas[self.nivel] if self.nivel <= 7 else random.choice(ordem_planetas[8:])
        if nome_img in self.pil_planetas:
            size_map = {0:30,1:35,2:40,3:45,4:50,5:53,6:56,7:60}
            novo = size_map.get(self.nivel, 66)
            pil = self.pil_planetas[nome_img].resize((novo, novo), Image.LANCZOS)
            foto = ImageTk.PhotoImage(pil)
            self.planeta_images.append(foto)
            y = random.randint(30, height - 45)
            p = self.canvas.create_image(width + 30, y, image=foto, anchor='center')
            nome_exo = random.choice(self.nomes_exo)
            lbl = self.canvas.create_text(width + 30, y + novo//2 + 5, text=nome_exo, fill="white", font=self.futuro_10)
            self.planetas.append((p, lbl, nome_img))

    # Cria a recarga da linha
    def criar_recarga(self):
        if self.final_round:
            return  # não cria recargas de rede no nível final
        y = random.randint(50, height - 50)
        sp = os.path.join(self.img_path, 'string.png')
        img = ImageTk.PhotoImage(Image.open(sp).resize((30, 30), Image.LANCZOS))
        self.string_images.append(img)
        o = self.canvas.create_image(width + 30, y, image=img, anchor='center')
        self.objetos_recarga.append(o)

    # Cria o meteoro
    def criar_meteoro(self):
        numero_meteor = random.randint(1,3)
        y = random.randint(50, height - 50)
        big = self.nivel >= 6 and random.choice([True, False])
        if numero_meteor == 1:
            img = self.img_meteor_big if big else self.img_meteor
        else:
            img = self.img_meteor_big2 if big else self.img_meteor2
        m = self.canvas.create_image(width + 40, y, image=img, anchor='center')
        self.meteoros.append(m)
        # Conta o numero de meteoros no nivel final
        if self.final_round:
            self.meteor_count += 1

    # Cria a recarga de vida
    def criar_vida(self):
        y = random.randint(50, height - 50)
        v = self.canvas.create_image(width + 30, y, image=self.img_wrench, anchor='center')
        self.objetos_vida.append(v)

    # Movimento e Colisoes 
    def mover_planetas(self):
        speed = int(base_speed_planet * (1 + 0.25 * self.nivel))
        for planeta, label, nome in self.planetas[:]:
            self.canvas.move(planeta, -speed, 0)
            self.canvas.move(label, -speed, 0)
            x, y = self.canvas.coords(planeta)
            if x < -30:
                self.canvas.delete(planeta)
                self.canvas.delete(label)
                self.planetas.remove((planeta, label, nome))
            elif self.rede_ativa:
                rx, ry = self.canvas.coords(self.rede)
                if abs(rx - x) < 20 and abs(ry - y) < 20: # Quando apanha um planeta, apaga, increm pontos e reduz a dur da rede.
                    self.canvas.delete(planeta)
                    self.canvas.delete(label)
                    self.planetas.remove((planeta, label, nome))
                    self.pontuacao += 2
                    self.durabilidade_rede -= 1
                    self.atualizar_barra_durabilidade()
                    self.canvas.itemconfig(self.texto_pontuacao, text=f"Pontos: {self.pontuacao}")
                    self.som_captura.play()
                    if self.durabilidade_rede <= 0:
                        msg = self.canvas.create_text(width//2, height//2, text="Rede rasgada!", font=self.futuro_24, fill="yellow")
                        self.root.after(1000, lambda m=msg: self.canvas.delete(m))
                        self.recolher_rede()
                        self.som_rede.play()
                    if self.pontuacao % 10 == 0 and self.pontuacao < final_score: # Muda de nivel
                        self.nivel = min(self.pontuacao // 10, len(ordem_planetas) - 1)
                        self.canvas.itemconfig(self.texto_nivel, text=f"Nível: {self.nivel+1}")
                        idx = min(self.nivel // 2, len(self.bg_images) - 1)
                        self.canvas.itemconfig(self.bg_image_id, image=self.bg_images[idx])
                        self.som_next_level.play()

        for obj in self.objetos_recarga[:]:
            self.canvas.move(obj, -speed, 0)
            x, y = self.canvas.coords(obj)
            if x < -20: # Quando sai do mapa apaga
                self.canvas.delete(obj)
                self.objetos_recarga.remove(obj)
            else:
                nx, ny = self.canvas.coords(self.nave)
                if abs(nx - x) < 25 and abs(ny - y) < 25:
                    self.canvas.delete(obj)
                    self.objetos_recarga.remove(obj)
                    self.durabilidade_rede = max_durability
                    self.atualizar_barra_durabilidade()
                    self.som_reparar_nave.play()

        for meteoro in self.meteoros[:]:
            self.canvas.move(meteoro, -speed, 0)
            x, y = self.canvas.coords(meteoro)
            if x < -50: # Quando sai do mapa apaga
                self.canvas.delete(meteoro)
                self.meteoros.remove(meteoro)
            else:
                nx, ny = self.canvas.coords(self.nave)
                if abs(nx - x) < 40 and abs(ny - y) < 40:
                    self.canvas.delete(meteoro)
                    self.meteoros.remove(meteoro)
                    self.vidas -= 1
                    self.atualizar_barra_vida()
                    self.som_impacto.play()
                    if self.vidas <= 0:
                        self.som_game_over.play()
                        self.canvas.create_text(width//2, height//2, text="Game Over", font=self.futuro_40, fill="red")
                        self.canvas.create_text(width//2, height - 20, text="PAMD2005", fill="white", font=self.futuro_12 , anchor="s")
                        return

        for item in self.objetos_vida[:]:
            self.canvas.move(item, -speed, 0)
            x, y = self.canvas.coords(item)
            if x < -20: # Quando sai do mapa apaga
                self.canvas.delete(item)
                self.objetos_vida.remove(item)
            else:
                nx, ny = self.canvas.coords(self.nave)
                if abs(nx - x) < 30 and abs(ny - y) < 30:
                    self.canvas.delete(item)
                    self.objetos_vida.remove(item)
                    if self.vidas < max_vidas:
                        self.vidas += 1
                        self.atualizar_barra_vida()
                        self.som_reparar_nave.play()

    def atualizar_jogo(self):
        # Valida se estamos no nivel final
        if not self.final_round and self.pontuacao >= final_score:
            self.final_round = True
            bg6_path = os.path.join(self.img_path, 'bg_space_6.jpg')
            if os.path.exists(bg6_path):
                img6 = Image.open(bg6_path).resize((width, height), Image.LANCZOS)
                self.bg6_img = ImageTk.PhotoImage(img6) 
                self.canvas.itemconfig(self.bg_image_id, image=self.bg6_img)
            self.nivel_final_id = self.canvas.create_text(width//2, height//2, text="💫 Chuva de Asteroides 💫 \n Sobrevive.", fill="yellow", font=self.futuro_24, justify="center")
            # Buraco Negro
            if self.bh_img:
                self.bh_id = self.canvas.create_image(width - -295, height//2, image=self.bh_img, anchor='e')
            self.canvas.itemconfig(self.texto_nivel, text=" Nível: ???")
            # 3 Seg antes de começar o nivel final
            self.root.after(3000, lambda: (self.canvas.delete(self.nivel_final_id)))

        # No nivel final cria apenas meteoritos e vida
        if self.final_round:
            if random.randint(1, 2) == 1:
                self.criar_meteoro()
            if random.randint(1, 100) == 1:
                self.criar_vida()
            self.mover_planetas()
            if self.meteor_count >= 200:
                # Quando passam 200 meteoros acaba ojogo
                self.canvas.create_text(width//2, height//2, text="Vitória!", fill="white", font=self.futuro_40)
                self.canvas.create_text(width//2, height - 20, text="PAMD2005", fill="white", font=self.futuro_12 , anchor="s")
                self.som_victory.play()
                return
        else:
            # Spawn normal (antes do nivel final)
            if random.randint(1, 50) == 1:
                self.criar_recarga()
            chance = 20 if self.nivel < 6 else 10
            if random.randint(1, chance) == 1:
                self.criar_planeta()
            if self.nivel >= 4 and random.randint(1, 40) == 1:
                self.criar_meteoro()
            if self.nivel >= 4 and random.randint(1, 200) == 1:
                self.criar_vida()
            self.mover_planetas()

        # Continua o loop se ainda houver vidas e nao for vitoria
        if self.vidas > 0 and (not self.final_round or self.meteor_count < 200):
            self.root.after(100, self.atualizar_jogo)

    # Instrucoes Iniciais 
    def mostrar_instrucoes(self):
        instrucoes_texto = (
            "🌌 Nave OnLine!\n\n"
            "🕹️Controlos:\n"
            "  - Mover nave: <⭡ ⭠ ⭣ ⭢> ou <W A S D>\n"
            "  - Lançar/Recolher rede: <Espaço>\n\n"
            "🎯 Objetivo:\n"
            "  - Capturar planetas com a rede\n"
            "  - Evitar meteoros\n"
            "  - Não destruir a Nave\n\n"
            "🔁 Pressiona <ENTER> para começar...")
        self.instrucoes_id = self.canvas.create_text(width // 2, height // 2, text=instrucoes_texto, fill="white", font=self.futuro_16, justify="center")
        self.root.bind("<Return>", self.iniciar_jogo)

    def iniciar_jogo(self, event=None):
        # Sai das instrucoes e inicia o jogo
        self.canvas.delete(self.instrucoes_id)
        self.root.unbind("<Return>")
        self.atualizar_jogo()


# Começa o Jogo
root = tk.Tk() 
jogo = JogoNave(root) 
root.mainloop()
