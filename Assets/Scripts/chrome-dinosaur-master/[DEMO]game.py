# import pygame
# import os
# import random
# import threading
# import socket
# import time

# pygame.init()

# # Global Constants
# SCREEN_HEIGHT = 600
# SCREEN_WIDTH = 1100
# SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
#            pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]
# JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
# DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
#            pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]

# SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
#                 pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
#                 pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
# LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
#                 pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
#                 pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

# BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
#         pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

# CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))

# BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

# immortal = True
# # --- 실시간 제어를 위한 전역 변수 ---
# global_vibro_condition_met = False
# REAL_TIME_SERVER_PORT = 25002 
# # ------------------------------------

# class Dinosaur:
#     X_POS = 80
#     Y_POS = 310
#     Y_POS_DUCK = 340
#     JUMP_VEL = 8.5

#     def __init__(self):
#         self.duck_img = DUCKING
#         self.run_img = RUNNING
#         self.jump_img = JUMPING

#         self.dino_duck = False
#         self.dino_run = True
#         self.dino_jump = False
#         # self.is_jump_finished = True  # 이 플래그는 더 이상 사용하지 않음

#         self.step_index = 0
#         self.jump_vel = self.JUMP_VEL
#         self.image = self.run_img[0]
#         self.dino_rect = self.image.get_rect()
#         self.dino_rect.x = self.X_POS
#         self.dino_rect.y = self.Y_POS

#     # jump_triggered_by_vibro_condition은 이제 매 프레임 Unity에서 온 신호 그대로
#     def update(self, userInput, jump_triggered_by_vibro_condition): 
#         # Debugging: Dinosaur.update 시작 시 현재 상태 출력
#         # print(f"Dino.update: dino_jump={self.dino_jump}, jump_vel={self.jump_vel:.2f}, "
#         #       f"vibro_cond={jump_triggered_by_vibro_condition}, K_UP={userInput[pygame.K_UP]}")

#         if self.dino_duck:
#             self.duck()
#         if self.dino_run:
#             self.run()
#         if self.dino_jump:
#             self.jump()
        
#         if self.step_index >= 10:
#             self.step_index = 0

#         # === 핵심 변경: global_vibro_condition_met이 True이면 무조건 점프 상태로 진입 ===
#         # 다른 모든 점프 관련 조건보다 최우선합니다.
#         # userInput[pygame.K_UP]과 jump_triggered_by_vibro_condition 중 하나라도 True이면 점프
#         # 단, dino_jump가 True일 때는 점프 로직이 jump() 메서드에서 계속 진행되므로 여기서 재설정할 필요 없음
        
#         # 디버깅: 점프 조건 진입 전 상태 확인
#         if jump_triggered_by_vibro_condition or userInput[pygame.K_UP]:
#             if not self.dino_jump: # 실제로 점프 상태가 아닐 때 점프 시작을 알림
#                 if jump_triggered_by_vibro_condition:
#                     print(f"Dino.update: JUMPING due to vibro_condition (current dino_jump: {self.dino_jump})")
#                 elif userInput[pygame.K_UP]:
#                     print(f"Dino.update: JUMPING due to K_UP (current dino_jump: {self.dino_jump})")
#             # 점프 상태로 전환
#             self.dino_duck = False
#             self.dino_run = False
#             self.dino_jump = True
#         elif userInput[pygame.K_DOWN]: # 숙이기는 점프 중이 아닐 때만 가능
#             if not self.dino_jump: # 점프 중이 아닐 때만 숙이도록 함
#                 print(f"Dino.update: DUCKING due to K_DOWN (current dino_jump: {self.dino_jump})")
#                 self.dino_duck = True
#                 self.dino_run = False
#                 self.dino_jump = False
#             else:
#                 print(f"Dino.update: DUCKING BLOCKED (dino_jump is {self.dino_jump})")
#         # 아무런 입력도 없고 (키보드 및 Unity 신호 모두), 점프 중이 아닐 때 달리기
#         # 이곳의 조건은 '점프가 아니고 숙이기도 아닐 때' 달리기로 설정
#         elif not (self.dino_jump or self.dino_duck): 
#             if not self.dino_run: # 달리기 상태가 아닐 때만 출력
#                 print(f"Dino.update: RUNNING (no jump/duck input, dino_jump:{self.dino_jump}, dino_duck:{self.dino_duck})")
#             self.dino_duck = False
#             self.dino_run = True
#             self.dino_jump = False
#         # 디버깅: 어떤 상태에도 해당하지 않을 때 (예: 점프 중인데 다른 입력이 들어오거나, 숙이기 중인 경우)
#         else:
#             # 이 else는 위에 명시된 조건들 (점프, 숙이기, 달리기) 외의 경우를 처리
#             # 예를 들어, 점프 중인데 DOWN 키가 눌린 경우 등
#             pass # print가 너무 많아질 수 있으므로 일단 비워둠

