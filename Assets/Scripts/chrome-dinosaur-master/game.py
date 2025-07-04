# import pygame
# import os
# import random
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

# global_vibro_condition_met = False

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

#         self.step_index = 0
#         self.jump_vel = self.JUMP_VEL
#         self.image = self.run_img[0]
#         self.dino_rect = self.image.get_rect()
#         self.dino_rect.x = self.X_POS
#         self.dino_rect.y = self.Y_POS

#     def update(self, userInput):
#         if self.dino_duck:
#             self.duck()
#         if self.dino_run:
#             self.run()
#         if self.dino_jump:
#             self.jump()

#         if self.step_index >= 10:
#             self.step_index = 0

#         if userInput[pygame.K_UP] and not self.dino_jump:
#             self.dino_duck = False
#             self.dino_run = False
#             self.dino_jump = True
#         elif userInput[pygame.K_DOWN] and not self.dino_jump:
#             self.dino_duck = True
#             self.dino_run = False
#             self.dino_jump = False
#         elif not (self.dino_jump or userInput[pygame.K_DOWN]):
#             self.dino_duck = False
#             self.dino_run = True
#             self.dino_jump = False

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
#         if self.dino_jump:
#             self.dino_rect.y -= self.jump_vel * 4
#             self.jump_vel -= 0.8
#         if self.jump_vel < - self.JUMP_VEL:
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


# def main():
#     global game_speed, x_pos_bg, y_pos_bg, points, obstacles
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
#         if points % 100 == 0:
#             game_speed += 1

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

#     while run:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 run = False

#         SCREEN.fill((255, 255, 255))
#         userInput = pygame.key.get_pressed()

#         player.draw(SCREEN)
#         player.update(userInput)

#         if len(obstacles) == 0:
#             if random.randint(0, 2) == 0:
#                 obstacles.append(SmallCactus(SMALL_CACTUS))
#             elif random.randint(0, 2) == 1:
#                 obstacles.append(LargeCactus(LARGE_CACTUS))
#             elif random.randint(0, 2) == 2:
#                 obstacles.append(Bird(BIRD))

#         for obstacle in obstacles:
#             obstacle.draw(SCREEN)
#             obstacle.update()
#             if player.dino_rect.colliderect(obstacle.rect):
#                 pygame.time.delay(2000)
#                 death_count += 1
#                 menu(death_count)

#         background()

#         cloud.draw(SCREEN)
#         cloud.update()

#         score()

#         clock.tick(30)
#         pygame.display.update()


# def menu(death_count):
#     global points
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
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 run = False
#             if event.type == pygame.KEYDOWN:
#                 main()


# menu(death_count=0)

# import pygame
# import os
# import random
# import threading
# import socket
# import time # 스레드에서 sleep 사용을 위해 추가

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

# # --- 실시간 제어를 위한 전역 변수 ---
# global_vibro_condition_met = False
# REAL_TIME_SERVER_PORT = 25002 # Unity에서 보낼 포트 번호와 일치해야 합니다.
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

#         self.step_index = 0
#         self.jump_vel = self.JUMP_VEL
#         self.image = self.run_img[0]
#         self.dino_rect = self.image.get_rect()
#         self.dino_rect.x = self.X_POS
#         self.dino_rect.y = self.Y_POS

#     def update(self, userInput, jump_triggered_by_vibro_condition=False): # 새로운 파라미터 추가
#         if self.dino_duck:
#             self.duck()
#         if self.dino_run:
#             self.run()
#         if self.dino_jump:
#             self.jump()

#         if self.step_index >= 10:
#             self.step_index = 0

#         # userInput[pygame.K_UP] 조건을 대신하거나 추가하여 사용
#         # jump_triggered_by_vibro_condition이 True이고, 현재 점프 중이 아니라면 점프 시작
#         if (userInput[pygame.K_UP] or jump_triggered_by_vibro_condition) and not self.dino_jump:
#             self.dino_duck = False
#             self.dino_run = False
#             self.dino_jump = True
#         # 아래로 숙이는 동작
#         elif userInput[pygame.K_DOWN] and not self.dino_jump:
#             self.dino_duck = True
#             self.dino_run = False
#             self.dino_jump = False
#         # 아무런 입력이 없고, 점프 중이 아닐 때 달리기 (dino_jump 상태와 vibro_condition이 활성 상태가 아닐 때)
#         elif not (self.dino_jump or userInput[pygame.K_DOWN] or jump_triggered_by_vibro_condition): 
#             self.dino_duck = False
#             self.dino_run = True
#             self.dino_jump = False

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
#         if self.dino_jump:
#             self.dino_rect.y -= self.jump_vel * 4
#             self.jump_vel -= 0.8
#         if self.jump_vel < - self.JUMP_VEL:
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

