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
FINAL_EPISODE_NUM = 4 # 마지막 에피소드 번호 (0-indexed라면 3; 1-indexed라면 4)

# 한글 폰트 설정 및 마이너스 기호 깨짐 방지
plt.rcParams['font.family'] = 'AppleGothic' # Mac 사용자용, 또는 'NanumGothic', 'Malgun Gothic' 등
plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

# 기울기 플롯을 위한 선 스타일 및 마커
SLOPE_LINESTYLE = '-' # 기울기 플롯은 실선으로 통일
SLOPE_MARKER = 'o' # 기울기 플롯 마커 통일

# 저장 폴더 이름
SAVE_DIR_NAME = "combined_average_slope_plots"

# --- 각 피드백 타입에 할당할 색상 (이전에는 사용자별 색상이었으나, 이제는 피드백 타입별 색상으로 사용) ---
# 더 많은 색상이 필요할 경우 'tab20' 또는 다른 컬러맵 사용
FEEDBACK_COLORS = plt.cm.get_cmap('tab10', len(FEEDBACK_SUBDIRS))
FEEDBACK_COLOR_MAP = {key: FEEDBACK_COLORS(i) for i, key in enumerate(FEEDBACK_SUBDIRS.keys())}
# ---

def load_all_episode_data_for_all_users(base_data_dir):
    """
    모든 사용자 폴더에서 모든 피드백 타입에 대한 에피소드 데이터를 통합하여 로드합니다.
    분석을 위해 단일 DataFrame으로 반환합니다.
    """
    all_combined_data = []

    user_folders = sorted([f for f in os.listdir(base_data_dir) if os.path.isdir(os.path.join(base_data_dir, f))])

    if not user_folders:
        print(f"No user folders found in '{base_data_dir}'. Please ensure data has been collected by main.py.")
        return pd.DataFrame()

    print(f"Loading all episode data from: {base_data_dir}")

    # 사용자 폴더 이름을 "User 1", "User 2" 등으로 매핑
    user_name_mapping = {folder_name: f"User {i+1}" for i, folder_name in enumerate(user_folders)}

    for user_folder_name in user_folders:
        user_folder_path = os.path.join(base_data_dir, user_folder_name)

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

                            episode_entry['user_id'] = display_user_name
                            episode_entry['original_user_folder_name'] = user_folder_name
                            episode_entry['feedback_type'] = feedback_key

                            all_combined_data.append(episode_entry)
                    except Exception as e:
                        print(f"Error loading episode file {e_file_path}: {e}")

    df = pd.DataFrame(all_combined_data)
    if not df.empty:
        df['episode_num'] = df['episode_num'].astype(int)
        df['feedback_type'] = df['feedback_type'].astype('category')
        df['user_id'] = pd.Categorical(df['user_id'], categories=[f"User {i+1}" for i in range(len(user_folders))], ordered=True)
        df = df.sort_values(by=['user_id', 'feedback_type', 'episode_num']).reset_index(drop=True)

    return df

def calculate_slope(x_values, y_values):
    """
    선형 회귀를 사용하여 기울기를 계산합니다.
    """
    if len(x_values) < 2:
        return np.nan # 데이터 포인트가 2개 미만이면 기울기 계산 불가

    coefficients = np.polyfit(x_values, y_values, 1)
    return coefficients[0]