#     def duck(self):
#         self.image = self.duck_img[self.step_index // 5]
#         self.dino_rect = self.image.get_rect()
#         self.dino_rect.x = self.X_POS
#         self.dino_rect.y = self.Y_POS_DUCK
#         self.step_index += 1

#     def run(self):
#         self.image = self.run_img[self.step_index // 5]
#         self.dino_rect = self.image.get_rect()
#         self.dino_rect.x = self.X_POS
#         self.dino_rect.y = self.Y_POS
#         self.step_index += 1

#     def jump(self):
#         self.image = self.jump_img
#         if self.dino_jump: # dino_jump가 True일 때만 점프 로직 수행
#             self.dino_rect.y -= self.jump_vel * 4
#             self.jump_vel -= 0.8
#         # 디버깅: 점프 속도가 음수가 되어 하강 중일 때
#         # if self.jump_vel < 0 and self.dino_jump:
#         #     print(f"Dino.jump: Currently falling, jump_vel={self.jump_vel:.2f}")

#         if self.jump_vel < - self.JUMP_VEL: # 하강 속도가 초기 점프 속도 절대값을 초과하면 착지
#             print(f"Dino.jump: LANDED! Resetting jump_vel. (old dino_jump: {self.dino_jump})")
#             self.dino_jump = False
#             self.jump_vel = self.JUMP_VEL
        
#     def draw(self, SCREEN):
#         SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


# class Cloud:
#     def __init__(self):
#         self.x = SCREEN_WIDTH + random.randint(800, 1000)
#         self.y = random.randint(50, 100)
#         self.image = CLOUD
#         self.width = self.image.get_width()

#     def update(self):
#         self.x -= game_speed
#         if self.x < -self.width:
#             self.x = SCREEN_WIDTH + random.randint(2500, 3000)
#             self.y = random.randint(50, 100)

#     def draw(self, SCREEN):
#         SCREEN.blit(self.image, (self.x, self.y))


# class Obstacle:
#     def __init__(self, image, type):
#         self.image = image
#         self.type = type
#         self.rect = self.image[self.type].get_rect()
#         self.rect.x = SCREEN_WIDTH

#     def update(self):
#         self.rect.x -= game_speed
#         if self.rect.x < -self.rect.width:
#             obstacles.pop()

#     def draw(self, SCREEN):
#         SCREEN.blit(self.image[self.type], self.rect)


# class SmallCactus(Obstacle):
#     def __init__(self, image):
#         self.type = random.randint(0, 2)
#         super().__init__(image, self.type)
#         self.rect.y = 325


# class LargeCactus(Obstacle):
#     def __init__(self, image):
#         self.type = random.randint(0, 2)
#         super().__init__(image, self.type)
#         self.rect.y = 300


# class Bird(Obstacle):
#     def __init__(self, image):
#         self.type = 0
#         super().__init__(image, self.type)
#         self.rect.y = 250
#         self.index = 0

#     def draw(self, SCREEN):
#         if self.index >= 9:
#             self.index = 0
#         SCREEN.blit(self.image[self.index//5], self.rect)
#         self.index += 1

# # --- Real-time server for game control ---
# def parse_realtime_data(msg):
#     data = {}
#     items = msg.strip().split(':', 1)
#     if len(items) == 2:
#         key, val = items
#         if key == "vibroCondition":
#             data[key] = val.strip().lower() == 'true'
#     return data

# def run_realtime_server():
#     global global_vibro_condition_met
#     realtime_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     realtime_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
#     try: # 서버 소켓 바인딩 및 리스닝 관련 예외 처리 강화
#         realtime_server_socket.bind(('127.0.0.1', REAL_TIME_SERVER_PORT))
#         realtime_server_socket.listen(1)
#         print(f"Real-time server listening for connection on port {REAL_TIME_SERVER_PORT}...")
        
#         conn = None
#         while True: # 클라이언트 연결 끊김 시 재연결 대기
#             try:
#                 conn, addr = realtime_server_socket.accept()
#                 print(f"Real-time client connected by {addr}")
#                 receive_buffer = ""
                
#                 while True: # 현재 클라이언트로부터 데이터 수신 루프
#                     data_chunk = conn.recv(1024)
#                     if not data_chunk:
#                         print(f"Real-time client {addr} disconnected.")
#                         break # 현재 클라이언트 연결 종료
                    
