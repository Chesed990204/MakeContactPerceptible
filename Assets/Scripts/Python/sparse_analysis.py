import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import DictionaryLearning
from sklearn.preprocessing import StandardScaler

CSV_FILE = "Python/hand_data/1748339680.463282.csv"

def load_and_sparse_code(filename):
    df = pd.read_csv(filename)
    if len(df) < 10:
        print("Not enough data.")
        return

    data = df[['palm_y', 'palm_v', 'palm_a']].values
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)

    dict_learner = DictionaryLearning(n_components=5, alpha=1.0, max_iter=500)
    sparse_codes = dict_learner.fit_transform(data_scaled)

    # 시각화
    plt.figure(figsize=(10, 6))
    for i in range(sparse_codes.shape[1]):
        plt.plot(sparse_codes[:, i], label=f'Component {i+1}')
    plt.title("Sparse Codes from Palm Motion")
    plt.xlabel("Time Index")
    plt.ylabel("Activation")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    load_and_sparse_code(CSV_FILE)