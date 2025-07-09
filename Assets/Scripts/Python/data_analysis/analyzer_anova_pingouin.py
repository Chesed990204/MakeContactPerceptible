import pandas as pd
import numpy as np
import os
import sys
import glob
import ast # 문자열로 저장된 리스트를 파싱하기 위해
import pingouin as pg # pingouin 라이브러리 임포트

# --- Configuration (main.py 및 viewer.py와 동일하게 유지) ---
FEEDBACK_SUBDIRS = {
    "OnlyVisual": "0.Visual",
    "OnlyVibrotactile_fixed": "1.Vibrotactile(fixed)",
    "OnlyVibrotactile_adaptive": "2.Vibrotactile(adaptive)",
    "VisualwithVibrotactile_fixed": "3.Visual&Vibrotactile(fixed)",
    "VisualwithVibrotactile_adaptive": "4.Visual&Vibrotactile(adaptive)"
}
TRIALS_PER_EPISODE = 15 # 한 에피소드당 trial 수 (조정 가능)

def load_all_episode_data_for_anova(base_data_dir):
    """
    모든 사용자 폴더에서 모든 피드백 타입에 대한 에피소드 데이터를 통합하여 로드합니다.
    ANOVA 분석을 위해 단일 DataFrame으로 반환합니다.
    """
    all_combined_data = []
    
    user_folders = [f for f in os.listdir(base_data_dir) if os.path.isdir(os.path.join(base_data_dir, f))]

    if not user_folders:
        print(f"No user folders found in '{base_data_dir}'. Please ensure data has been collected by main.py.")
        return pd.DataFrame()

    print(f"Loading all episode data from: {base_data_dir}")

    for user_folder_name in user_folders:
        user_folder_path = os.path.join(base_data_dir, user_folder_name)
        
        for feedback_key, subdir_name in FEEDBACK_SUBDIRS.items():
            episode_stats_dir = os.path.join(user_folder_path, subdir_name, "episode_stats")

            if os.path.exists(episode_stats_dir):
                episode_files = sorted(glob.glob(os.path.join(episode_stats_dir, 'episode_data_ep*.csv')))
                for e_file_path in episode_files:
                    try:
                        df_episode = pd.read_csv(e_file_path)
                        if not df_episode.empty:
                            episode_entry = df_episode.iloc[0].to_dict()
                            
                            # 문자열로 저장된 리스트 파싱 및 float 변환
                            for key_list in ['all_maxZs_in_episode', 'all_errors_in_episode', 'all_impacts_in_episode']:
                                if key_list in episode_entry and isinstance(episode_entry[key_list], str):
                                    parsed_list = ast.literal_eval(episode_entry[key_list])
                                    episode_entry[key_list] = list(map(float, parsed_list))
                                else:
                                    episode_entry[key_list] = []
                            
                            # float 값 변환
                            for key_float in ['mean_maxZ', 'std_maxZ', 'mean_error', 'std_error', 'mean_impact', 'std_impact']:
                                if key_float in episode_entry:
                                    episode_entry[key_float] = float(episode_entry[key_float])

                            if 'episode_num' in episode_entry:
                                episode_entry['episode_num'] = int(episode_entry['episode_num'])
                            
                            episode_entry['user_id'] = user_folder_name
                            episode_entry['feedback_type'] = feedback_key

                            all_combined_data.append(episode_entry)
                    except Exception as e:
                        print(f"Error loading episode file {e_file_path}: {e}")
    
    df = pd.DataFrame(all_combined_data)
    if not df.empty:
        # pingouin은 category 타입을 자동으로 처리하지만, 명시적으로 변환하는 것이 좋습니다.
        df['episode_num'] = df['episode_num'].astype(int) # within subject factor는 int 또는 str
        df['feedback_type'] = df['feedback_type'].astype(str) # between subject factor는 str
        df['user_id'] = df['user_id'].astype(str) # subject ID는 str
        df = df.sort_values(by=['user_id', 'feedback_type', 'episode_num']).reset_index(drop=True)
    
    return df


