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
prev_trial_indexZ = [] # 이전 trial의 Index Z 데이터를 저장할 리스트
prev_trial_metadata = {} # 이전 trial의 메타데이터를 저장할 딕셔너리

# 에피소드 관련 변수 추가
TRIALS_PER_EPISODE = 15 # 한 에피소드당 trial 수 (조정 가능)
current_episode_trial_count = 0 # 현재 에피소드에서 진행된 trial 수
episode_maxZs = [] # 현재 에피소드의 maxZ 값들을 저장할 리스트
episode_errors = [] # 현재 에피소드의 error 값들을 저장할 리스트
episode_impacts = [] # NEW: 에피소드별 impact 값들을 저장할 리스트

episode_data = [] # 에피소드 통계 데이터를 저장할 리스트
# current_feedback_type을 초기화할 때, 이전 값을 추적할 변수 추가
current_feedback_type = "UNKNOWN" # 현재 피드백 타입을 저장할 변수 (초기값)
last_processed_feedback_type = "UNKNOWN" # 마지막으로 처리된 피드백 타입을 저장할 변수


trial_history = [] # 각 trial의 (indexZ_list, metadata) 튜플을 저장

BASE_SAVE_DIR = ""  # 사용자 이름으로 생성될 최상위 폴더
FEEDBACK_SUBDIRS = {
    "OnlyVisual": "0.Visual",
    "OnlyVibrotactile_fixed": "1.Vibrotactile(fixed)",
    "OnlyVibrotactile_adaptive": "2.Vibrotactile(adaptive)",
    "VisualwithVibrotactile_fixed": "3.Visual&Vibrotactile(fixed)",
    "VisualwithVibrotactile_adaptive": "4.Visual&Vibrotactile(adaptive)"
}
# --------------------------------------------------

# 서브플롯 생성: 2행 3열로 구성 (새로운 Impact 통계 그래프 추가)
fig, axs = plt.subplots(2, 3, figsize=(20, 10)) # figsize도 조정
fig.suptitle('Button Press demo Dashboard', fontsize=16)


# --- axs[0,0]: 개별 Trial의 Index Z 변화 (현재 Trial) ---
ax1 = axs[0, 0]
line, = ax1.plot([], [], 'o-', label='Index Z')
maxZ_marker = ax1.axhline(0, color='red', linestyle='--', label='Max Z')
impact_marker = ax1.axhline(0, color='green', linestyle='--', label='Impact Point')
trial_info_text = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, verticalalignment='top')
ax1.legend()
ax1.set_title('Real-time Index Z per Trial (Current)')
ax1.set_xlabel("Time Step")
ax1.set_ylabel("Index Z Position (m)")
ax1.grid(True)


# --- axs[0,1]: Episode별 MaxZ 평균 및 분산 ---
ax2 = axs[0, 1]
episode_means_line, = ax2.plot([], [], 'b-o', label='Mean MaxZ') # 올바른 언팩킹
episode_stds_line, = ax2.plot([], [], 'r--x', label='Std Dev MaxZ') # 올바른 언팩킹
episode_maxz_text_box = ax2.text(0.02, 0.95, '', transform=ax2.transAxes, verticalalignment='top')
ax2.legend()
ax2.set_title(f'Episode Statistics: MaxZ (Trials per Episode: {TRIALS_PER_EPISODE})')
ax2.set_xlabel("Episode Number")
ax2.set_ylabel("Max Z Value (m)")
ax2.grid(True)


# --- axs[1,0]: Episode별 Error 평균 및 분산 ---
ax3 = axs[1, 0]
episode_error_means_line, = ax3.plot([], [], 'g-o', label='Mean Error')
episode_error_stds_line, = ax3.plot([], [], 'm--x', label='Std Dev Error')
episode_error_text_box = ax3.text(0.02, 0.95, '', transform=ax3.transAxes, verticalalignment='top')
ax3.legend()
ax3.set_title(f'Episode Statistics: Error (Trials per Episode: {TRIALS_PER_EPISODE})')
ax3.set_xlabel("Episode Number")
ax3.set_ylabel("Error (m)")
ax3.grid(True)