# # --- Real-time server for game control (새로 추가) ---
# def parse_realtime_data(msg):
#     """
#     실시간 메시지를 파싱하여 딕셔너리 형태로 반환합니다.
#     형식: vibroCondition:True
#     """
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
#     realtime_server_socket.bind(('127.0.0.1', REAL_TIME_SERVER_PORT)) # 새로운 포트
#     realtime_server_socket.listen(1)
#     print(f"Real-time server listening for connection on port {REAL_TIME_SERVER_PORT}...")
    
#     conn = None
#     try:
#         conn, addr = realtime_server_socket.accept()
#         print(f"Real-time client connected by {addr}")
#         receive_buffer = ""
#         while True:
#             try:
#                 data_chunk = conn.recv(1024)
#                 if not data_chunk:
#                     print("Real-time client disconnected.")
#                     break
                
#                 receive_buffer += data_chunk.decode('utf-8')
#                 while '\n' in receive_buffer:
#                     message_end_index = receive_buffer.find('\n')
#                     full_message = receive_buffer[:message_end_index].strip()
#                     receive_buffer = receive_buffer[message_end_index + 1:]

#                     if not full_message:
#                         continue

#                     parsed_rt = parse_realtime_data(full_message)
#                     if 'vibroCondition' in parsed_rt:
#                         global_vibro_condition_met = parsed_rt['vibroCondition']
#                         # Debugging: Uncomment to see real-time updates
#                         if global_vibro_condition_met:
#                             print(f"Real-time vibroCondition: {global_vibro_condition_met}")
#                         conn.sendall(b"OK_RT\n") # 간단한 응답
#                     else:
#                         print(f"Real-time parse error: {full_message}")
#                         conn.sendall(b"ERROR_RT\n")

#             except ConnectionResetError:
#                 print("Real-time client forcibly disconnected.")
#                 break
#             except BrokenPipeError:
#                 print("Real-time broken pipe error.")
#                 break
#             except Exception as e:
#                 print(f"Real-time server error: {e}")
#                 break
#     except Exception as e:
#         print(f"Real-time server socket init error: {e}")
#     finally:
#         if conn:
#             conn.close()
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
#         if points % 100 == 0:
#             game_speed += 1

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

#     # Flag to ensure jump is triggered only once per condition being met
#     # (Unity의 freezeConditionDetected와 유사한 역할)
#     jump_condition_already_met_in_current_frame = False 

#     while run:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 run = False

#         SCREEN.fill((255, 255, 255))
#         userInput = pygame.key.get_pressed()

#         # 실시간 vibroCondition 상태를 게임 입력으로 사용
#         jump_triggered_by_vibro_condition = False
#         # global_vibro_condition_met가 True이고, 공룡이 점프 중이 아니며,
#         # 이번 프레임에서 이미 vibro_condition으로 점프가 트리거되지 않았다면
#         if global_vibro_condition_met and not player.dino_jump and not jump_condition_already_met_in_current_frame:
#             jump_triggered_by_vibro_condition = True
#             jump_condition_already_met_in_current_frame = True # 이번 프레임에서 점프 트리거됨
#             print("Python Game: Jump triggered by Unity vibro condition!")
        
#         # global_vibro_condition_met가 False로 돌아오면 플래그 리셋
#         # 이는 다음 번 global_vibro_condition_met가 True가 될 때 다시 점프할 수 있도록 합니다.
#         if not global_vibro_condition_met:
#             jump_condition_already_met_in_current_frame = False


#         player.draw(SCREEN)
#         player.update(userInput, jump_triggered_by_vibro_condition) # 새로운 파라미터 전달

#         if len(obstacles) == 0:
#             if random.randint(0, 2) == 0:
#                 obstacles.append(SmallCactus(SMALL_CACTUS))
#             elif random.randint(0, 2) == 1:
#                 obstacles.append(LargeCactus(LARGE_CACTUS))
#             elif random.randint(0, 2) == 2:
#                 obstacles.append(Bird(BIRD))

#         for obstacle in obstacles:
#             obstacle.draw(SCREEN)
#             obstacle.update()
#             if player.dino_rect.colliderect(obstacle.rect):
#                 pygame.time.delay(2000)
#                 death_count += 1
#                 menu(death_count)

#         background()

#         cloud.draw(SCREEN)
#         cloud.update()

#         score()

#         clock.tick(30) # 게임 FPS 설정
#         pygame.display.update()


# def menu(death_count):
#     global points, global_vibro_condition_met # global_vibro_condition_met도 초기화
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
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 run = False
#             if event.type == pygame.KEYDOWN:
#                 global_vibro_condition_met = False # 게임 시작/재시작 시 초기화
#                 main()

