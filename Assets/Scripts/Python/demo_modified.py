

# --- Constants for Button Visualization ---
CONTACT_Z = 0.0645
BOTTOM_OUT_Z = 0.1293
# ------------------------------------------
import socket
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
import pandas as pd
import datetime
import ast
import numpy as np
import os
import threading

# --- Configuration for Trial Success ---
# index_z가 최소한 넘어야 하는 값 (0보다 커야 함)
MIN_INDEX_Z_THRESHOLD = 0.0 
# ---------------------------------------

# 데이터 저장용
trial_indexZ = []
trial_metadata = {}

# 에피소드 관련 변수 추가
TRIALS_PER_EPISODE = 15 # 한 에피소드당 trial 수 (조정 가능)
current_episode_trial_count = 0 # 현재 에피소드에서 진행된 trial 수
episode_maxZs = [] # 현재 에피소드의 maxZ 값들을 저장할 리스트
episode_errors = [] # 현재 에피소드의 error 값들을 저장할 리스트
episode_impacts = [] # 에피소드별 impact 값들을 저장할 리스트 (데이터 기록용)
current_episode_start_impact = 0.0 # 에피소드 시작 시점의 impact_position

episode_data = [] # 에피소드 통계 데이터를 저장할 리스트
# current_feedback_type을 초기화할 때, 이전 값을 추적할 변수 추가
current_feedback_type = "UNKNOWN" # 현재 피드백 타입을 저장할 변수 (초기값)
last_processed_feedback_type = "UNKNOWN" # 마지막으로 처리된 피드백 타입을 저장할 변수


trial_history = [] # 각 trial의 (indexZ_list, metadata) 튜플을 저장

BASE_SAVE_DIR = "demo_data_fixed_session"  # 고정된 저장 폴더 이름
FEEDBACK_SUBDIRS = {
    "OnlyVisual": "0.Visual",
    "OnlyVibrotactile_fixed": "1.Vibrotactile(fixed)",
    "OnlyVibrotactile_adaptive": "2.Vibrotactile(adaptive)",
    "VisualwithVibrotactile_fixed": "3.Visual&Vibrotactile(fixed)",
    "VisualwithVibrotactile_adaptive": "4.Visual&Vibrotactile(adaptive)"
}
# --------------------------------------------------

# 서브플롯 생성: 1행 3열로 구성
fig, axs = plt.subplots(1, 3, figsize=(20, 7)) # figsize도 조정
fig.suptitle('Button Press demo Dashboard', fontsize=16)


# --- axs[0]: 개별 Trial의 Index Z 변화 (현재 Trial) ---
ax1 = axs[0] # Adjusted index for 1x3 subplot
line, = ax1.plot([], [], 'o-', label='Index Z')
maxZ_marker = ax1.axhline(0, color='darkred', linestyle='--', label='Max Z')
impact_marker = ax1.axhline(0, color='green', linestyle='-',linewidth = 2,  label='Vib trigger')
# Re-add Contact, Bottom Out, and Button Press Zone
contact_line_ax1 = ax1.axhline(CONTACT_Z, color='blue', linestyle='-', linewidth=3,label=f'Contact ({CONTACT_Z}m)')
bottom_out_line_ax1 = ax1.axhline(BOTTOM_OUT_Z, color='red', linestyle='-', linewidth=3,label=f'Bottom Out ({BOTTOM_OUT_Z}m)')
button_press_zone_ax1 = ax1.axhspan(CONTACT_Z, BOTTOM_OUT_Z, color='lightgray', alpha=0.3, label='Button Press Zone')
trial_info_text = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, verticalalignment='top')
ax1.legend()
ax1.set_title('Real-time Index Z per Trial (Current)') # Reverted title
ax1.set_xlabel("Time Step")
ax1.set_ylabel("Index Z Position (m)") # Reverted label
ax1.grid(True)


