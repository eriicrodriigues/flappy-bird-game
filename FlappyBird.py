import pygame
from pygame import image, transform, font
import os
import random

pygame.font.init()

TELA_LARGURA = 500
TELA_ALTURA = 800

IMAGEM_CANO = transform.scale2x(image.load(os.path.join('imgs', 'pipe.png')))
IMAGEM_CHAO = transform.scale2x(image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = transform.scale2x(image.load(os.path.join('imgs', 'bg.png')))
IMAGEM_START = transform.scale(image.load(os.path.join('imgs', 'start.png')), (200, 100))

IMAGENS_PASSARO = [
    transform.scale2x(image.load(os.path.join('imgs', 'bird1.png'))),
    transform.scale2x(image.load(os.path.join('imgs', 'bird2.png'))),
    transform.scale2x(image.load(os.path.join('imgs', 'bird3.png')))
]

FONTE_PONTOS = font.Font('font\\flappybird.ttf', 50)

ARQUIVO_PONTUACAO = "melhor_pontuacao.txt"

class Passaro:
    IMGS = IMAGENS_PASSARO
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO*4 +1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0

        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO*2

        imagem_rotacionada = transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)


class Cano:
    DISTANCIA = 200
    VELOCIDADE = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False


class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


def desenhar_tela(tela, passaros, canos, chao, pontos, jogo_iniciado):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    if not jogo_iniciado:
        tela.blit(IMAGEM_START, ((TELA_LARGURA - IMAGEM_START.get_width()) // 2, TELA_ALTURA // 2 - 50))
    else:
        for passaro in passaros:
            passaro.desenhar(tela)
        for cano in canos:
            cano.desenhar(tela)

        texto = FONTE_PONTOS.render(f"{pontos}", 1, (0, 0, 0))
        pos_x_texto = TELA_LARGURA // 2 - texto.get_width() // 2
        tela.blit(texto, (pos_x_texto, 0))
        chao.desenhar(tela)
    pygame.display.update()


def carregar_melhor_pontuacao():
    if os.path.exists(ARQUIVO_PONTUACAO):
        with open('melhor_pontuacao.txt', 'r') as file:
            melhor_pontuacao = int(file.read().strip())
        return melhor_pontuacao
    else:
        return 0


def salvar_melhor_pontuacao(pontuacao, melhor_pontuacao):
    with open('melhor_pontuacao.txt', 'w') as file:
        file.write(str(melhor_pontuacao))


def main():
    passaros = [Passaro(230, 350)]
    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    melhor_pontuacao = 0
    relogio = pygame.time.Clock()
    game_over = False
    jogo_iniciado = False
    melhor_pontuacao = carregar_melhor_pontuacao()

    while not game_over:
        relogio.tick(30)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    jogo_iniciado = True
                    for passaro in passaros:
                        passaro.pular()

        if jogo_iniciado:
            for passaro in passaros:
                passaro.mover()
            chao.mover()

            adicionar_cano = False
            remover_canos = []
            for cano in canos:
                for i, passaro in enumerate(passaros):
                    if cano.colidir(passaro):
                        game_over = True
                        if pontos > melhor_pontuacao:
                            melhor_pontuacao = pontos
                            salvar_melhor_pontuacao(pontos, melhor_pontuacao)
                    if not cano.passou and passaro.x > cano.x:
                        cano.passou = True
                        adicionar_cano = True
                cano.mover()
                if cano.x + cano.CANO_TOPO.get_width() < 0:
                    remover_canos.append(cano)

            if adicionar_cano:
                pontos += 1
                canos.append(Cano(600))
            for cano in remover_canos:
                canos.remove(cano)

            for i, passaro in enumerate(passaros):
                if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                    game_over = True
                    if pontos > melhor_pontuacao:
                        melhor_pontuacao = pontos

        desenhar_tela(tela, passaros, canos, chao, pontos, jogo_iniciado)

    # Tela de "Game Over"
    fonte_game_over = font.Font('font\\flappybird.ttf', 30)
    cor_texto = (255, 0, 0)
    texto_game_over_preto = fonte_game_over.render('GAME OVER', True, (0, 0, 0))
    texto_game_over = fonte_game_over.render('GAME OVER', True, cor_texto)
    largura_texto = texto_game_over.get_width()
    altura_texto = texto_game_over.get_height()
    posicao_x = TELA_LARGURA // 2 - largura_texto // 2
    posicao_y = TELA_ALTURA // 3 - altura_texto // 2
    tela.blit(texto_game_over_preto, (posicao_x + 2, posicao_y + 2))
    tela.blit(texto_game_over, (posicao_x, posicao_y))

    fonte_pontuacao = font.Font('font\\flappybird.ttf', 25)
    cor_texto_pontuacao = (255, 255, 255)
    texto_pontuacao_preto = fonte_pontuacao.render(f'PONTOS   {pontos}', True, (0, 0, 0))
    texto_pontuacao = fonte_pontuacao.render(f'PONTOS   {pontos}', True, cor_texto_pontuacao)
    largura_texto_pontuacao = texto_pontuacao.get_width()
    altura_texto_pontuacao = texto_pontuacao.get_height()
    posicao_x_pontuacao = TELA_LARGURA // 2 - largura_texto_pontuacao // 2
    posicao_y_pontuacao = TELA_ALTURA // 2 - altura_texto_pontuacao // 2
    tela.blit(texto_pontuacao_preto, (posicao_x_pontuacao + 2, posicao_y_pontuacao + 2))
    tela.blit(texto_pontuacao, (posicao_x_pontuacao, posicao_y_pontuacao))

    texto_melhor_pontuacao = fonte_pontuacao.render(f'MELHOR  {melhor_pontuacao}', True, (255, 255, 255))
    texto_melhor_pontuacao_preto = fonte_pontuacao.render(f'MELHOR  {melhor_pontuacao}', True, (0, 0, 0))
    largura_texto_melhor_pontuacao = texto_melhor_pontuacao.get_width()
    altura_texto_melhor_pontuacao = texto_melhor_pontuacao.get_height()
    posicao_x_melhor_pontuacao = TELA_LARGURA // 2 - largura_texto_melhor_pontuacao // 2
    posicao_y_melhor_pontuacao = TELA_ALTURA // 2 + 50 - altura_texto_melhor_pontuacao // 2
    tela.blit(texto_melhor_pontuacao_preto, (posicao_x_melhor_pontuacao + 2, posicao_y_melhor_pontuacao + 2))
    tela.blit(texto_melhor_pontuacao, (posicao_x_melhor_pontuacao, posicao_y_melhor_pontuacao))

    pygame.display.update()

    # Loop de reinício
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    main()


if __name__ == '__main__':
    main()