def plot_combined_average_slopes(df_all_users):
    """
    각 metric(MaxZ/Error, mean/std) 별로 하나의 plot에 모든 condition의
    'Average All Users' 기울기 그래프를 plot합니다.
    총 4개의 플롯이 생성됩니다.
    """

    fig, axs = plt.subplots(4, 1, figsize=(15, 20), sharex=True) # 4행 1열 서브플롯, x축 공유
    fig.suptitle('Average Slope Analysis by Metric Across All Conditions', fontsize=20)

    # 각 측정항목별 제목 및 데이터 접근 키
    plot_configs = [
        {'title': 'Average Slope of Max Z Mean', 'data_key': 'mean_maxZ', 'ylabel': 'Slope of Mean Max Z'},
        {'title': 'Average Slope of Max Z Std Dev', 'data_key': 'std_maxZ', 'ylabel': 'Slope of Std Dev Max Z'},
        {'title': 'Average Slope of Error Mean', 'data_key': 'mean_error', 'ylabel': 'Slope of Mean Error'},
        {'title': 'Average Slope of Error Std Dev', 'data_key': 'std_error', 'ylabel': 'Slope of Std Dev Error'},
    ]

    # 각 피드백 타입 이름 (정의된 순서대로)
    feedback_types_ordered = list(FEEDBACK_SUBDIRS.keys())

    for row_idx, config in enumerate(plot_configs):
        ax = axs[row_idx]

        ax.set_title(config['title'])
        ax.set_xlabel("Episode Number")
        ax.set_ylabel(config['ylabel'])
        ax.grid(True)
        ax.tick_params(axis='both', which='major', labelsize=10) # 축의 숫자 레이블 크기 설정

        for ft_name in feedback_types_ordered:
            # 해당 피드백 타입에 대한 데이터 필터링
            df_ft_filtered = df_all_users[df_all_users['feedback_type'] == ft_name].copy()

            # 모든 사용자의 기울기 데이터를 저장할 딕셔너리 (episode_num -> list of slopes)
            all_users_slopes_by_episode = {}

            # 각 사용자별로 기울기 계산 및 저장
            unique_users = df_ft_filtered['user_id'].cat.categories # 해당 피드백 타입에 있는 사용자들만
            for user_id_display in unique_users:
                df_user_ft = df_ft_filtered[df_ft_filtered['user_id'] == user_id_display].sort_values(by='episode_num')

                if df_user_ft.empty:
                    continue

                episode_nums = df_user_ft['episode_num'].tolist()
                values = df_user_ft[config['data_key']].tolist()

                # Cumulative slope calculation for each user
                slopes = [calculate_slope(episode_nums[:i+1], values[:i+1]) for i in range(len(episode_nums))]

                # Store each user's slopes by episode for averaging
                for ep, slope in zip(episode_nums, slopes):
                    if not np.isnan(slope):
                        # 에피소드 1 (0-indexed)의 기울기 데이터는 제외
                        if ep != 1: # 이 부분이 수정된 핵심 부분입니다.
                            if ep not in all_users_slopes_by_episode:
                                all_users_slopes_by_episode[ep] = []
                            all_users_slopes_by_episode[ep].append(slope)

            # 모든 사용자 기울기의 평균 그래프 (for current feedback type)
            if all_users_slopes_by_episode:
                avg_slopes_episodes = sorted(all_users_slopes_by_episode.keys())
                avg_slopes_values = [np.mean(all_users_slopes_by_episode[ep]) for ep in avg_slopes_episodes]

                ax.plot(avg_slopes_episodes, avg_slopes_values,
                        color=FEEDBACK_COLOR_MAP[ft_name],
                        linestyle=SLOPE_LINESTYLE, marker=SLOPE_MARKER,
                        label=f'{ft_name}', linewidth=2)

                # 마지막 에피소드 평균 기울기 값을 그래프에 텍스트로 표시
                if FINAL_EPISODE_NUM in avg_slopes_episodes:
                    last_avg_slope_value = avg_slopes_values[avg_slopes_episodes.index(FINAL_EPISODE_NUM)]
                    # 텍스트 위치를 각 라인의 마지막 지점 근처에 배치
                    ax.text(FINAL_EPISODE_NUM + 0.1, last_avg_slope_value,
                            f'{last_avg_slope_value:.4f}',
                            color=FEEDBACK_COLOR_MAP[ft_name],
                            fontsize=9, verticalalignment='center')


        ax.legend(loc='upper right', fontsize=10) # 각 서브플롯별 범례

    plt.tight_layout(rect=[0, 0.03, 1, 0.96]) # 타이틀 공간 확보

    # --- 플롯 저장 기능 ---
    save_base_dir = "Python/data_analysis/" # 기존 구조에 맞춤 (이전 요청과 동일하게 유지)
    save_dir = os.path.join(save_base_dir, SAVE_DIR_NAME)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created save directory: {save_dir}")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"combined_average_slopes_analysis_{timestamp}.png"
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


def start_combined_slope_analyzer():
    """
    모든 사용자의 데이터를 로드하고, 각 metric 별로 모든 condition의 평균 기울기를 플롯하는 메인 함수.
    """
    base_dir = "Python/data_analysis/experiment_data" # 데이터가 있는 최상위 폴더 경로

    df_all_users = load_all_episode_data_for_all_users(base_dir)

    if not df_all_users.empty:
        plot_combined_average_slopes(df_all_users)
    else:
        print("No data loaded for slope analysis. Exiting.")
        sys.exit(0)

if __name__ == "__main__":
    start_combined_slope_analyzer()