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

immortal = False
# --- 실시간 제어를 위한 전역 변수 ---
global_vibro_condition_met = False
last_vibro_true_time = 0 
REAL_TIME_SERVER_PORT = 25002 
# ------------------------------------

class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 9.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput, jump_triggered_by_vibro_condition): 
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()
        
        if self.step_index >= 10:
            self.step_index = 0

        if jump_triggered_by_vibro_condition or userInput[pygame.K_UP]: 
            if not self.dino_jump:
                if jump_triggered_by_vibro_condition:
                    print(f"[Dino.update JUMP_INIT] Triggered by vibro_condition. dino_jump was False.")
                elif userInput[pygame.K_UP]:
                    print(f"[Dino.update JUMP_INIT] Triggered by K_UP. dino_jump was False.")
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN]: 
            if not self.dino_jump:
                print(f"[Dino.update DUCK_INIT] DUCKING due to K_DOWN.")
                self.dino_duck = True
                self.dino_run = False
                self.dino_jump = False
        elif not (self.dino_jump or self.dino_duck): 
            if not self.dino_run:
                print(f"[Dino.update RUN_INIT] RUNNING (no jump/duck input).")
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
            print(f"[Dino.jump LANDED] dino_jump was {self.dino_jump}. Resetting jump_vel.")
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL
        
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
    global global_vibro_condition_met, last_vibro_true_time
    realtime_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    realtime_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try: 
        realtime_server_socket.bind(('127.0.0.1', REAL_TIME_SERVER_PORT))
        realtime_server_socket.listen(1)
        print(f"Real-time server listening for connection on port {REAL_TIME_SERVER_PORT}...")
        
        # 외부 루프: 클라이언트 연결을 계속 기다림
        while True: 
            conn = None # 연결 객체 초기화
            try:
                conn, addr = realtime_server_socket.accept()
                print(f"Real-time client connected by {addr}")
                receive_buffer = "" # 새 연결마다 버퍼 초기화
                
                # 내부 루프: 현재 클라이언트로부터 데이터를 지속적으로 받음
                while True: 
                    data_chunk = conn.recv(1024)
                    if not data_chunk:
                        print(f"Real-time client {addr} disconnected.")
                        break # 현재 클라이언트와의 데이터 수신 루프 종료
                    
                    receive_buffer += data_chunk.decode('utf-8')
                    
                    while '\n' in receive_buffer:
                        message_end_index = receive_buffer.find('\n')
                        full_message = receive_buffer[:message_end_index].strip()
                        receive_buffer = receive_buffer[message_end_index + 1:]

                        if not full_message:
                            continue

                        try:
                            parsed_rt = parse_realtime_data(full_message)
                            if 'vibroCondition' in parsed_rt:
                                if global_vibro_condition_met != parsed_rt['vibroCondition']:
                                    print(f"[RT Server] global_vibro_condition_met changed from {global_vibro_condition_met} to {parsed_rt['vibroCondition']}")
                                
                                global_vibro_condition_met = parsed_rt['vibroCondition']
                                
                                if global_vibro_condition_met:
                                    last_vibro_true_time = time.time()

                                conn.sendall(b"OK_RT\n") 
                            else:
                                print(f"[RT Server] Parse error: {full_message}")
                                conn.sendall(b"ERROR_RT\n")

                        except Exception as e:
                            print(f"[RT Server] Error processing message '{full_message}': {e}")
                            conn.sendall(b"ERROR_PROCESSING_RT\n")
                    
            except ConnectionResetError:
                print(f"Real-time client {addr} forcibly disconnected.")
            except BrokenPipeError:
                print(f"Broken pipe error with client {addr}.")
            except Exception as e:
                print(f"An unexpected error occurred in real-time client handling: {e}")
            finally:
                if conn:
                    conn.close() # 현재 클라이언트 연결 종료
                    conn = None # conn을 None으로 설정하여 다음 accept() 시도를 보장
                time.sleep(1) # 재연결 시도 전 잠시 대기

    except Exception as e:
        print(f"Server socket initialization or binding error: {e}. Server will shut down.")
    finally:
        if realtime_server_socket: # 서버 소켓이 유효한 경우에만 닫기
            realtime_server_socket.close()
        print("Real-time server shut down.")


def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, global_vibro_condition_met, last_vibro_true_time
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
        if points % 100 == 0: 
            game_speed += 1

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
    
    previous_global_vibro_condition_met = False

    while run:
        current_frame_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        SCREEN.fill((255, 255, 255))
        userInput = pygame.key.get_pressed()

        jump_by_vibro_condition = global_vibro_condition_met
        
        if jump_by_vibro_condition and not previous_global_vibro_condition_met:
            time_since_true = current_frame_time - last_vibro_true_time if last_vibro_true_time > 0 else -1
            print(f"[Main Loop START] VIBRO_TRUE_CHANGE! global_vibro_condition_met:{global_vibro_condition_met}, "
                  f"Time since RT server saw True: {time_since_true:.4f}s. "
                  f"Player dino_jump:{player.dino_jump}")
        elif not jump_by_vibro_condition and previous_global_vibro_condition_met:
            print(f"[Main Loop START] VIBRO_FALSE_CHANGE! global_vibro_condition_met:{global_vibro_condition_met}.")

        player.draw(SCREEN)
        player.update(userInput, jump_by_vibro_condition) 

        previous_global_vibro_condition_met = global_vibro_condition_met

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
    global points, global_vibro_condition_met, last_vibro_true_time
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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.K_DOWN: 
                global_vibro_condition_met = False 
                last_vibro_true_time = 0 
                print("Menu: Keyboard input detected. Starting game.")
                main()
                return 
        
        if global_vibro_condition_met:
            print("Menu: Unity vibro condition detected. Starting game.")
            global_vibro_condition_met = False 
            last_vibro_true_time = 0 
            main()
            return 


# --- 서버 스레드 시작 및 게임 실행 ---
if __name__ == "__main__":
    realtime_server_thread = threading.Thread(target=run_realtime_server, daemon=True)
    realtime_server_thread.start()
    
    menu(death_count=0)

    print("Pygame application ended. Real-time server will shut down.")