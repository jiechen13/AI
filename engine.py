import pandas as pd
import numpy as np
import os
import random

print("engine version v5 loaded")

# ===============================
# 讀取資料（自動判斷 second 是否存在）
# ===============================
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(BASE_DIR, "data", "history.csv")

    df = pd.read_csv(path)

    # 如果沒有 second 欄位，自動補 1
    if "second" not in df.columns:
        df["second"] = 1

    return df


# ===============================
# 群判定
# ===============================
def classify_group(num):
    tail = num % 10

    if tail in [0, 2]:
        return "A"
    elif tail in [4, 5]:
        return "B"
    elif tail in [6, 8]:
        return "C"
    elif tail in [1, 3]:
        return "D"
    else:
        return "E"


# ===============================
# 計算權重（支援 mode）
# ===============================
def calculate_weights(df, mode="aggressive"):
    recent30 = df.tail(30)
    recent10 = df.tail(10)

    groups = ["A", "B", "C", "D", "E"]
    weights = {}

    for g in groups:
        count30 = 0
        count10 = 0

        for _, row in recent30.iterrows():
            nums = row[:6]
            count30 += sum(1 for n in nums if classify_group(n) == g)

        for _, row in recent10.iterrows():
            nums = row[:6]
            count10 += sum(1 for n in nums if classify_group(n) == g)

        avg30 = count30 / (30 * 6)
        avg10 = count10 / (10 * 6)

        momentum = avg10 - avg30

        if mode == "aggressive":
            weight = avg10 + momentum
        else:
            weight = avg30 * 0.7 + avg10 * 0.3

        weights[g] = max(weight, 0.01)

    total = sum(weights.values())
    for k in weights:
        weights[k] /= total

    return weights


# ===============================
# 產生號碼（無重複）
# ===============================
def generate_numbers(weights):
    numbers = list(range(1, 39))
    groups = [classify_group(n) for n in numbers]

    probs = [weights[g] for g in groups]

    selected = set()
    while len(selected) < 6:
        selected.add(random.choices(numbers, probs)[0])

    return sorted(selected)


# ===============================
# 第二區推薦
# ===============================
def generate_second(df):
    recent20 = df.tail(20)

    counts = {}
    for n in range(1, 9):
        counts[n] = sum(recent20["second"] == n)

    best = max(counts, key=counts.get)
    return best