# # --- 서버 스레드 시작 및 게임 실행 ---
# if __name__ == "__main__":
#     # 실시간 서버 스레드 시작
#     realtime_server_thread = threading.Thread(target=run_realtime_server, daemon=True)
#     realtime_server_thread.start()
    
#     # Pygame 게임 시작
#     menu(death_count=0) # 이 함수 내부에서 main()이 호출됨

#     # Pygame 종료 후 스레드 종료 대기 (daemon 스레드는 자동으로 종료됨)
#     print("Pygame application ended. Real-time server will shut down.")

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
#         self.is_jump_finished = True # NEW: 점프 완료 여부 트래킹

#         self.step_index = 0
#         self.jump_vel = self.JUMP_VEL
#         self.image = self.run_img[0]
#         self.dino_rect = self.image.get_rect()
#         self.dino_rect.x = self.X_POS
#         self.dino_rect.y = self.Y_POS

#     def update(self, userInput, jump_triggered_by_vibro_condition=False):
#         if self.dino_duck:
#             self.duck()
#         if self.dino_run:
#             self.run()
#         if self.dino_jump:
#             self.jump()
#             self.is_jump_finished = False # 점프 중이므로 완료 상태 아님
#         else:
#             self.is_jump_finished = True # 점프 중이 아니라면 완료 상태

#         if self.step_index >= 10:
#             self.step_index = 0

#         # userInput[pygame.K_UP] 조건을 대신하거나 추가하여 사용
#         if (userInput[pygame.K_UP] or jump_triggered_by_vibro_condition) and not self.dino_jump:
#             self.dino_duck = False
#             self.dino_run = False
#             self.dino_jump = True
#         elif userInput[pygame.K_DOWN] and not self.dino_jump:
#             self.dino_duck = True
#             self.dino_run = False
#             self.dino_jump = False
#         elif not (self.dino_jump or userInput[pygame.K_DOWN] or jump_triggered_by_vibro_condition): 
#             self.dino_duck = False
#             self.dino_run = True
#             self.dino_jump = False

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
#         if self.dino_jump:
#             self.dino_rect.y -= self.jump_vel * 4
#             self.jump_vel -= 0.8
#         if self.jump_vel < - self.JUMP_VEL:
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
#     realtime_server_socket.bind(('127.0.0.1', REAL_TIME_SERVER_PORT))
#     realtime_server_socket.listen(1)
#     print(f"Real-time server listening for connection on port {REAL_TIME_SERVER_PORT}...")
    
#     conn = None
#     try:
#         conn, addr = realtime_server_socket.accept()
#         print(f"Real-time client connected by {addr}")
#         receive_buffer = ""
#         while True:
#             try:
#                 data_chunk = conn.recv(1024)
#                 if not data_chunk:
#                     print("Real-time client disconnected.")
#                     break
                
#                 receive_buffer += data_chunk.decode('utf-8')
#                 while '\n' in receive_buffer:
#                     message_end_index = receive_buffer.find('\n')
#                     full_message = receive_buffer[:message_end_index].strip()
#                     receive_buffer = receive_buffer[message_end_index + 1:]

#                     if not full_message:
#                         continue

#                     parsed_rt = parse_realtime_data(full_message)
#                     if 'vibroCondition' in parsed_rt:
#                         global_vibro_condition_met = parsed_rt['vibroCondition']
#                         if global_vibro_condition_met:
#                             print(f"Real-time vibroCondition: {global_vibro_condition_met}") # 디버깅용
#                         conn.sendall(b"OK_RT\n") 
#                     else:
#                         print(f"Real-time parse error: {full_message}")
#                         conn.sendall(b"ERROR_RT\n")

#             except ConnectionResetError:
#                 print("Real-time client forcibly disconnected.")
#                 break
#             except BrokenPipeError:
#                 print("Real-time broken pipe error.")
#                 break
#             except Exception as e:
#                 print(f"Real-time server error: {e}")
#                 break
#     except Exception as e:
#         print(f"Real-time server socket init error: {e}")
#     finally:
#         if conn:
#             conn.close()
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
#         if points % 100 == 0:
#             game_speed += 1

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

#     # Flag to ensure jump is triggered only once per condition being met
#     # and then reset when the jump animation is finished.
#     jump_triggered_by_vibro_condition_in_current_frame = False # NEW: 현재 프레임에서 점프가 트리거되었는지
    
#     while run:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 run = False

#         SCREEN.fill((255, 255, 255))
#         userInput = pygame.key.get_pressed()

#         # 실시간 vibroCondition 상태를 게임 입력으로 사용
#         jump_should_be_triggered = False # NEW: 현재 프레임에서 점프가 되어야 하는지 (로직 최종 결과)