# --- axs[1,1]: 이전 Trial의 Index Z 변화 ---
ax4 = axs[1, 1]
line_prev, = ax4.plot([], [], 'o-', color='purple', label='Prev Index Z')
maxZ_marker_prev = ax4.axhline(0, color='orange', linestyle='--', label='Prev Max Z')
impact_marker_prev = ax4.axhline(0, color='cyan', linestyle='--', label='Prev Impact Point')
trial_info_text_prev = ax4.text(0.02, 0.95, '', transform=ax4.transAxes, verticalalignment='top')
ax4.legend()
ax4.set_title('Index Z per Trial (Previous)')
ax4.set_xlabel("Time Step")
ax4.set_ylabel("Index Z Position (m)")
ax4.grid(True)

# --- NEW: axs[0,2]: Episode별 Impact Position 평균 및 분산 ---
ax5 = axs[0, 2] # 새로운 위치 (예: 0행 2열)
episode_impact_means_line, = ax5.plot([], [], 'c-o', label='Mean Impact Pos') # 올바른 언팩킹
episode_impact_stds_line, = ax5.plot([], [], 'y--x', label='Std Dev Impact Pos') # 올바른 언팩킹
episode_impact_text_box = ax5.text(0.02, 0.95, '', transform=ax5.transAxes, verticalalignment='top')
ax5.legend()
ax5.set_title(f'Episode Statistics: Impact Position (Trials per Episode: {TRIALS_PER_EPISODE})')
ax5.set_xlabel("Episode Number")
ax5.set_ylabel("Impact Position (m)")
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
            elif key == "feedbackType": # feedbackType 파싱
                data[key] = val.strip() # 문자열 그대로 저장
            else:
                # maxZ와 error는 Unity에서 보내도 여기서 덮어쓸 것이므로 크게 중요하지 않음
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

    # 피드백 타입에 해당하는 서브디렉토리 이름 가져오기
    subdir_name = FEEDBACK_SUBDIRS.get(feedback_type, "UnknownFeedbackType")
    
    # 최상위 폴더/자식 폴더/파일타입 폴더 구조
    type_specific_dir = os.path.join(BASE_SAVE_DIR, subdir_name, file_type)

    if not os.path.exists(type_specific_dir):
        os.makedirs(type_specific_dir)

    if file_type == "trials" and trial_info:
        filename = f'trial_{int(trial_info["trial"]):03d}_{datetime.datetime.now().strftime("%H%M%S")}.csv'
    elif file_type == "episode_stats" and trial_info: # episode_num이 trial_info에 들어있다고 가정
        filename = f'episode_data_ep{trial_info["episode_num"]:03d}_{feedback_type}_{datetime.datetime.now().strftime("%H%M%S")}.csv'
    else:
        raise ValueError(f"Invalid file_type: {file_type} or missing trial_info for it.")
        
    return os.path.join(type_specific_dir, filename)

def save_trial(indexZ_list, metadata):
    """
    개별 trial 데이터를 현재 세션 폴더에 저장합니다.
    """
    df = pd.DataFrame({'index_z': indexZ_list})
    # metadata에서 maxZ와 error를 직접 사용 (이 부분은 아래 로직에서 재계산된 값으로 대체될 것임)
    for key in ['trial', 'maxZ', 'impact', 'error']:
        df[key] = metadata[key]
    df['feedbackType'] = metadata.get('feedbackType', 'UNKNOWN')
    
    filepath = get_save_path(metadata.get('feedbackType', 'UNKNOWN'), "trials", metadata)
    df.to_csv(filepath, index=False)
    # print(f"[Saved] {filepath}") # 너무 많은 로그를 피하기 위해 주석 처리

