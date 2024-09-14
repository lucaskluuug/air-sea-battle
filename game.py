import pygame
import random

pygame.init()

# Configurações da janela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Air-Sea Battle")

# Definições de cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (135, 206, 235)
DARK_GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)

clock = pygame.time.Clock()
FPS = 60

# Função para desenhar o fundo
def draw_background(screen):
    # Céu
    screen.fill(BLUE)

    # Nuvens
    pygame.draw.ellipse(screen, WHITE, (100, 50, 200, 100))
    pygame.draw.ellipse(screen, WHITE, (300, 80, 250, 120))
    pygame.draw.ellipse(screen, WHITE, (600, 60, 180, 90))

    # Montanhas
    pygame.draw.polygon(screen, DARK_GREEN, [(0, HEIGHT - 100), (200, HEIGHT - 300), (400, HEIGHT - 100)])
    pygame.draw.polygon(screen, DARK_GREEN, [(200, HEIGHT - 100), (400, HEIGHT - 300), (600, HEIGHT - 100)])
    
    # Grama
    pygame.draw.rect(screen, LIGHT_GREEN, (0, HEIGHT - 100, WIDTH, 100))

# Classe do Canhão Antiaéreo
class Cannon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 90  # Começa apontado para cima (90 graus)
        self.speed = 5  # Velocidade de movimentação horizontal
        self.projectile = None  # Sem projéteis no início
        self.last_angle_change = pygame.time.get_ticks()  # Última vez que o ângulo foi alterado
        self.angle_change_delay = 200  # Delay de 200ms entre mudanças de ângulo

    def draw(self, screen):
        # Desenha o canhão com base no ângulo
        pygame.draw.rect(screen, RED, (self.x, self.y, 20, 40))
        pygame.draw.line(screen, RED, (self.x + 10, self.y), 
                         (self.x + 10 + 30 * self.angle_vector()[0], 
                          self.y - 30 * self.angle_vector()[1]), 5)

    def move_horizontal(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed  # Move para a esquerda
        elif direction == "right" and self.x < WIDTH - 20:
            self.x += self.speed  # Move para a direita

    def adjust_angle(self, direction):
        current_time = pygame.time.get_ticks()
        # Verifica se já se passaram 200ms desde a última mudança de ângulo
        if current_time - self.last_angle_change > self.angle_change_delay:
            if direction == "up" and self.angle == 60:
                self.angle = 90  # Ajusta para cima
            elif direction == "up" and self.angle == 90:
                self.angle = 120  # Ajusta para a direita
            elif direction == "down" and self.angle == 120:
                self.angle = 90  # Ajusta para cima
            elif direction == "down" and self.angle == 90:
                self.angle = 60  # Ajusta para a esquerda
            self.last_angle_change = current_time

    def angle_vector(self):
        # Retorna o vetor de movimento baseado no ângulo atual
        if self.angle == 90:  # Direto para cima
            return (0, 1)
        elif self.angle == 60:  # Inclinado para a esquerda
            return (-1, 1)
        elif self.angle == 120:  # Inclinado para a direita
            return (1, 1)

    def shoot(self):
        if not self.projectile:  # Só dispara se não houver um projétil ativo
            self.projectile = Projectile(self.x + 10, self.y, self.angle_vector())

    def update(self):
        if self.projectile:
            self.projectile.update()
            if self.projectile.y < 0 or self.projectile.x < 0 or self.projectile.x > WIDTH:
                self.projectile = None  # Remove o projétil se ele sair da tela

# Classe de Projéteis
class Projectile:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 7
        self.radius = 6

    def update(self):
        self.x += self.direction[0] * self.speed
        self.y -= self.direction[1] * self.speed
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)

    def check_collision(self, airplanes):
        for airplane in airplanes:
            if (airplane.x < self.x < airplane.x + airplane.width) and \
               (airplane.y < self.y < airplane.y + airplane.height):
                airplanes.remove(airplane)  # Remove a aeronave
                return True, (self.x, self.y)  # Retorna a posição da colisão
        return False, None