def perform_anova_analysis_pingouin(df):
    """
    로드된 DataFrame에 대해 pingouin을 사용하여 ANOVA 분석을 수행합니다.
    """
    if df.empty:
        print("No data available for ANOVA analysis.")
        return

    dependent_variables = [
        'mean_maxZ', 'std_maxZ', 'mean_error', 'std_error', 'mean_impact', 'std_impact'
    ]

    print("\n--- Performing ANOVA Analysis with Pingouin ---")

    # To perform a Two-Way Repeated Measures ANOVA with pingouin,
    # we need to transform the data to a 'wide' format where each row is a subject (user)
    # and columns represent the combinations of within-subject factors (feedback_type and episode_num).

    def to_wide_format(df_long, dep_var_name):
        df_wide = df_long.pivot_table(index='user_id', 
                                      columns=['feedback_type', 'episode_num'], 
                                      values=dep_var_name)
        # Flatten multi-index columns to single string names like 'OnlyVisual_1'
        df_wide.columns = ['_'.join(map(str, col)).replace(' ', '') for col in df_wide.columns.values]
        return df_wide

    for dep_var in dependent_variables:
        print(f"\n===== Analyzing Dependent Variable: {dep_var} =====")
        
        # 1. One-Way ANOVA (Feedback Type) - using pingouin.anova
        # This treats feedback_type as a between-subjects factor, which might not be strictly accurate
        # if the same user experiences all feedback types. It's for general group comparison.
        print("\n--- One-Way ANOVA (Pingouin) by Feedback Type (Assumes Between-Subjects) ---")
        try:
            aov_ow = pg.anova(data=df, dv=dep_var, between='feedback_type', detailed=True)
            print(aov_ow)
            print(f"Interpretation: If p-val for 'feedback_type' is < 0.05, there's a significant difference between feedback types for {dep_var}.")
        except Exception as e:
            print(f"  Error performing One-Way ANOVA (Pingouin) for {dep_var}: {e}")

        # 2. Two-Way Repeated Measures ANOVA (Feedback Type x Episode Num)
        # This is more appropriate as both feedback_type and episode_num are within-subject factors.
        print(f"\n--- Two-Way Repeated Measures ANOVA (Pingouin) for {dep_var} ---")
        try:
            df_wide = to_wide_format(df, dep_var)
            
            # Construct the list of column names for the 'dv' argument in pg.rm_anova
            # These columns are the combinations of feedback_type and episode_num
            within_cols = []
            # Ensure categories are sorted to create consistent column names
            sorted_feedback_types = sorted(df['feedback_type'].unique())
            sorted_episode_nums = sorted(df['episode_num'].unique())

            for ft in sorted_feedback_types:
                 for ep in sorted_episode_nums:
                     col_name = f"{ft}_{ep}".replace(' ', '')
                     if col_name in df_wide.columns: # Check if the column exists in the wide DataFrame
                         within_cols.append(col_name)
            
            if not within_cols:
                print(f"  Warning: No suitable columns found for RM ANOVA for {dep_var}. Skipping RM ANOVA.")
                continue

            # Perform the Repeated Measures ANOVA
            aov_rm = pg.rm_anova(data=df_wide, dv=within_cols, 
                                 within=['feedback_type', 'episode_num'], 
                                 subject='user_id', detailed=True, correction=True) # correction for sphericity
            print(aov_rm)
            print(f"Interpretation: Look at p-val for 'feedback_type', 'episode_num', and 'feedback_type * episode_num'.")
            print(f"  A significant interaction suggests the effect of feedback type depends on episode progression for {dep_var}.")
            print("  `p-unc` is uncorrected p-value, `p-GG-unc` is Greenhouse-Geisser corrected if sphericity violated.")
        except Exception as e:
            print(f"  Error performing Two-Way Repeated Measures ANOVA for {dep_var}: {e}")
            print("  (Common issues: data imbalance, missing values for combinations, or insufficient unique subjects for certain factor levels.)")
            print("  Ensure all subjects have data for all combinations of feedback_type and episode_num, or handle missing data appropriately (e.g., imputation).")


def start_anova_analyzer():
    """
    ANOVA 분석기의 시작 지점으로, 데이터를 로드하고 분석을 수행합니다.
    """
    # Assuming 'experiment_data' is in the current working directory, or adjust path as needed.
    base_data_dir = "Python/data_analysis/experiment_data" 

    df_for_anova = load_all_episode_data_for_anova(base_data_dir)
    
    if not df_for_anova.empty:
        perform_anova_analysis_pingouin(df_for_anova)
    else:
        print("Exiting ANOVA analyzer due to no data.")
        sys.exit(0)

if __name__ == "__main__":
    start_anova_analyzer()