import pygame
import os
import random
import threading
import socket
import time

pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

immortal = True
# --- 실시간 제어를 위한 전역 변수 ---
global_vibro_condition_met = False
REAL_TIME_SERVER_PORT = 25002 
# ------------------------------------

class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False
        # self.is_jump_finished = True  # 이 플래그는 더 이상 사용하지 않음

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    # jump_triggered_by_vibro_condition은 이제 매 프레임 Unity에서 온 신호 그대로
    def update(self, userInput, jump_triggered_by_vibro_condition): 
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()
            # self.is_jump_finished = False # 이 부분도 더 이상 필요 없음
        # else:
            # self.is_jump_finished = True # 이 부분도 더 이상 필요 없음

        if self.step_index >= 10:
            self.step_index = 0

        # === 핵심 변경: global_vibro_condition_met이 True이면 무조건 점프 상태로 진입 ===
        # 다른 모든 점프 관련 조건보다 최우선합니다.
        # userInput[pygame.K_UP]과 jump_triggered_by_vibro_condition 중 하나라도 True이면 점프
        # 단, dino_jump가 True일 때는 점프 로직이 jump() 메서드에서 계속 진행되므로 여기서 재설정할 필요 없음
        if jump_triggered_by_vibro_condition or userInput[pygame.K_UP]: 
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump: # 숙이기는 점프 중이 아닐 때만 가능
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        # 아무런 입력도 없고 (키보드 및 Unity 신호 모두), 점프 중이 아닐 때 달리기
        elif not (self.dino_jump or userInput[pygame.K_DOWN]): # 이 조건을 이전처럼 단순히 바꿈
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < - self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL
        print("I jump!!")

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 250
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index//5], self.rect)
        self.index += 1

# --- Real-time server for game control ---
def parse_realtime_data(msg):
    data = {}
    items = msg.strip().split(':', 1)
    if len(items) == 2:
        key, val = items
        if key == "vibroCondition":
            data[key] = val.strip().lower() == 'true'
    return data

def run_realtime_server():
    global global_vibro_condition_met
    realtime_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    realtime_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    realtime_server_socket.bind(('127.0.0.1', REAL_TIME_SERVER_PORT))
    realtime_server_socket.listen(1)
    print(f"Real-time server listening for connection on port {REAL_TIME_SERVER_PORT}...")
    
    conn = None
    try:
        conn, addr = realtime_server_socket.accept()
        print(f"Real-time client connected by {addr}")
        receive_buffer = ""
        while True:
            try:
                data_chunk = conn.recv(1024)
                if not data_chunk:
                    print("Real-time client disconnected.")
                    break
                
                receive_buffer += data_chunk.decode('utf-8')
                while '\n' in receive_buffer:
                    message_end_index = receive_buffer.find('\n')
                    full_message = receive_buffer[:message_end_index].strip()
                    receive_buffer = receive_buffer[message_end_index + 1:]

                    if not full_message:
                        continue

                    parsed_rt = parse_realtime_data(full_message)
                    if 'vibroCondition' in parsed_rt:
                        global_vibro_condition_met = parsed_rt['vibroCondition']
                        if(global_vibro_condition_met):
                            print(f"Real-time vibroCondition: {global_vibro_condition_met}") 
                        conn.sendall(b"OK_RT\n") 
                    else:
                        print(f"Real-time parse error: {full_message}")
                        conn.sendall(b"ERROR_RT\n")

            except ConnectionResetError:
                print("Real-time client forcibly disconnected.")
                break
            except BrokenPipeError:
                print("Real-time broken pipe error.")
                break
            except Exception as e:
                print(f"Real-time server error: {e}")
                break
    except Exception as e:
        print(f"Real-time server socket init error: {e}")
    finally:
        if conn:
            conn.close()
        realtime_server_socket.close()
        print("Real-time server shut down.")


def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, global_vibro_condition_met
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font('freesansbold.ttf', 20)
    obstacles = []
    death_count = 0

    def score():
        global points, game_speed
        points += 1
        #if points % 100 == 0: # 속도 증가 비활성화 (선택 사항)
            #game_speed += 1

        text = font.render("Points: " + str(points), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (1000, 40)
        SCREEN.blit(text, textRect)

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    # === 이 플래그와 관련된 모든 로직을 제거 ===
    # jump_triggered_by_vibro_condition_in_current_frame = False 
    
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        SCREEN.fill((255, 255, 255))
        userInput = pygame.key.get_pressed()

        # jump_should_be_triggered = False # 이 변수도 필요 없음

        # === 핵심 변경: global_vibro_condition_met 값을 player.update에 직접 전달 ===
        # 이 값이 True이면 Dinosaur의 update 메서드에서 무조건 점프를 시도합니다.
        jump_by_vibro_condition = global_vibro_condition_met
        
        # 디버깅: Unity 신호가 들어왔을 때만 출력
        if jump_by_vibro_condition: # 이제 점프 중 여부와 상관없이 출력
            print("Python Game: Jump triggered by Unity vibro condition!")

        # player.update에 userInput과 jump_by_vibro_condition을 전달
        player.draw(SCREEN)
        player.update(userInput, jump_by_vibro_condition) 

        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif random.randint(0, 2) == 2:
                obstacles.append(Bird(BIRD))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if not immortal:
                if player.dino_rect.colliderect(obstacle.rect):
                    pygame.time.delay(2000)
                    death_count += 1
                    menu(death_count)

        background()

        cloud.draw(SCREEN)
        cloud.update()

        score()

        clock.tick(30) 
        pygame.display.update()


def menu(death_count):
    global points, global_vibro_condition_met 
    run = True
    while run:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font('freesansbold.ttf', 30)

        if death_count == 0:
            text = font.render("Press any Key to Start", True, (0, 0, 0))
        elif death_count > 0:
            text = font.render("Press any Key to Restart", True, (0, 0, 0))
            score = font.render("Your Score: " + str(points), True, (0, 0, 0))
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score, scoreRect)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))
        pygame.display.update()

        # 메뉴 화면 입력 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            # 아무 키나 눌리면 게임 시작
            if event.type == pygame.K_DOWN:
                global_vibro_condition_met = False # 게임 시작/재시작 시 초기화
                main()
                return 
        
        # NEW: Check for global_vibro_condition_met to start the game
        if global_vibro_condition_met:
            print("Python Game: Starting game via vibro condition!")
            global_vibro_condition_met = False # 게임 시작 시 초기화
            main()
            return 


# --- 서버 스레드 시작 및 게임 실행 ---
if __name__ == "__main__":
    realtime_server_thread = threading.Thread(target=run_realtime_server, daemon=True)
    realtime_server_thread.start()
    
    menu(death_count=0)

    print("Pygame application ended. Real-time server will shut down.")