# --- axs[1]: Episode별 MaxZ 평균 및 분산 ---
ax2 = axs[1] # Adjusted index for 1x3 subplot
episode_means_line, = ax2.plot([], [], 'b-o', label='Mean MaxZ')
episode_stds_line, = ax2.plot([], [], 'r--x', label='Std Dev MaxZ')
episode_maxz_text_box = ax2.text(0.02, 0.95, '', transform=ax2.transAxes, verticalalignment='top')
ax2.legend()
ax2.set_title(f'Episode Statistics: MaxZ (Trials per Episode: {TRIALS_PER_EPISODE})')
ax2.set_xlabel("Episode Number")
ax2.set_ylabel("Max Z Value (m)")
contact_line_ax2 = ax2.axhline(CONTACT_Z, color='blue', linestyle='-', linewidth=3, label=f'Contact ({CONTACT_Z}m)')
bottom_out_line_ax2 = ax2.axhline(BOTTOM_OUT_Z, color='red', linestyle='-', linewidth=3, label=f'Bottom Out ({BOTTOM_OUT_Z}m)')
ax2.axhspan(CONTACT_Z, BOTTOM_OUT_Z, color='lightgray', alpha=0.3, label='Button Press Zone')

ax2.grid(True)


# --- NEW: axs[2]: Episode별 Target Impact Position ---
ax5 = axs[2] # Adjusted index for 1x3 subplot
episode_initial_impact_line, = ax5.plot([], [], 'k-o', label='Vib Feedback Trigger Pos Updated')
episode_impact_text_box = ax5.text(0.02, 0.95, '', transform=ax5.transAxes, verticalalignment='top')
ax5.legend()
ax5.set_title(f'Episode Statistics: Vibrotactile Trigger Position (Trials per Episode: {TRIALS_PER_EPISODE})')
ax5.set_xlabel("Episode Number")
ax5.set_ylabel("Impact Position (m)")
contact_line_ax5 = ax5.axhline(CONTACT_Z, color='blue', linestyle='-', linewidth=3, label=f'Contact ({CONTACT_Z}m)')
bottom_out_line_ax5 = ax5.axhline(BOTTOM_OUT_Z, color='red', linestyle='-', linewidth=3, label=f'Bottom Out ({BOTTOM_OUT_Z}m)')
ax5.axhspan(CONTACT_Z, BOTTOM_OUT_Z, color='lightgray', alpha=0.3, label='Button Press Zone')
ax5.grid(True)


def parse_data(msg):
    """
    수신된 메시지를 파싱하여 딕셔너리 형태로 반환합니다.
    형식: trial:1|indexZs:[0.1,0.2]|maxZ:0.3|impact:0.1|error:0.2|feedbackType:OnlyVisual
    """
    data = {}
    items = msg.strip().split('|')
    for item in items:
        try:
            key, val = item.split(':', 1)
            if key == "indexZs":
                data[key] = ast.literal_eval(val)
            elif key == "feedbackType":
                data[key] = val.strip()
            else:
                data[key] = float(val)
        except ValueError as ve:
            print(f"Parse Error (ValueError): {ve} in message part '{item}' from full message: '{msg}'")
            raise
        except IndexError as ie:
            print(f"Parse Error (IndexError): {ie} in message part '{item}' from full message: '{msg}'")
            raise
        except Exception as e:
            print(f"Parse Error (General): {e} from message part '{item}' from full message: '{msg}')")
            raise
    return data

def get_save_path(feedback_type, file_type, trial_info=None):
    """
    주어진 feedback_type과 file_type에 따라 데이터를 저장할 올바른 경로를 반환합니다.
    """
    global BASE_SAVE_DIR, FEEDBACK_SUBDIRS
    
    if not BASE_SAVE_DIR:
        raise Exception("BASE_SAVE_DIR (user name folder) is not set.")

    subdir_name = FEEDBACK_SUBDIRS.get(feedback_type, "UnknownFeedbackType")
    
    type_specific_dir = os.path.join(BASE_SAVE_DIR, subdir_name, file_type)

    if not os.path.exists(type_specific_dir):
        os.makedirs(type_specific_dir)

    if file_type == "trials" and trial_info:
        filename = f'trial_{int(trial_info["trial"]):03d}_{datetime.datetime.now().strftime("%H%M%S")}.csv'
    elif file_type == "episode_stats" and trial_info:
        filename = f'episode_data_ep{trial_info["episode_num"]:03d}_{feedback_type}_{datetime.datetime.now().strftime("%H%M%S")}.csv'
    else:
        raise ValueError(f"Invalid file_type: {file_type} or missing trial_info for it.")
        
    return os.path.join(type_specific_dir, filename)

