import socket
import threading
import time

# --- 실시간 제어를 위한 설정 ---
REAL_TIME_SERVER_PORT = 25002 # Unity의 TCPClient.cs와 동일한 포트 사용
global_vibro_condition_met = False # Unity에서 수신할 상태를 저장할 변수
# ----------------------------

def parse_realtime_data(msg):
    """
    실시간 메시지를 파싱하여 딕셔너리 형태로 반환합니다.
    형식: vibroCondition:True
    """
    data = {}
    items = msg.strip().split(':', 1)
    if len(items) == 2:
        key, val = items
        if key == "vibroCondition":
            data[key] = val.strip().lower() == 'true'
    return data

def run_realtime_dummy_server():
    global global_vibro_condition_met
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('127.0.0.1', REAL_TIME_SERVER_PORT))
        server_socket.listen(1)
        print(f"Dummy Real-time Server listening for connection on port {REAL_TIME_SERVER_PORT}...")
        
        conn = None
        while True: # 클라이언트 연결 끊김 시 재연결 대기
            try:
                conn, addr = server_socket.accept()
                print(f"Client connected from {addr}")
                receive_buffer = ""
                
                while True: # 현재 클라이언트로부터 데이터 수신 루프
                    data_chunk = conn.recv(1024)
                    if not data_chunk:
                        print(f"Client {addr} disconnected.")
                        break # 현재 클라이언트 연결 종료
                    
                    receive_buffer += data_chunk.decode('utf-8')
                    
                    while '\n' in receive_buffer:
                        message_end_index = receive_buffer.find('\n')
                        full_message = receive_buffer[:message_end_index].strip()
                        receive_buffer = receive_buffer[message_end_index + 1:]

                        if not full_message:
                            continue

                        try:
                            parsed_data = parse_realtime_data(full_message)
                            if 'vibroCondition' in parsed_data:
                                global_vibro_condition_met = parsed_data['vibroCondition']
                                # 상태 변화가 있을 때만 출력하여 로그를 깔끔하게 유지
                                if global_vibro_condition_met:
                                    print(f"[{time.strftime('%H:%M:%S')}] Received vibroCondition: {global_vibro_condition_met}")
                                
                                conn.sendall(b"OK_RT_DUMMY\n") # Unity에 응답
                            else:
                                print(f"[{time.strftime('%H:%M:%S')}] Dummy server parse error: {full_message}")
                                conn.sendall(b"ERROR_RT_DUMMY\n") # Unity에 오류 응답
                        except Exception as e:
                            print(f"[{time.strftime('%H:%M:%S')}] Error processing message '{full_message}': {e}")
                            conn.sendall(b"ERROR_PROCESSING_DUMMY\n") # Unity에 처리 오류 응답
                    

            except ConnectionResetError:
                print(f"Client {addr} forcibly disconnected.")
            except BrokenPipeError:
                print(f"Broken pipe error with client {addr}.")
            except Exception as e:
                print(f"An unexpected error occurred in client handling: {e}")
            finally:
                if conn:
                    conn.close() # 클라이언트 소켓 닫기
                print("Waiting for new client connection...")
                # 연결이 끊어지면 다시 accept() 대기

    except Exception as e:
        print(f"Server socket initialization or binding error: {e}")
    finally:
        server_socket.close()
        print("Dummy Real-time Server shut down.")

if __name__ == "__main__":
    # 서버 스레드 시작
    server_thread = threading.Thread(target=run_realtime_dummy_server, daemon=True)
    server_thread.start()
    
    print("Dummy server is running. Press Enter to stop.")
    input() # 사용자가 Enter를 누르면 스크립트 종료 (데몬 스레드도 함께 종료)
    print("Stopping dummy server...")