# Classe dos Aviões
class Airplane:
    def __init__(self, x, y, speed, size):
        self.x = x
        self.y = y
        self.width, self.height = size
        self.speed = speed

        # Define o formato do losango
        self.shape = [
            (self.x + self.width // 2, self.y),
            (self.x + self.width, self.y + self.height // 2),
            (self.x + self.width // 2, self.y + self.height),
            (self.x, self.y + self.height // 2)
        ]

    def draw(self, screen):
        # Desenha a aeronave como um losango
        pygame.draw.polygon(screen, BLACK, self.shape)

    def update(self):
        self.x -= self.speed
        # Atualiza as coordenadas do losango com base na nova posição
        self.shape = [
            (self.x + self.width // 2, self.y),
            (self.x + self.width, self.y + self.height // 2),
            (self.x + self.width // 2, self.y + self.height),
            (self.x, self.y + self.height // 2)
        ]

# Classe da Frota de Aviões
class AirplaneFleet:
    def __init__(self):
        self.airplanes = []
        self.create_fleet()  # Cria a primeira frota

    def create_fleet(self):
        num_airplanes = random.randint(1, 5)  # Número aleatório de 1 a 5 aviões
        x = WIDTH  # Todos começam na borda direita da tela
        y = random.randint(50, 150)  # Posição inicial variável no eixo Y
        size = (80, 40) if random.random() < 0.5 else (60, 30)  # Tamanhos maiores para as naves

        # Definição da velocidade baseada no tamanho da nave
        speed = 3 if size == (80, 40) else 5

        # Definir o espaçamento entre as naves com base no tamanho
        vertical_spacing = 70 if size == (80, 40) else 50

        # Criar os aviões de acordo com o número sorteado
        for i in range(num_airplanes):
            airplane = Airplane(x, y + i * vertical_spacing, speed, size)  # Aviões alinhados verticalmente
            self.airplanes.append(airplane)

    def update(self):
        # Atualiza as aeronaves
        for airplane in self.airplanes:
            airplane.update()

        # Verifica se todas as aeronaves saíram da tela
        if all(airplane.x + airplane.width < 0 for airplane in self.airplanes):
            self.create_fleet()  # Cria uma nova frota se a anterior saiu da tela

    def draw(self, screen):
        for airplane in self.airplanes:
            airplane.draw(screen)

    def is_empty(self):
        return len(self.airplanes) == 0

# Função para desenhar o efeito de colisão
def draw_collision_effect(screen, position):
    pygame.draw.circle(screen, YELLOW, (int(position[0]), int(position[1])), 24)
    pygame.draw.circle(screen, RED, (int(position[0]), int(position[1])), 12)

def main():
    running = True
    cannon = Cannon(WIDTH // 2 - 10, HEIGHT - 50)
    fleet = AirplaneFleet()  # Inicia com uma frota de aviões
    score = 0  # Inicializa o placar

    while running:
        draw_background(screen)  # Desenha o fundo

        # Desenha o placar
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Controles do jogador
        keys = pygame.key.get_pressed()

        # Movimento horizontal do canhão
        if keys[pygame.K_LEFT]:
            cannon.move_horizontal("left")
        if keys[pygame.K_RIGHT]:
            cannon.move_horizontal("right")

        # Ajuste do ângulo do canhão
        if keys[pygame.K_UP]:
            cannon.adjust_angle("up")
        if keys[pygame.K_DOWN]:
            cannon.adjust_angle("down")

        # Disparo do canhão
        if keys[pygame.K_SPACE]:
            cannon.shoot()

        cannon.update()

        # Verifica colisões com projétil
        if cannon.projectile:
            collision, position = cannon.projectile.check_collision(fleet.airplanes)
            if collision:
                draw_collision_effect(screen, position)  # Desenha o efeito de colisão
                cannon.projectile = None  # Remove o projétil após colisão
                score += 1  # Incrementa o placar

        # Atualiza e desenha a frota de aviões
        fleet.update()
        fleet.draw(screen)

        # Desenha o canhão
        cannon.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()