def save_trial(indexZ_list, metadata):
    """
    개별 trial 데이터를 현재 세션 폴더에 저장합니다.
    """
    df = pd.DataFrame({'index_z': indexZ_list})
    for key in ['trial', 'maxZ', 'impact', 'error']:
        df[key] = metadata[key]
    df['feedbackType'] = metadata.get('feedbackType', 'UNKNOWN')
    
    filepath = get_save_path(metadata.get('feedbackType', 'UNKNOWN'), "trials", metadata)
    df.to_csv(filepath, index=False)

def save_episode_data(episode_num, data, feedback_type):
    """
    에피소드 통계 데이터를 현재 세션 폴더에 저장합니다.
    """
    filepath = get_save_path(feedback_type, "episode_stats", {"episode_num": episode_num})
    df = pd.DataFrame([data])
    df.to_csv(filepath, index=False)
    print(f"[Saved Episode Data] {filepath}")


def update_plot(frame):
    global trial_indexZ, trial_metadata, current_episode_trial_count, \
           episode_maxZs, episode_errors, episode_data, current_feedback_type, \
           trial_history, episode_impacts, current_episode_start_impact

    # --- axs[0]: 개별 Trial의 Index Z 변화 업데이트 (현재 Trial) ---
    if trial_indexZ and trial_metadata and 'maxZ' in trial_metadata and 'impact' in trial_metadata:
        x = list(range(len(trial_indexZ)))
        y = trial_indexZ
        line.set_data(x, y)
        ax1.set_xlim(0, max(10, len(x)))
        ax1.set_ylim(CONTACT_Z - 0.005, BOTTOM_OUT_Z + 0.005) 

        maxZ_marker.set_ydata([trial_metadata['maxZ']])
        impact_marker.set_ydata([trial_metadata['impact']])
        
        trial_info_text.set_text(f"Trial {int(trial_metadata['trial'])} ({current_episode_trial_count}/{TRIALS_PER_EPISODE})\n"
                                 f"Error: {trial_metadata['error']:.5f}")
    else:
        line.set_data([], [])
        maxZ_marker.set_ydata([0]) 
        impact_marker.set_ydata([0]) 
        trial_info_text.set_text("No current trial data")
        ax1.set_xlim(0, 10)
        ax1.set_ylim(CONTACT_Z - 0.005, BOTTOM_OUT_Z + 0.005)


    if episode_data:
        episode_numbers = [d['episode_num'] for d in episode_data]
        
        # MaxZ 통계
        episode_means = [d['mean_maxZ'] for d in episode_data]
        episode_stds = [d['std_maxZ'] for d in episode_data]
        episode_means_line.set_data(episode_numbers, episode_means)
        episode_stds_line.set_data(episode_numbers, episode_stds)
        
        all_max_z_values = [m for d in episode_data for m in d.get('all_maxZs_in_episode', [])]
        if all_max_z_values:
            min_y2 = min(all_max_z_values) - 0.02
            max_y2 = max(all_max_z_values) + 0.02
            if abs(max_y2 - min_y2) < 0.01:
                center = (min_y2 + max_y2) / 2
                min_y2 = center - 0.005
                max_y2 = center + 0.005
            ax2.set_ylim(min_y2, max_y2)
        else:
            ax2.set_ylim(0, 0.3)
        ax2.set_xlim(-0.5, max(episode_numbers) + 0.5 if episode_numbers else 0.5)

        # 가장 최근 에피소드의 MaxZ 통계 표시
        latest_episode_num = episode_data[-1]['episode_num']
        latest_maxz_mean = episode_data[-1]['mean_maxZ']
        latest_maxz_std = episode_data[-1]['std_maxZ'] # 여기에 오타가 있었습니다.
        episode_maxz_text_box.set_text(f"Ep {latest_episode_num}\nMean: {latest_maxz_mean:.5f}\nStd Dev: {latest_maxz_std:.5f}") # 수정된 부분

        
        # NEW: Target Impact Position 통계
        episode_initial_impacts = [d['initial_impact_position'] for d in episode_data]
        episode_initial_impact_line.set_data(episode_numbers, episode_initial_impacts)
        
        if episode_initial_impacts:
            min_y5 = min(episode_initial_impacts) - 0.02
            max_y5 = max(episode_initial_impacts) + 0.02
            if abs(max_y5 - min_y5) < 0.01:
                center = (min_y5 + max_y5) / 2
                min_y5 = center - 0.005
                max_y5 = center + 0.005
            ax5.set_ylim(min_y5, max_y5)
        else:
            ax5.set_ylim(0, 0.2)
        ax5.set_xlim(-0.5, max(episode_numbers) + 0.5 if episode_numbers else 0.5)

        # 가장 최근 에피소드의 Target Impact Position 통계 표시
        latest_initial_impact = episode_data[-1]['initial_impact_position']
        episode_impact_text_box.set_text(f"Ep {latest_episode_num}\nTarget: {latest_initial_impact:.5f}")

    else:
        episode_means_line.set_data([], [])
        episode_stds_line.set_data([], [])
        episode_maxz_text_box.set_text("No episode data")
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 0.3)
        
        episode_initial_impact_line.set_data([], [])
        episode_impact_text_box.set_text("No episode data")
        ax5.set_xlim(0, 1)
        ax5.set_ylim(0, 0.2)


    return line, maxZ_marker, impact_marker, contact_line_ax1, bottom_out_line_ax1, button_press_zone_ax1, trial_info_text, \
           episode_means_line, episode_stds_line, episode_maxz_text_box, \
           episode_initial_impact_line, episode_impact_text_box


