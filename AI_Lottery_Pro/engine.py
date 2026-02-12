import pandas as pd
import numpy as np
import random


def load_data(path="data/history.csv"):
    return pd.read_csv(path)


# ==============================
# 群策略強化
# ==============================

def apply_transition_boost(weights, df):
    last_row = df.iloc[-1]

    transition_map = {
        "A": "B",
        "B": "C",
        "C": "A"
    }

    dominant_group = last_row.idxmax()

    if dominant_group in transition_map:
        target = transition_map[dominant_group]
        weights[target] *= 1.25

    return weights


def apply_cold_rebound(weights, df):
    last3 = df.tail(3)

    for g in weights.keys():
        if last3[g].mean() <= 1:
            weights[g] *= 1.1

    return weights


def apply_overheat_suppression(weights, df):
    last_row = df.iloc[-1]

    for g in weights.keys():
        if last_row[g] >= 3:
            weights[g] *= 0.85

    return weights


# ==============================
# 計算群權重（雙模式）
# ==============================

def calculate_weights(df, mode="stable"):

    last30 = df.tail(30)
    last10 = df.tail(10)

    weights = {}

    for g in ["A","B","C","D","E"]:

        avg30 = last30[g].mean()
        avg10 = last10[g].mean()
        momentum = avg10 - avg30

        if mode == "stable":
            weight = avg30*0.4 + avg10*0.4 + momentum*0.2
        else:
            weight = avg30*0.1 + avg10*0.7 + momentum*0.4

        weights[g] = max(weight, 0.0001)

    weights = apply_transition_boost(weights, df)
    weights = apply_cold_rebound(weights, df)
    weights = apply_overheat_suppression(weights, df)

    total = sum(weights.values())
    weights = {g: w/total for g,w in weights.items()}

    return weights


# ==============================
# 第一區生成
# ==============================

def generate_numbers(weights):

    groups = list(weights.keys())
    probs = np.array(list(weights.values()))
    probs = probs / probs.sum()

    pool = {
        "A":[2,10,12,20,22,30,32],
        "B":[4,5,14,15,24,25,34,35],
        "C":[6,8,16,18,26,28,36,38],
        "D":[1,7,11,17,21,27,31,37],
        "E":[3,9,13,19,23,29,33]
    }

    while True:

        numbers = set()
        used_groups = set()

        while len(numbers) < 6:
            g = np.random.choice(groups, p=probs)
            n = random.choice(pool[g])
            numbers.add(n)
            used_groups.add(g)

        numbers = sorted(numbers)

        small = sum(1 for n in numbers if n <= 19)

        if small != 3:
            continue

        if not (3 <= len(used_groups) <= 4):
            continue

        return numbers


# ==============================
# 第二區生成
# ==============================

def generate_second_zone(df_raw, mode="stable"):

    second_col = df_raw.columns[-1]

    last20 = df_raw.tail(20)[second_col]
    last5 = df_raw.tail(5)[second_col]

    scores = {}

    for num in range(1,9):

        freq20 = sum(last20 == num)
        freq5 = sum(last5 == num)

        if mode == "stable":
            score = freq20*0.6 + freq5*0.4
        else:
            score = freq20*0.4 + freq5*0.7

        scores[num] = score + 0.01

    total = sum(scores.values())
    probs = [v/total for v in scores.values()]

    return int(np.random.choice(list(scores.keys()), p=probs))