def save_episode_data(episode_num, data, feedback_type):
    """
    에피소드 통계 데이터를 현재 세션 폴더에 저장합니다.
    """
    # episode_num을 포함한 dict를 넘겨줘서 get_save_path에서 사용할 수 있도록 함
    filepath = get_save_path(feedback_type, "episode_stats", {"episode_num": episode_num})
    df = pd.DataFrame([data]) # 단일 에피소드 데이터를 DataFrame으로 변환
    df.to_csv(filepath, index=False)
    print(f"[Saved Episode Data] {filepath}")


def update_plot(frame):
    global trial_indexZ, trial_metadata, current_episode_trial_count, \
           episode_maxZs, episode_errors, episode_data, current_feedback_type, \
           prev_trial_indexZ, prev_trial_metadata, episode_impacts

    # --- axs[0,0]: 개별 Trial의 Index Z 변화 업데이트 (현재 Trial) ---
    # trial_metadata가 비어있을 때 'maxZ'나 'impact' 키가 없을 수 있으므로, 먼저 trial_metadata의 유효성 검사
    if trial_indexZ and trial_metadata and 'maxZ' in trial_metadata and 'impact' in trial_metadata:
        x = list(range(len(trial_indexZ)))
        y = trial_indexZ
        line.set_data(x, y)
        ax1.set_xlim(0, max(10, len(x)))
        ax1.set_ylim(min(y) - 0.01, max(y) + 0.01)
        maxZ_marker.set_ydata([trial_metadata['maxZ']])
        impact_marker.set_ydata([trial_metadata['impact']])
        
        # 현재 trial 정보 (episode 진행 상황 및 feedbackType 포함)
        trial_info_text.set_text(f"Trial {int(trial_metadata['trial'])} ({current_episode_trial_count}/{TRIALS_PER_EPISODE})\n"
                                 f"Type: {current_feedback_type}\nError: {trial_metadata['error']:.5f}")
    else: # 데이터가 없으면 그래프 초기화
        line.set_data([], [])
        maxZ_marker.set_ydata([0]) # 빈 리스트 대신 기본값 0으로 설정하여 오류 방지
        impact_marker.set_ydata([0]) # 빈 리스트 대신 기본값 0으로 설정하여 오류 방지
        trial_info_text.set_text("No current trial data")
        ax1.set_xlim(0, 10)
        ax1.set_ylim(-0.1, 0.3)


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
        latest_maxz_std = episode_data[-1]['std_maxZ']
        episode_maxz_text_box.set_text(f"Ep {latest_episode_num}\nMean: {latest_maxz_mean:.5f}\nStd Dev: {latest_maxz_std:.5f}")


        # Error 통계
        episode_error_means = [d['mean_error'] for d in episode_data]
        episode_error_stds = [d['std_error'] for d in episode_data]
        episode_error_means_line.set_data(episode_numbers, episode_error_means)
        episode_error_stds_line.set_data(episode_numbers, episode_error_stds)
        
        all_error_values = [e for d in episode_data for e in d.get('all_errors_in_episode', [])]
        if all_error_values:
            min_y3 = min(all_error_values) - 0.02
            max_y3 = max(all_error_values) + 0.02
            if abs(max_y3 - min_y3) < 0.01:
                center = (min_y3 + max_y3) / 2
                min_y3 = center - 0.005
                max_y3 = center + 0.005
            ax3.set_ylim(min_y3, max_y3)
        else:
            ax3.set_ylim(-0.1, 0.1)
        ax3.set_xlim(-0.5, max(episode_numbers) + 0.5 if episode_numbers else 0.5)

        # 가장 최근 에피소드의 Error 통계 표시
        latest_error_mean = episode_data[-1]['mean_error']
        latest_error_std = episode_data[-1]['std_error']
        episode_error_text_box.set_text(f"Ep {latest_episode_num}\nMean: {latest_error_mean:.5f}\nStd Dev: {latest_error_std:.5f}")
        
        # NEW: Impact Position 통계
        episode_impact_means = [d['mean_impact'] for d in episode_data]
        episode_impact_stds = [d['std_impact'] for d in episode_data]
        episode_impact_means_line.set_data(episode_numbers, episode_impact_means)
        episode_impact_stds_line.set_data(episode_numbers, episode_impact_stds)
        
        all_impact_values = [i for d in episode_data for i in d.get('all_impacts_in_episode', [])]
        if all_impact_values:
            min_y5 = min(all_impact_values) - 0.02
            max_y5 = max(all_impact_values) + 0.02
            if abs(max_y5 - min_y5) < 0.01:
                center = (min_y5 + max_y5) / 2
                min_y5 = center - 0.005
                max_y5 = center + 0.005
            ax5.set_ylim(min_y5, max_y5)
        else:
            ax5.set_ylim(-0.1, 0.1)
        ax5.set_xlim(-0.5, max(episode_numbers) + 0.5 if episode_numbers else 0.5)

        # 가장 최근 에피소드의 Impact 통계 표시
        latest_impact_mean = episode_data[-1]['mean_impact']
        latest_impact_std = episode_data[-1]['std_impact']
        episode_impact_text_box.set_text(f"Ep {latest_episode_num}\nMean: {latest_impact_mean:.5f}\nStd Dev: {latest_impact_std:.5f}")

    else: # 에피소드 데이터가 없으면 그래프 초기화
        episode_means_line.set_data([], [])
        episode_stds_line.set_data([], [])
        episode_maxz_text_box.set_text("No episode data")
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 0.3)

        episode_error_means_line.set_data([], [])
        episode_error_stds_line.set_data([], [])
        episode_error_text_box.set_text("No episode data")
        ax3.set_xlim(0, 1)
        ax3.set_ylim(-0.1, 0.1)
        
        # NEW: Impact Position 통계 초기화
        episode_impact_means_line.set_data([], [])
        episode_impact_stds_line.set_data([], [])
        episode_impact_text_box.set_text("No episode data")
        ax5.set_xlim(0, 1)
        ax5.set_ylim(-0.1, 0.1)


    # --- axs[1,1]: 이전 Trial의 Index Z 변화 업데이트 ---
    # prev_trial_metadata가 비어있을 때 'maxZ'나 'impact' 키가 없을 수 있으므로, 먼저 prev_trial_metadata의 유효성 검사
    if prev_trial_indexZ and prev_trial_metadata and 'maxZ' in prev_trial_metadata and 'impact' in prev_trial_metadata:
        x_prev = list(range(len(prev_trial_indexZ)))
        y_prev = prev_trial_indexZ
        line_prev.set_data(x_prev, y_prev)
        ax4.set_xlim(0, max(10, len(x_prev)))
        ax4.set_ylim(min(y_prev) - 0.01, max(y_prev) + 0.01)
        maxZ_marker_prev.set_ydata([prev_trial_metadata['maxZ']])
        impact_marker_prev.set_ydata([prev_trial_metadata['impact']])
        trial_info_text_prev.set_text(f"Prev Trial {int(prev_trial_metadata['trial'])}\n"
                                      f"Type: {prev_trial_metadata.get('feedbackType', 'UNKNOWN')}\nError: {prev_trial_metadata['error']:.5f}")
    else: # 이전 trial 데이터가 없으면 그래프 초기화
        line_prev.set_data([], [])
        maxZ_marker_prev.set_ydata([0]) # 빈 리스트 대신 기본값 0으로 설정하여 오류 방지
        impact_marker_prev.set_ydata([0]) # 빈 리스트 대신 기본값 0으로 설정하여 오류 방지
        trial_info_text_prev.set_text("No previous trial data")
        ax4.set_xlim(0, 10)
        ax4.set_ylim(-0.1, 0.3)


    # 모든 업데이트된 객체 반환 (모든 라인 객체와 텍스트 객체를 반환해야 애니메이션이 동작)
    return line, maxZ_marker, impact_marker, trial_info_text, \
           episode_means_line, episode_stds_line, episode_maxz_text_box, \
           episode_error_means_line, episode_error_stds_line, episode_error_text_box, \
           line_prev, maxZ_marker_prev, impact_marker_prev, trial_info_text_prev, \
           episode_impact_means_line, episode_impact_stds_line, episode_impact_text_box


