import numpy as np
from engine import generate_numbers, calculate_weights


# ===============================
# 第一區回測
# ===============================
def rolling_backtest(df, mode="aggressive"):
    hits = []
    hit2 = 0
    hit3 = 0

    for i in range(30, len(df)):
        train = df.iloc[:i]
        test = df.iloc[i]

        weights = calculate_weights(train, mode=mode)
        pred = generate_numbers(weights)

        actual = test[:6].tolist()

        h = len(set(pred) & set(actual))
        hits.append(h)

        if h >= 2:
            hit2 += 1
        if h >= 3:
            hit3 += 1

    avg_hit = np.mean(hits)
    hit2_rate = hit2 / len(hits)
    hit3_rate = hit3 / len(hits)
    std_dev = np.std(hits)

    return avg_hit, hit2_rate, hit3_rate, std_dev


# ===============================
# 第二區回測
# ===============================
def second_zone_backtest(df):
    hits = 0
    total = 0

    for i in range(30, len(df)):
        train = df.iloc[:i]
        test = df.iloc[i]

        from engine import generate_second
        pred_second = generate_second(train)

        actual_second = test["second"] if "second" in df.columns else 1

        if pred_second == actual_second:
            hits += 1

        total += 1

    if total == 0:
        return 0

    return hits / total