#                     receive_buffer += data_chunk.decode('utf-8')
                    
#                     while '\n' in receive_buffer:
#                         message_end_index = receive_buffer.find('\n')
#                         full_message = receive_buffer[:message_end_index].strip()
#                         receive_buffer = receive_buffer[message_end_index + 1:]

#                         if not full_message:
#                             continue

#                         try:
#                             parsed_rt = parse_realtime_data(full_message)
#                             if 'vibroCondition' in parsed_rt:
#                                 # Debugging: 수신된 vibroCondition 상태와 global_vibro_condition_met 변경 여부
#                                 if global_vibro_condition_met != parsed_rt['vibroCondition']:
#                                     print(f"Real-time: global_vibro_condition_met changed from {global_vibro_condition_met} to {parsed_rt['vibroCondition']}")
#                                 global_vibro_condition_met = parsed_rt['vibroCondition']
#                                 # if(global_vibro_condition_met): # True일 때만 출력하도록 유지
#                                 #     print(f"Real-time vibroCondition: {global_vibro_condition_met}") 
#                                 conn.sendall(b"OK_RT\n") 
#                             else:
#                                 print(f"Real-time parse error: {full_message}")
#                                 conn.sendall(b"ERROR_RT\n")

#                         except Exception as e:
#                             print(f"Error processing message '{full_message}': {e}")
#                             conn.sendall(b"ERROR_PROCESSING_RT\n")
                    
#             except ConnectionResetError:
#                 print(f"Real-time client {addr} forcibly disconnected.")
#             except BrokenPipeError:
#                 print(f"Broken pipe error with client {addr}.")
#             except Exception as e:
#                 print(f"An unexpected error occurred in real-time client handling: {e}")
#             finally:
#                 if conn:
#                     conn.close() # 클라이언트 소켓 닫기
#                 print("Waiting for new real-time client connection...")
#                 # 연결이 끊어지면 다시 accept() 대기

#     except Exception as e:
#         print(f"Server socket initialization or binding error: {e}")
#     finally:
#         realtime_server_socket.close()
#         print("Real-time server shut down.")


# def main():
#     global game_speed, x_pos_bg, y_pos_bg, points, obstacles, global_vibro_condition_met
#     run = True
#     clock = pygame.time.Clock()
#     player = Dinosaur()
#     cloud = Cloud()
#     game_speed = 20
#     x_pos_bg = 0
#     y_pos_bg = 380
#     points = 0
#     font = pygame.font.Font('freesansbold.ttf', 20)
#     obstacles = []
#     death_count = 0

#     def score():
#         global points, game_speed
#         points += 1
#         #if points % 100 == 0: # 속도 증가 비활성화 (선택 사항)
#             #game_speed += 1

#         text = font.render("Points: " + str(points), True, (0, 0, 0))
#         textRect = text.get_rect()
#         textRect.center = (1000, 40)
#         SCREEN.blit(text, textRect)

#     def background():
#         global x_pos_bg, y_pos_bg
#         image_width = BG.get_width()
#         SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
#         SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
#         if x_pos_bg <= -image_width:
#             SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
#             x_pos_bg = 0
#         x_pos_bg -= game_speed

#     # 이전의 점프 제어 플래그는 더 이상 필요 없음
#     # jump_triggered_by_vibro_condition_in_current_frame = False 
    
#     while run:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 run = False

#         SCREEN.fill((255, 255, 255))
#         userInput = pygame.key.get_pressed()

#         # === 핵심 변경: global_vibro_condition_met을 player.update에 직접 전달 ===
#         # 이 값이 True이면 Dinosaur의 update 메서드에서 무조건 점프를 시도합니다.
#         jump_by_vibro_condition = global_vibro_condition_met
        
#         # 디버깅: Unity 신호가 들어왔을 때만 출력
#         # print(f"Main Loop: Passing jump_by_vibro_condition={jump_by_vibro_condition} to player.update")
#         if jump_by_vibro_condition: # 점프가 트리거될 가능성이 있는 경우에만 출력
#              print(f"Main Loop: Global vibro condition is TRUE. Attempting jump.")

#         player.draw(SCREEN)
#         player.update(userInput, jump_by_vibro_condition) 

#         if len(obstacles) == 0:
#             if random.randint(0, 2) == 0:
#                 obstacles.append(SmallCactus(SMALL_CACTUS))
#             elif random.randint(0, 2) == 1:
#                 obstacles.append(LargeCactus(LARGE_CACTUS))
#             elif random.randint(0, 2) == 2:
#                 obstacles.append(Bird(BIRD)) # Bird 클래스 생성자에 이미지 전달