def on_key_press(event):
    """
    키보드 이벤트를 처리하여 이전 trial 데이터를 삭제합니다.
    """
    global trial_indexZ, trial_metadata, \
           current_episode_trial_count, episode_maxZs, episode_errors, trial_history, \
           episode_impacts, current_episode_start_impact

    if event.key == 'backspace' or event.key == 'delete':
        print(f"Key '{event.key}' pressed. Attempting to undo last trial.")
        
        if not trial_history:
            print("No trials in history to undo.")
            return

        removed_trial_indexZ, removed_trial_metadata = trial_history.pop()

        if episode_maxZs and episode_errors and episode_impacts and current_episode_trial_count > 0:
            if np.isclose(episode_maxZs[-1], removed_trial_metadata['maxZ']) and \
               np.isclose(episode_errors[-1], removed_trial_metadata['error']) and \
               np.isclose(episode_impacts[-1], removed_trial_metadata['impact']):
                
                episode_maxZs.pop()
                episode_errors.pop()
                episode_impacts.pop()
                current_episode_trial_count -= 1
                print(f"Last trial (Trial {int(removed_trial_metadata['trial'])}) removed from episode data.")
            else:
                 print(f"Warning: Removed trial {int(removed_trial_metadata['trial'])} from history, but it did not match last episode data entry. Episode data might be out of sync. (This might happen if a trial was discarded in Python but was not the very last one added to episode_maxZs/errors, or if the episode just completed.)")
        else:
            print("No episode data to remove from.")

        # 현재 표시되는 trial 데이터를 업데이트 (이전 trial 표시는 없음)
        if trial_history:
            trial_indexZ, trial_metadata = trial_history[-1]
            # current_episode_start_impact는 에피소드 단위로 관리되므로, 트라이얼 언두 시 여기서 직접 재설정하지 않습니다.
            # reset_episode_and_trial_data()에서 피드백 타입 변경 시 에피소드 전체가 초기화됩니다.
        else: # trial_history가 비었으면 모두 비움
            trial_indexZ = []
            trial_metadata = {}
            current_episode_start_impact = 0.0 # 모든 트라이얼이 취소되면 에피소드 시작 임팩트도 초기화

        # 그래프 업데이트 강제
        fig.canvas.draw_idle()
        print("Plot updated after undo operation.")


def reset_episode_and_trial_data():
    """
    에피소드 및 트라이얼 관련 데이터를 초기화합니다.
    feedbackType이 변경될 때 호출됩니다.
    """
    global current_episode_trial_count, episode_maxZs, episode_errors, \
           episode_impacts, episode_data, trial_history, \
           trial_indexZ, trial_metadata, \
           current_episode_start_impact

    current_episode_trial_count = 0
    episode_maxZs = []
    episode_errors = []
    episode_impacts = []
    episode_data = []
    trial_history = []
    
    trial_indexZ = []
    trial_metadata = {}
    current_episode_start_impact = 0.0

    print("Episode and trial data has been reset due to feedback type change.")