#         # 1. global_vibro_condition_met가 True이고, 공룡이 점프 중이 아니라면,
#         #    이번 프레임에서 점프를 트리거해야 함.
#         if global_vibro_condition_met and not player.dino_jump:
#             jump_should_be_triggered = True
            
#         # 2. 공룡의 점프 애니메이션이 끝나면, jump_triggered_by_vibro_condition_in_current_frame 플래그를 리셋
#         #    이렇게 해야 다음 번 vibro_condition_met 신호에 반응할 수 있음.
#         if player.is_jump_finished: # Dinosaur 클래스에 is_jump_finished 추가됨
#             jump_triggered_by_vibro_condition_in_current_frame = False

#         # 3. 최종적으로 점프를 player.update로 전달하기 전에,
#         #    이미 이전 vibro_condition으로 인해 점프가 트리거된 상태라면 (점프 애니메이션이 끝나지 않았다면),
#         #    새로운 vibro_condition 신호는 무시.
#         final_jump_input = jump_should_be_triggered and not jump_triggered_by_vibro_condition_in_current_frame
        
#         # 만약 final_jump_input이 True가 되면, jump_triggered_by_vibro_condition_in_current_frame을 True로 설정
#         if final_jump_input:
#             jump_triggered_by_vibro_condition_in_current_frame = True
#             print("Python Game: Jump triggered by Unity vibro condition!")

#         player.draw(SCREEN)
#         player.update(userInput, final_jump_input) # 새로운 파라미터 전달

#         if len(obstacles) == 0:
#             if random.randint(0, 2) == 0:
#                 obstacles.append(SmallCactus(SMALL_CACTUS))
#             elif random.randint(0, 2) == 1:
#                 obstacles.append(LargeCactus(LARGE_CACTUS))
#             elif random.randint(0, 2) == 2:
#                 obstacles.append(Bird(BIRD))

#         for obstacle in obstacles:
#             obstacle.draw(SCREEN)
#             obstacle.update()
#             if player.dino_rect.colliderect(obstacle.rect):
#                 pygame.time.delay(2000)
#                 death_count += 1
#                 menu(death_count)

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
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 run = False
#             if event.type == pygame.KEYDOWN:
#                 global_vibro_condition_met = False # 게임 시작/재시작 시 초기화
#                 main()

# # --- 서버 스레드 시작 및 게임 실행 ---
# if __name__ == "__main__":
#     # 실시간 서버 스레드 시작
#     realtime_server_thread = threading.Thread(target=run_realtime_server, daemon=True)
#     realtime_server_thread.start()
    
#     # Pygame 게임 시작
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
        self.is_jump_finished = True 

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
            self.is_jump_finished = False 
        else:
            self.is_jump_finished = True 

        if self.step_index >= 10:
            self.step_index = 0

        if (userInput[pygame.K_UP] or jump_triggered_by_vibro_condition) and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN] or jump_triggered_by_vibro_condition): 
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
                            print(f"Real-time vibroCondition: {global_vibro_condition_met}") # 디버깅용
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

    jump_triggered_by_vibro_condition_in_current_frame = False 
    
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        SCREEN.fill((255, 255, 255))
        userInput = pygame.key.get_pressed()

        jump_should_be_triggered = False 

        # if global_vibro_condition_met and not player.dino_jump:
        if global_vibro_condition_met and not player.dino_jump:
            jump_should_be_triggered = True
            
        if player.is_jump_finished: 
            jump_triggered_by_vibro_condition_in_current_frame = False

        final_jump_input = jump_should_be_triggered and not jump_triggered_by_vibro_condition_in_current_frame
        #print("not available: ",jump_triggered_by_vibro_condition_in_current_frame)
        if final_jump_input:
            jump_triggered_by_vibro_condition_in_current_frame = True
            print("Python Game: Jump triggered by Unity vibro condition!")

        player.draw(SCREEN)
        player.update(userInput, final_jump_input) 

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

        # Input handling for menu screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            # Check for ANY key press
            if event.type == pygame.KEYDOWN:
                global_vibro_condition_met = False # 게임 시작/재시작 시 초기화
                main()
                return # main()이 시작되면 menu 루프 종료
        
        # NEW: Check for global_vibro_condition_met to start the game
        if global_vibro_condition_met:
            print("Python Game: Starting game via vibro condition!")
            global_vibro_condition_met = False # 게임 시작 시 초기화
            main()
            return # main()이 시작되면 menu 루프 종료


# --- 서버 스레드 시작 및 게임 실행 ---
if __name__ == "__main__":
    realtime_server_thread = threading.Thread(target=run_realtime_server, daemon=True)
    realtime_server_thread.start()
    
    menu(death_count=0)

    print("Pygame application ended. Real-time server will shut down.")