#         for obstacle in obstacles:
#             obstacle.draw(SCREEN)
#             obstacle.update()
#             if not immortal:
#                 if player.dino_rect.colliderect(obstacle.rect):
#                     pygame.time.delay(2000)
#                     death_count += 1
#                     menu(death_count)

#         background()

#         cloud.draw(SCREEN)
#         cloud.update()

#         score()

#         clock.tick(30) 
#         pygame.display.update()


# def menu(death_count):
#     global points, global_vibro_condition_met 
#     run = True
#     while run:
#         SCREEN.fill((255, 255, 255))
#         font = pygame.font.Font('freesansbold.ttf', 30)

#         if death_count == 0:
#             text = font.render("Press any Key to Start", True, (0, 0, 0))
#         elif death_count > 0:
#             text = font.render("Press any Key to Restart", True, (0, 0, 0))
#             score = font.render("Your Score: " + str(points), True, (0, 0, 0))
#             scoreRect = score.get_rect()
#             scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
#             SCREEN.blit(score, scoreRect)
#         textRect = text.get_rect()
#         textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
#         SCREEN.blit(text, textRect)
#         SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))
#         pygame.display.update()

#         # 메뉴 화면 입력 처리
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 run = False
#             # Check for ANY key press
#             if event.type == pygame.K_DOWN: # K_DOWN으로 변경되어 있었으나, 보통은 K_SPACE나 아무 키 입력 사용
#                 global_vibro_condition_met = False # 게임 시작/재시작 시 초기화
#                 print("Menu: Keyboard input detected. Starting game.")
#                 main()
#                 return 
        
#         # NEW: Check for global_vibro_condition_met to start the game
#         if global_vibro_condition_met:
#             print("Menu: Unity vibro condition detected. Starting game.")
#             global_vibro_condition_met = False # 게임 시작 시 초기화
#             main()
#             return 


# # --- 서버 스레드 시작 및 게임 실행 ---
# if __name__ == "__main__":
#     realtime_server_thread = threading.Thread(target=run_realtime_server, daemon=True)
#     realtime_server_thread.start()
    
#     menu(death_count=0)