def run_server_session():
    """
    단일 서버 세션을 실행하고, 클라이언트 연결이 끊겨도 자동으로 재연결을 시도합니다.
    """
    global trial_indexZ, trial_metadata, current_episode_trial_count, \
           episode_maxZs, episode_errors, episode_data, current_feedback_type, \
           trial_history, episode_impacts, current_episode_start_impact, BASE_SAVE_DIR, last_processed_feedback_type

    
    # 초기 디렉토리 설정은 서버 스레드가 시작될 때 한 번만 수행
    os.makedirs(BASE_SAVE_DIR, exist_ok=True)
    print(f"모든 데이터는 다음 위치에 저장됩니다: {BASE_SAVE_DIR}")

    for subdir in FEEDBACK_SUBDIRS.values():
        os.makedirs(os.path.join(BASE_SAVE_DIR, subdir, "trials"), exist_ok=True)
        os.makedirs(os.path.join(BASE_SAVE_DIR, subdir, "episode_stats"), exist_ok=True)
    print("피드백 타입별 폴더 구조를 생성했습니다.")

    # 서버 소켓 생성 및 바인딩, 리스닝은 함수 호출 시 한 번만 수행
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('127.0.0.1', 25001))
        server_socket.listen(1)
        print("Listening for connections on port 25001...")

        # 클라이언트 연결을 기다리는 외부 루프 (지속적인 재연결 시도)
        while True: 
            conn = None 
            try:
                conn, addr = server_socket.accept()
                print(f"Connected by {addr}")
                receive_buffer = "" # 새 클라이언트 연결마다 버퍼 초기화
                
                # --- 클라이언트 연결 시 트라이얼 관련 변수 초기화 ---
                # 주의: feedbackType이 바뀌면 reset_episode_and_trial_data()에서 전체 초기화 됨.
                # 연결이 끊겼다가 붙을 때만 reset을 원하면 이 위치에서 초기화
                # 현재 feedbackType 및 last_processed_feedback_type을 UNKNOWN으로 재설정
                # 이렇게 해야 다음 데이터 수신 시 feedbackType 변경 감지 로직이 정상 작동
                # 이 변수들은 전역으로 선언되어야 합니다. (이미 함수 상단 global에 선언됨)
                current_feedback_type = "UNKNOWN" 
                last_processed_feedback_type = "UNKNOWN"
                # 트라이얼 데이터는 유지 (재연결 시 초기화하지 않음)

                # 현재 클라이언트로부터 데이터를 받는 내부 루프
                while True: 
                    data_chunk = conn.recv(4096)
                    if not data_chunk:
                        print(f"Client {addr} disconnected. Waiting for new connection...")
                        break # 현재 클라이언트와의 데이터 수신 루프 종료
                    
                    receive_buffer += data_chunk.decode('utf-8')

                    while '\n' in receive_buffer:
                        message_end_index = receive_buffer.find('\n')
                        full_message = receive_buffer[:message_end_index].strip()
                        receive_buffer = receive_buffer[message_end_index + 1:]

                        if not full_message:
                            continue

                        try:
                            parsed = parse_data(full_message)

                            new_feedback_type = parsed.get('feedbackType', 'UNKNOWN')
                            # feedbackType 변경 시에만 초기화
                            if new_feedback_type != last_processed_feedback_type and last_processed_feedback_type != "UNKNOWN":
                                print(f"Feedback Type changed from '{last_processed_feedback_type}' to '{new_feedback_type}'. Resetting episode and trial counts.")
                                reset_episode_and_trial_data() # 이 함수에서 모든 트라이얼 데이터 초기화
                                current_feedback_type = new_feedback_type
                                last_processed_feedback_type = new_feedback_type
                            # 첫 데이터 수신 시 feedbackType 설정
                            elif last_processed_feedback_type == "UNKNOWN":
                                current_feedback_type = new_feedback_type
                                last_processed_feedback_type = new_feedback_type
                            
                            # Capture impact at episode start
                            if current_episode_trial_count == 0:
                                current_episode_start_impact = parsed['impact'] 


                            if not any(z > MIN_INDEX_Z_THRESHOLD for z in parsed['indexZs']):
                                print(f"Trial {int(parsed['trial'])} discarded: Index Z never went above {MIN_INDEX_Z_THRESHOLD} (did not register button press).")
                                conn.sendall(b"OK_DISCARDED_NO_PRESS")
                                continue

                            calculated_maxZ = max(parsed['indexZs'])

                            trial_metadata_for_processing = {
                                'trial': parsed['trial'],
                                'indexZs': parsed['indexZs'],
                                'maxZ': calculated_maxZ,
                                'impact': parsed['impact'],
                                'error': calculated_maxZ - parsed['impact'],
                                'feedbackType': new_feedback_type
                            }

                            trial_indexZ = trial_metadata_for_processing['indexZs']
                            trial_metadata = trial_metadata_for_processing

                            trial_history.append((list(trial_indexZ), dict(trial_metadata)))

                            save_trial(trial_indexZ, trial_metadata)

                            episode_maxZs.append(trial_metadata['maxZ'])
                            episode_errors.append(trial_metadata['error'])
                            episode_impacts.append(trial_metadata['impact']) # 데이터 기록용으로 유지
                            current_episode_trial_count += 1

                            if current_episode_trial_count >= TRIALS_PER_EPISODE:
                                mean_maxZ = np.mean(episode_maxZs)
                                std_maxZ = np.std(episode_maxZs)

                                mean_error = np.mean(episode_errors)
                                std_error = np.std(episode_errors)

                                episode_num = len(episode_data) + 1

                                episode_entry = {
                                    'episode_num': episode_num,
                                    'feedback_type': current_feedback_type,
                                    'mean_maxZ': mean_maxZ,
                                    'std_maxZ': std_maxZ,
                                    'all_maxZs_in_episode': list(episode_maxZs),
                                    'mean_error': mean_error,
                                    'std_error': std_error,
                                    'initial_impact_position': current_episode_start_impact, # 에피소드 시작 시의 impact 값
                                    'all_impacts_in_episode': list(episode_impacts) # 기록용
                                }
                                episode_data.append(episode_entry)

                                save_episode_data(episode_num, episode_entry, current_feedback_type)

                                print(f"\n--- Episode {episode_num} Completed ({current_feedback_type}) ---")
                                print(f"MaxZ - Mean: {mean_maxZ:.5f}, Std Dev: {std_maxZ:.5f}")
                                print(f"Error - Mean: {mean_error:.5f}, Std Dev: {std_error:.5f}")
                                print(f"Impact - Target: {current_episode_start_impact:.5f}\n")                   

                                conn.sendall(b"EPISODE_COMPLETED_NO_OPTIMIZER")

                                episode_maxZs = []
                                episode_errors = []
                                episode_impacts = []
                                current_episode_trial_count = 0

                            else:
                                conn.sendall(b"OK")

                        except (ValueError, IndexError) as ve:
                            print(f"Handler Error: Parsing failed for message. Sending ERROR to client. Error: {ve}. Incomplete buffer: '{receive_buffer}'")
                            conn.sendall(b"ERROR")
                            receive_buffer = ""
                            break

                        except ConnectionResetError:
                            print(f"Client {addr} forcibly disconnected.")
                            break
                        except BrokenPipeError:
                            print(f"Broken pipe error (client {addr} likely disconnected).")
                            break
                        except Exception as e:
                            print(f"An unexpected error occurred during data reception: {e}. Incomplete buffer: '{receive_buffer}'")
                            conn.sendall(b"ERROR")
                            receive_buffer = ""
                            break
            
            except Exception as e:
                print(f"Server accept or connection handling error: {e}. Waiting for new connection...")
            finally:
                if conn:
                    conn.close()
                    conn = None 
                time.sleep(1) 

    except Exception as e:
        print(f"Server socket initialization or binding error: {e}. Server will shut down.")
    finally:
        if server_socket:
            server_socket.close()
        print("Server application ended.")


# 메인 스레드에서 서버 루프를 실행 (게임 루프와 분리)
threading.Thread(target=run_server_session, daemon=True).start()

# 키보드 이벤트 리스너 등록
fig.canvas.mpl_connect('key_press_event', on_key_press)

plt.tight_layout()
ani = FuncAnimation(fig, update_plot, interval=1000)
plt.show()