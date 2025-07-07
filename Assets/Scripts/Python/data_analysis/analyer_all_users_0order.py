import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import sys
import glob
import ast # 문자열로 저장된 리스트를 파싱하기 위해
import datetime # 파일명에 타임스탬프 추가

# --- Configuration (main.py 및 viewer.py와 동일하게 유지) ---
FEEDBACK_SUBDIRS = {
    "OnlyVisual": "0.Visual",
    "OnlyVibrotactile_fixed": "1.Vibrotactile(fixed)",
    "OnlyVibrotactile_adaptive": "2.Vibrotactile(adaptive)",
    "VisualwithVibrotactile_fixed": "3.Visual&Vibrotactile(fixed)",
    "VisualwithVibrotactile_adaptive": "4.Visual&Vibrotactile(adaptive)"
}
TRIALS_PER_EPISODE = 15 # 한 에피소드당 trial 수 (조정 가능)
FINAL_EPISODE_NUM = 4 # 마지막 에피소드 번호 (0-indexed라면 3, 1-indexed라면 4)

# 한글 폰트 설정 및 마이너스 기호 깨짐 방지
plt.rcParams['font.family'] = 'AppleGothic' # Mac 사용자용, 또는 'NanumGothic', 'Malgun Gothic' 등
plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지


# 값 플롯을 위한 선 스타일 및 마커
VALUE_LINESTYLE = '-' # 값 플롯은 실선으로 통일
VALUE_MARKER = 'o' # 값 플롯 마커 통일

# 저장 폴더 이름
SAVE_DIR_NAME = "all_users_raw_values_plots"

def load_all_episode_data_for_all_users(base_data_dir):
    """
    모든 사용자 폴더에서 모든 피드백 타입에 대한 에피소드 데이터를 통합하여 로드합니다.
    ANOVA 분석을 위해 단일 DataFrame으로 반환합니다.
    """
    all_combined_data = []

    user_folders = sorted([f for f in os.listdir(base_data_dir) if os.path.isdir(os.path.join(base_data_dir, f))])

    if not user_folders:
        print(f"No user folders found in '{base_data_dir}'. Please ensure data has been collected by main.py.")
        return pd.DataFrame()

    print(f"Loading all episode data from: {base_data_dir}")

    # 사용자 폴더 이름을 "User 1", "User 2" 등으로 매핑하기 위한 딕셔너리
    user_name_mapping = {folder_name: f"User {i+1}" for i, folder_name in enumerate(user_folders)}


    for user_folder_name in user_folders:
        user_folder_path = os.path.join(base_data_dir, user_folder_name)

        # 매핑된 사용자 이름을 가져옴
        display_user_name = user_name_mapping[user_folder_name]

        for feedback_key, subdir_name in FEEDBACK_SUBDIRS.items():
            episode_stats_dir = os.path.join(user_folder_path, subdir_name, "episode_stats")

            if os.path.exists(episode_stats_dir):
                episode_files = sorted(glob.glob(os.path.join(episode_stats_dir, 'episode_data_ep*.csv')))
                for e_file_path in episode_files:
                    try:
                        df_episode = pd.read_csv(e_file_path)
                        if not df_episode.empty:
                            episode_entry = df_episode.iloc[0].to_dict()

                            for key_list in ['all_maxZs_in_episode', 'all_errors_in_episode', 'all_impacts_in_episode']:
                                if key_list in episode_entry and isinstance(episode_entry[key_list], str):
                                    parsed_list = ast.literal_eval(episode_entry[key_list])
                                    episode_entry[key_list] = list(map(float, parsed_list))
                                else:
                                    episode_entry[key_list] = []

                            for key_float in ['mean_maxZ', 'std_maxZ', 'mean_error', 'std_error', 'mean_impact', 'std_impact']:
                                if key_float in episode_entry:
                                    episode_entry[key_float] = float(episode_entry[key_float])

                            if 'episode_num' in episode_entry:
                                episode_entry['episode_num'] = int(episode_entry['episode_num'])

                            episode_entry['user_id'] = display_user_name # 매핑된 사용자 이름을 사용
                            episode_entry['original_user_folder_name'] = user_folder_name # 원본 폴더 이름도 저장 (필요시)
                            episode_entry['feedback_type'] = feedback_key

                            all_combined_data.append(episode_entry)
                    except Exception as e:
                        print(f"Error loading episode file {e_file_path}: {e}")

    df = pd.DataFrame(all_combined_data)
    if not df.empty:
        df['episode_num'] = df['episode_num'].astype(int)
        df['feedback_type'] = df['feedback_type'].astype('category')
        # user_id는 이제 'User 1' 형태의 문자열이므로 category로 변환
        df['user_id'] = pd.Categorical(df['user_id'], categories=[f"User {i+1}" for i in range(len(user_folders))], ordered=True) # 순서 지정
        df = df.sort_values(by=['user_id', 'feedback_type', 'episode_num']).reset_index(drop=True)

    return df