def on_key_press(event):
    """
    키보드 이벤트를 처리하여 이전 trial 데이터를 삭제합니다.
    """
    global trial_indexZ, trial_metadata, prev_trial_indexZ, prev_trial_metadata, \
           current_episode_trial_count, episode_maxZs, episode_errors, trial_history, \
           episode_impacts

    if event.key == 'backspace' or event.key == 'delete':
        print(f"Key '{event.key}' pressed. Attempting to undo last trial.")
        
        if not trial_history:
            print("No trials in history to undo.")
            return

        # 마지막 trial 데이터 제거
        removed_trial_indexZ, removed_trial_metadata = trial_history.pop()

        # episode 관련 데이터에서 제거
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

        # 현재 표시되는 trial 데이터를 이전 trial로 업데이트
        if trial_history:
            trial_indexZ, trial_metadata = trial_history[-1]
            if len(trial_history) > 1:
                prev_trial_indexZ, prev_trial_metadata = trial_history[-2]
            else: # trial_history에 하나만 남았으면 prev는 비움
                prev_trial_indexZ = []
                prev_trial_metadata = {}
        else: # trial_history가 비었으면 모두 비움
            trial_indexZ = []
            trial_metadata = {}
            prev_trial_indexZ = []
            prev_trial_metadata = {}

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
           trial_indexZ, trial_metadata, prev_trial_indexZ, prev_trial_metadata

    current_episode_trial_count = 0
    episode_maxZs = []
    episode_errors = []
    episode_impacts = []
    episode_data = [] # 에피소드 통계 데이터도 초기화
    trial_history = [] # 트라이얼 히스토리도 초기화
    
    # 현재 플롯에 표시되는 데이터도 초기화 (옵션)
    trial_indexZ = []
    trial_metadata = {}
    prev_trial_indexZ = []
    prev_trial_metadata = {}

    print("Episode and trial data has been reset due to feedback type change.")