#     print("Pygame application ended. Real-time server will shut down.")

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
# NEW: global_vibro_condition_met이 True가 된 마지막 시간
last_vibro_true_time = 0 
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

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput, jump_triggered_by_vibro_condition): 
        # === NEW DEBUGGING: update 메서드 진입 시점의 상세 상태 ===
        # 각 프레임마다 호출되므로, 점프 관련 주요 변수들의 현재 상태를 확인
        # print(f"[Dino.update START] "
        #       f"dino_jump:{self.dino_jump}, jump_vel:{self.jump_vel:.2f}, "
        #       f"vibro_input:{jump_triggered_by_vibro_condition}, K_UP_input:{userInput[pygame.K_UP]}")
        # ==========================================================

        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()
        
        if self.step_index >= 10:
            self.step_index = 0

        # === 핵심 변경: global_vibro_condition_met이 True이면 무조건 점프 상태로 진입 ===
        if jump_triggered_by_vibro_condition or userInput[pygame.K_UP]: 
            # 디버깅: 점프 상태 진입 시 현재 dino_jump 상태와 입력 소스 확인
            if not self.dino_jump: # 실제로 점프 상태가 아니었다가 점프 상태로 진입할 때만 출력
                if jump_triggered_by_vibro_condition:
                    print(f"[Dino.update JUMP_INIT] Triggered by vibro_condition. dino_jump was False.")
                elif userInput[pygame.K_UP]:
                    print(f"[Dino.update JUMP_INIT] Triggered by K_UP. dino_jump was False.")
            # 점프 상태로 전환
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN]: 
            if not self.dino_jump: # 점프 중이 아닐 때만 숙이도록 함
                print(f"[Dino.update DUCK_INIT] DUCKING due to K_DOWN.")
                self.dino_duck = True
                self.dino_run = False
                self.dino_jump = False
            # else:
            #     print(f"[Dino.update DUCK_BLOCKED] K_DOWN ignored (dino_jump is {self.dino_jump})")
        elif not (self.dino_jump or self.dino_duck): 
            # 디버깅: 달리기 상태 진입 시 (점프/숙이기가 아닐 때)
            if not self.dino_run: # 달리기 상태가 아니었다가 달리기 상태로 진입할 때만 출력
                print(f"[Dino.update RUN_INIT] RUNNING (no jump/duck input).")
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False
        # else:
        #     # 이 경우는 현재 점프 중이거나 숙이기 중인데 다른 입력이 없거나 무시된 경우.
        #     # print(f"[Dino.update NO_STATE_CHANGE] Current state: Jump={self.dino_jump}, Duck={self.dino_duck}, Run={self.dino_run}")
        #     pass

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
            # 디버깅: 착지 시점
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
    def __init__(self, image): # 생성자에 image 파라미터 추가
        self.type = 0
        super().__init__(image, self.type) # BIRD 이미지를 전달받도록 수정
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
    global global_vibro_condition_met, last_vibro_true_time # NEW: last_vibro_true_time 사용
    realtime_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    realtime_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try: 
        realtime_server_socket.bind(('127.0.0.1', REAL_TIME_SERVER_PORT))
        realtime_server_socket.listen(1)
        print(f"Real-time server listening for connection on port {REAL_TIME_SERVER_PORT}...")
        
        conn = None
        while True: 
            try:
                conn, addr = realtime_server_socket.accept()
                print(f"Real-time client connected by {addr}")
                receive_buffer = ""
                
                while True: 
                    data_chunk = conn.recv(1024)
                    if not data_chunk:
                        print(f"Real-time client {addr} disconnected.")
                        break 
                    
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
                                # Debugging: 수신된 vibroCondition 상태와 global_vibro_condition_met 변경 여부
                                if global_vibro_condition_met != parsed_rt['vibroCondition']:
                                    print(f"[RT Server] global_vibro_condition_met changed from {global_vibro_condition_met} to {parsed_rt['vibroCondition']}")
                                
                                global_vibro_condition_met = parsed_rt['vibroCondition']
                                
                                # NEW: global_vibro_condition_met이 True가 된 시점 기록
                                if global_vibro_condition_met:
                                    last_vibro_true_time = time.time()
                                    # print(f"[RT Server] last_vibro_true_time set to {last_vibro_true_time:.4f}")

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
                    conn.close() 
                print("Waiting for new real-time client connection...")

    except Exception as e:
        print(f"Server socket initialization or binding error: {e}")
    finally:
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
        #if points % 100 == 0: 
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
    
    # NEW: 마지막 프레임의 global_vibro_condition_met 상태를 저장
    previous_global_vibro_condition_met = False

    while run:
        current_frame_time = time.time() # NEW: 현재 프레임 시간 기록

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        SCREEN.fill((255, 255, 255))
        userInput = pygame.key.get_pressed()

        jump_by_vibro_condition = global_vibro_condition_met
        
        # === NEW DEBUGGING: 메인 루프 시작 시점의 상세 상태 ===
        # 이전 프레임과 현재 프레임의 global_vibro_condition_met 변화 감지
        if jump_by_vibro_condition and not previous_global_vibro_condition_met:
            time_since_true = current_frame_time - last_vibro_true_time if last_vibro_true_time > 0 else -1
            print(f"[Main Loop START] VIBRO_TRUE_CHANGE! global_vibro_condition_met:{global_vibro_condition_met}, "
                  f"Time since RT server saw True: {time_since_true:.4f}s. "
                  f"Player dino_jump:{player.dino_jump}")
        elif not jump_by_vibro_condition and previous_global_vibro_condition_met:
            print(f"[Main Loop START] VIBRO_FALSE_CHANGE! global_vibro_condition_met:{global_vibro_condition_met}.")
        # ======================================================

        # player.update에 userInput과 jump_by_vibro_condition을 전달
        player.draw(SCREEN)
        player.update(userInput, jump_by_vibro_condition) 

        # NEW: 현재 프레임의 global_vibro_condition_met 상태를 다음 프레임을 위해 저장
        previous_global_vibro_condition_met = global_vibro_condition_met

        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif random.randint(0, 2) == 2:
                obstacles.append(Bird(BIRD)) # Bird 클래스 생성자에 이미지 전달

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

        # NEW: FPS와 현재 프레임 시간 로깅
        # print(f"FPS: {clock.get_fps():.1f}, Frame Duration: {(time.time() - current_frame_time)*1000:.2f}ms")
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
                last_vibro_true_time = 0 # NEW: 초기화
                print("Menu: Keyboard input detected. Starting game.")
                main()
                return 
        
        if global_vibro_condition_met:
            print("Menu: Unity vibro condition detected. Starting game.")
            global_vibro_condition_met = False 
            last_vibro_true_time = 0 # NEW: 초기화
            main()
            return 


# --- 서버 스레드 시작 및 게임 실행 ---
if __name__ == "__main__":
    realtime_server_thread = threading.Thread(target=run_realtime_server, daemon=True)
    realtime_server_thread.start()
    
    menu(death_count=0)

    print("Pygame application ended. Real-time server will shut down.")