def plot_all_users_raw_values(df_all_users):
    """
    모든 사용자에 대해 각 조건별로 Max Z와 Error의 평균 및 표준 편차의 원본 값을 플롯합니다.
    총 4개의 주요 측정항목 (Max Z Mean, Max Z Std Dev, Error Mean, Error Std Dev)에 대해,
    각 측정항목별로 5개의 피드백 조건이 있으므로 총 4개의 행과 5개의 열을 가진 서브플롯을 생성합니다.
    각 플롯에는 개별 사용자 데이터 포인트와 모든 사용자 데이터의 평균을 나타내는 선이 포함됩니다.
    """

    fig, axs = plt.subplots(4, 5, figsize=(30, 20), sharex='col', sharey='row') # col로 x축 공유, row로 y축 공유

    # Sup title
    fig.suptitle('Raw Value Analysis for All Users Across All Conditions', fontsize=24)

    # 각 피드백 타입 이름 가져오기 (정의된 순서대로)
    feedback_types_ordered = list(FEEDBACK_SUBDIRS.keys())

    # 사용자별 고유 색상 매핑 (이제 user_id는 'User 1' 형태의 문자열)
    unique_users = df_all_users['user_id'].cat.categories # Categorical의 categories 속성 사용
    user_colors = plt.cm.get_cmap('tab10', len(unique_users)) # 'tab10' 컬러맵 사용
    user_color_map = {user: user_colors(i) for i, user in enumerate(unique_users)}

    # 각 측정항목별 제목 및 데이터 접근 키
    plot_configs = [
        {'title_prefix': 'Max Z Mean', 'data_key': 'mean_maxZ', 'ylabel': 'Mean Max Z Value'},
        {'title_prefix': 'Max Z Std Dev', 'data_key': 'std_maxZ', 'ylabel': 'Std Dev Max Z Value'},
        {'title_prefix': 'Error Mean', 'data_key': 'mean_error', 'ylabel': 'Mean Error Value'},
        {'title_prefix': 'Error Std Dev', 'data_key': 'std_error', 'ylabel': 'Std Dev Error Value'},
    ]

    # 데이터를 순회하며 각 서브플롯에 플롯
    for row_idx, config in enumerate(plot_configs):
        for col_idx, ft_name in enumerate(feedback_types_ordered):
            ax = axs[row_idx, col_idx]

            # Subplot Title
            ax.set_title(f'{config["title_prefix"]} ({ft_name})')
            ax.set_xlabel("Episode Number")
            ax.set_ylabel(config["ylabel"])
            ax.grid(True)

            # --- 여기부터 추가된 부분: 축의 숫자 레이블 크기 설정 ---
            ax.tick_params(axis='both', which='major', labelsize=10) # 모든 축의 주 틱 레이블 크기 설정
            # --- 추가된 부분 끝 ---

            # 해당 피드백 타입에 대한 데이터 필터링
            df_ft_filtered = df_all_users[df_all_users['feedback_type'] == ft_name].copy()

            # 모든 사용자의 값 데이터를 저장할 딕셔너리 (episode_num -> list of values)
            # 이를 통해 각 episode_num별로 사용자들의 값 평균을 계산할 수 있음
            all_users_values_by_episode = {}

            for user_id_display in unique_users:
                df_user_ft = df_ft_filtered[df_ft_filtered['user_id'] == user_id_display].sort_values(by='episode_num')

                if df_user_ft.empty:
                    continue

                episode_nums = df_user_ft['episode_num'].tolist()
                values = df_user_ft[config['data_key']].tolist()

                # 개별 사용자 데이터 플롯
                ax.plot(episode_nums, values, VALUE_LINESTYLE + VALUE_MARKER,
                        color=user_color_map[user_id_display], label=f'{user_id_display}', linewidth=1.5)

                # 모든 사용자의 값 데이터를 에피소드별로 저장
                for ep, value in zip(episode_nums, values):
                    if not np.isnan(value):
                        if ep not in all_users_values_by_episode:
                            all_users_values_by_episode[ep] = []
                        all_users_values_by_episode[ep].append(value)

            # 모든 사용자 값의 평균 그래프 추가
            last_avg_value = np.nan
            if all_users_values_by_episode:
                avg_values_episodes = sorted(all_users_values_by_episode.keys())
                avg_values = [np.mean(all_users_values_by_episode[ep]) for ep in avg_values_episodes]

                ax.plot(avg_values_episodes, avg_values, 'k--', label='Average All Users', linewidth=2.5, marker='X') # 검은색 점선, 마커 X

                # 마지막 에피소드 (FINAL_EPISODE_NUM)에 해당하는 평균 값 찾기
                if FINAL_EPISODE_NUM in avg_values_episodes:
                    last_avg_value = avg_values[avg_values_episodes.index(FINAL_EPISODE_NUM)]

            # 마지막 에피소드 평균 값을 플롯에 표시
            text_content = ""
            if not np.isnan(last_avg_value):
                text_content += f'Avg All Users (Ep {FINAL_EPISODE_NUM}): {last_avg_value:.4f}'

            if text_content:
                # 텍스트 박스에 표시 (그래프의 오른쪽 상단에 고정)
                text_x = 0.98
                text_y = 0.98
                ax.text(text_x, text_y,
                        text_content,
                        transform=ax.transAxes,
                        fontsize=10, verticalalignment='top', horizontalalignment='right',
                        bbox=dict(boxstyle='round,pad=0.5'))

    # Figure 전체에 대한 중앙 집중식 범례
    all_handles = []
    all_labels = []
    for user_id_display in unique_users:
        all_handles.append(plt.Line2D([0], [0], color=user_color_map[user_id_display], lw=1.5, marker=VALUE_MARKER, linestyle=VALUE_LINESTYLE))
        all_labels.append(user_id_display)

    # 평균 선에 대한 범례 추가
    all_handles.append(plt.Line2D([0], [0], color='k', lw=2.5, marker='X', linestyle='--'))
    all_labels.append('Average All Users')

    fig.legend(all_handles, all_labels, loc='upper left', bbox_to_anchor=(0.01, 0.99),
               title="Users", ncol=len(unique_users) + 1) # 평균 선 때문에 열 하나 추가

    plt.tight_layout(rect=[0, 0.03, 1, 0.96]) # 타이틀 공간 확보

    # --- 플롯 저장 기능 ---
    save_base_dir = "Python/data_analysis/experiment_data" # 기존 구조에 맞춤
    save_dir = os.path.join(save_base_dir, SAVE_DIR_NAME)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created save directory: {save_dir}")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"all_users_raw_values_analysis_{timestamp}.png"
    filepath = os.path.join(save_dir, filename)

    try:
        print("\nDEBUG: Preparing to save plot.")
        plt.savefig(filepath, dpi=300, bbox_inches='tight') # 고해상도, 잘림 방지
        print(f"DEBUG: Attempting plt.savefig to {filepath}")
        print(f"\nPlot saved successfully to: {filepath}")
    except Exception as e:
        print(f"\nError saving plot: {e}")
    # --- 저장 기능 끝 ---

    plt.show()


def start_all_users_value_analyzer():
    """
    모든 사용자의 데이터를 로드하고, 원본 값을 플롯하는 메인 함수.
    """
    base_dir = "Python/data_analysis/experiment_data" # 데이터가 있는 최상위 폴더 경로 (현재 스크립트 위치 기준)

    df_all_users = load_all_episode_data_for_all_users(base_dir)

    if not df_all_users.empty:
        plot_all_users_raw_values(df_all_users)
    else:
        print("No data loaded for value analysis. Exiting.")
        sys.exit(0)

if __name__ == "__main__":
    start_all_users_value_analyzer()