def run_server_session():
    """
    단일 서버 세션을 실행하고, 클라이언트 연결이 끊어지면 종료됩니다.
    """
    global trial_indexZ, trial_metadata, current_episode_trial_count, \
           episode_maxZs, episode_errors, episode_data, current_feedback_type, \
           prev_trial_indexZ, prev_trial_metadata, trial_history, \
           episode_impacts, BASE_SAVE_DIR, last_processed_feedback_type

    # --- 2. 이름 입력에서 이미 존재하는 폴더일 시 기존 폴더 사용 ---
    user_name = input("데이터를 저장할 사용자 이름을 입력하세요: ").strip()
    if not user_name:
        user_name = "default_user"
        print("이름이 입력되지 않아 'default_user'로 설정합니다.")
    
    BASE_SAVE_DIR = os.path.join("demo_data", user_name) # 'demo_data' 하위에 사용자 이름 폴더
    
    if os.path.exists(BASE_SAVE_DIR):
        print(f"경고: '{user_name}' 폴더가 이미 존재합니다. 기존 폴더를 사용합니다.")
    else:
        os.makedirs(BASE_SAVE_DIR)
        print(f"새 폴더 '{user_name}'를 생성했습니다.")

    print(f"모든 데이터는 다음 위치에 저장됩니다: {BASE_SAVE_DIR}")

    # 피드백 타입별 자식 폴더 생성
    for subdir in FEEDBACK_SUBDIRS.values():
        os.makedirs(os.path.join(BASE_SAVE_DIR, subdir, "trials"), exist_ok=True)
        os.makedirs(os.path.join(BASE_SAVE_DIR, subdir, "episode_stats"), exist_ok=True)
    print("피드백 타입별 폴더 구조를 생성했습니다.")

    # 각 서버 세션 시작 시 데이터 초기화
    # 새로운 사용자 이름이 입력되었을 때 모든 통계 및 기록 초기화
    current_episode_trial_count = 0
    episode_maxZs = []
    episode_errors = []
    episode_impacts = []
    episode_data = []
    trial_history = []
    trial_indexZ = []
    trial_metadata = {}
    prev_trial_indexZ = []
    prev_trial_metadata = {}
    current_feedback_type = "UNKNOWN"
    last_processed_feedback_type = "UNKNOWN" # 세션 시작 시 초기화

    receive_buffer = ""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 주소 재사용 옵션 추가
            s.bind(('127.0.0.1', 25001))
            s.listen(1)
            print("Listening for connection...")
            conn, addr = s.accept()
            print(f"Connected by {addr}")

            with conn:
                while True: # 클라이언트로부터 데이터를 받는 루프
                    try:
                        # 데이터를 받아서 버퍼에 추가
                        data_chunk = conn.recv(4096)
                        if not data_chunk:
                            print("Client disconnected. Restarting server...")
                            break # 클라이언트 연결 끊김 시 내부 루프 종료

                        receive_buffer += data_chunk.decode('utf-8')

                        # 종단 문자 '\n'을 기준으로 메시지 분리
                        # 한 번의 recv로 여러 메시지가 올 수도 있으므로 while 루프 사용
                        while '\n' in receive_buffer:
                            message_end_index = receive_buffer.find('\n')
                            full_message = receive_buffer[:message_end_index].strip() # 완전한 메시지
                            receive_buffer = receive_buffer[message_end_index + 1:] # 나머지 데이터

                            if not full_message: # 빈 메시지 (연속된 \n 등)는 무시
                                continue

                            # 여기서부터 기존 parse_data 및 처리 로직 시작
                            parsed = parse_data(full_message) # 완전한 메시지를 파싱

                            # --- 1. feedbackType 변경 시 초기화 로직 ---
                            new_feedback_type = parsed.get('feedbackType', 'UNKNOWN')
                            if new_feedback_type != last_processed_feedback_type and last_processed_feedback_type != "UNKNOWN":
                                print(f"Feedback Type changed from '{last_processed_feedback_type}' to '{new_feedback_type}'. Resetting episode and trial counts.")
                                reset_episode_and_trial_data()
                                current_feedback_type = new_feedback_type
                                last_processed_feedback_type = new_feedback_type
                            elif last_processed_feedback_type == "UNKNOWN": # 첫 데이터 수신 시 (서버 재시작 후 첫 데이터)
                                current_feedback_type = new_feedback_type
                                last_processed_feedback_type = new_feedback_type

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

                            prev_trial_indexZ = list(trial_indexZ)
                            prev_trial_metadata = dict(trial_metadata)

                            trial_indexZ = trial_metadata_for_processing['indexZs']
                            trial_metadata = trial_metadata_for_processing

                            trial_history.append((list(trial_indexZ), dict(trial_metadata)))

                            save_trial(trial_indexZ, trial_metadata)

                            episode_maxZs.append(trial_metadata['maxZ'])
                            episode_errors.append(trial_metadata['error'])
                            episode_impacts.append(trial_metadata['impact'])
                            current_episode_trial_count += 1

                            if current_episode_trial_count >= TRIALS_PER_EPISODE:
                                mean_maxZ = np.mean(episode_maxZs)
                                std_maxZ = np.std(episode_maxZs)

                                mean_error = np.mean(episode_errors)
                                std_error = np.std(episode_errors)

                                mean_impact = np.mean(episode_impacts)
                                std_impact = np.std(episode_impacts)

                                episode_num = len(episode_data) + 1

                                episode_entry = {
                                    'episode_num': episode_num,
                                    'feedback_type': current_feedback_type,
                                    'mean_maxZ': mean_maxZ,
                                    'std_maxZ': std_maxZ,
                                    'all_maxZs_in_episode': list(episode_maxZs),
                                    'mean_error': mean_error,
                                    'std_error': std_error,
                                    'all_errors_in_episode': list(episode_errors),
                                    'mean_impact': mean_impact,
                                    'std_impact': std_impact,
                                    'all_impacts_in_episode': list(episode_impacts)
                                }
                                episode_data.append(episode_entry)

                                save_episode_data(episode_num, episode_entry, current_feedback_type)

                                print(f"\n--- Episode {episode_num} Completed ({current_feedback_type}) ---")
                                print(f"MaxZ - Mean: {mean_maxZ:.5f}, Std Dev: {std_maxZ:.5f}")
                                print(f"Error - Mean: {mean_error:.5f}, Std Dev: {std_error:.5f}")
                                print(f"Impact - Mean: {mean_impact:.5f}, Std Dev: {std_impact:.5f}\n")                   

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
                        # 오류 발생 시 버퍼 비우지 않고 다음 데이터 기다려볼 수 있음 (복구 가능성)
                        # 또는 오류 메시지 자체가 문제인 경우, 버퍼를 비워야 함.
                        # 여기서는 ast.literal_eval 오류이므로, 해당 불완전한 메시지는 버려야 할 가능성 높음.
                        # 가장 안전하게는, 오류가 발생한 메시지는 버리고 receive_buffer를 해당 오류 메시지 이후로 잘라야 함.
                        # 현재 로직은 `full_message`에서 오류가 나도 `receive_buffer`를 건드리지 않으므로, 다음 루프에서 동일 오류 발생 가능.
                        # 따라서 `receive_buffer`를 여기서 명시적으로 조정해야 함.
                        receive_buffer = "" # 오류 발생시 현재 버퍼를 비워서 무한 루프 방지 (더 견고한 방법 필요시 재고)
                        break # 중요한 파싱 오류는 현재 연결을 끊고 재시작

                    except ConnectionResetError:
                        print("Client forcibly disconnected. Restarting server...")
                        break
                    except BrokenPipeError:
                        print("Broken pipe error (client likely disconnected). Restarting server...")
                        break
                    except Exception as e:
                        print(f"An unexpected error occurred during data reception: {e}. Incomplete buffer: '{receive_buffer}'")
                        conn.sendall(b"ERROR")
                        receive_buffer = "" # 오류 발생시 현재 버퍼를 비워서 무한 루프 방지
                        break
    except Exception as e:
        print(f"Server socket error: {e}. Attempting to restart server...")
    finally:
        pass

# 스레드로 서버 시작 (외부 루프에서 run_server_session을 계속 호출)
def server_main_loop():
    while True:
        print("Starting new server session...")
        # 각 세션 시작 시, 전역 변수들을 (필요에 따라) 초기 상태로 재설정합니다.
        # 이렇게 하지 않으면, 이전 세션의 데이터가 새 세션에 영향을 줄 수 있습니다.
        # run_server_session 내부에서 처리하는 것이 더 명확합니다.
        run_server_session()
        print("Server session ended. Waiting for a moment before restarting...")
        time.sleep(1) # 1초 대기

# 메인 스레드에서 서버 루프를 실행
threading.Thread(target=server_main_loop, daemon=True).start()

# 키보드 이벤트 리스너 등록
fig.canvas.mpl_connect('key_press_event', on_key_press)

plt.tight_layout() # 레이아웃을 자동으로 조절하여 겹치지 않게 함
ani = FuncAnimation(fig, update_plot, interval=1000)
plt.show()