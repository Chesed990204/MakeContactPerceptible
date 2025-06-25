import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import wilcoxon, ttest_rel, shapiro

# 조건별 폴더 이름
DATA_DIRS = {
    "with_haptics": "Python\\hand_data\\with_haptics",
    "with_adaptive_haptics": "Python\\hand_data\\with_adaptive_haptics"
}

# 조건별 maxZ 값 저장
condition_trials = {cond: [] for cond in DATA_DIRS.keys()}

def test_normality(data, label):
    stat, p = shapiro(data)
    print(f"\nShapiro-Wilk Test for '{label}':")
    print(f"  W-statistic = {stat:.9f}, p-value = {p:.9f}")
    if p < 0.05:
        print(f"  → '{label}'는 정규성을 따르지 않습니다 (p < 0.05)")
    else:
        print(f"  → '{label}'는 정규성을 따른다고 볼 수 있습니다 (p ≥ 0.05)")
    return stat, p

for cond, path in DATA_DIRS.items():
    csv_files = sorted(glob.glob(os.path.join(path, "*.csv")))
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            if "maxZ" in df.columns:
                condition_trials[cond].append(df["maxZ"].max())
            else:
                print(f"'maxZ' column not found in {file}")
        except Exception as e:
            print(f"Error reading {file}: {e}")

cond1, cond2 = list(DATA_DIRS.keys())
trials_A = condition_trials[cond1]
trials_B = condition_trials[cond2]

# 길이 맞추기
min_len = min(len(trials_A), len(trials_B))
if min_len == 0:
    print("하나 이상의 조건에서 trial 수가 0입니다.")
    exit()

trials_A = trials_A[:min_len]
trials_B = trials_B[:min_len]

test_normality(trials_A, cond1)
test_normality(trials_B, cond2)

# 평균과 표준편차
mean_A = np.mean(trials_A)
std_A = np.std(trials_A)
mean_B = np.mean(trials_B)
std_B = np.std(trials_B)

print(f"\n통계 요약:")
print(f"{cond1}: 평균 = {mean_A:.9f}, 표준편차 = {std_A:.9f}")
print(f"{cond2}: 평균 = {mean_B:.9f}, 표준편차 = {std_B:.9f}")

# Wilcoxon Test
stat_w, p_w = wilcoxon(trials_A, trials_B)
print(f"\nWilcoxon Signed-Rank Test:")
print(f"Statistic = {stat_w:.9f}, p-value = {p_w:.9f}")
if p_w < 0.05:
    print("→ 유의미한 차이가 있습니다 (p < 0.05)")
else:
    print("→ 유의미한 차이가 없습니다 (p ≥ 0.05)")


# 시각화
fig, axs = plt.subplots(1, 2, figsize=(12, 5))

# Boxplot
axs[0].boxplot([trials_A, trials_B], labels=[cond1, cond2])
axs[0].set_title("Max Index Z - Boxplot")
axs[0].set_ylabel("Max Z")
axs[0].annotate(f"Wilcoxon p = {p_w:.5f}",
                xy=(1.5, max(max(trials_A), max(trials_B))),
                ha='center', fontsize=10)
axs[0].grid(True)

# Histogram
axs[1].hist(trials_A, bins=10, alpha=0.6, label=f"{cond1} (M={mean_A:.5f}, SD={std_A:.5f})")
axs[1].hist(trials_B, bins=10, alpha=0.6, label=f"{cond2} (M={mean_B:.5f}, SD={std_B:.5f})")
axs[1].set_title("Max Index Z - Distribution")
axs[1].set_xlabel("Max Z")
axs[1].set_ylabel("Frequency")
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()
plt.show()
