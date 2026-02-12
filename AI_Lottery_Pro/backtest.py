import numpy as np
from engine import calculate_weights, generate_numbers, generate_second_zone


# ==============================
# 建立群統計
# ==============================

def build_group_df(df_raw):

    first_zone = df_raw.iloc[:, :-1]

    return first_zone.apply(lambda row: {
        "A": sum((row % 10).isin([0,2])),
        "B": sum((row % 10).isin([4,5])),
        "C": sum((row % 10).isin([6,8])),
        "D": sum((row % 10).isin([1,7])),
        "E": sum((row % 10).isin([3,9]))
    }, axis=1, result_type="expand")


# ==============================
# 第一區回測（200次模擬）
# ==============================

def rolling_backtest(df_raw, mode="stable"):

    if len(df_raw) < 50:
        return 0,0,0,0

    hits = []
    total_sim = 0
    total_hit2 = 0
    total_hit3 = 0

    for i in range(30, len(df_raw)-1):

        train_raw = df_raw.iloc[:i]
        test = df_raw.iloc[i]

        train_group = build_group_df(train_raw)
        weights = calculate_weights(train_group, mode=mode)

        for _ in range(200):

            prediction = generate_numbers(weights)

            overlap = len(set(prediction) & set(test.iloc[:-1]))

            hits.append(overlap)
            total_sim += 1

            if overlap >= 2:
                total_hit2 += 1
            if overlap >= 3:
                total_hit3 += 1

    if total_sim == 0:
        return 0,0,0,0

    model_avg = np.mean(hits)
    std_dev = np.std(hits)

    hit2_rate = total_hit2 / total_sim
    hit3_rate = total_hit3 / total_sim

    return round(model_avg,4), round(hit2_rate,4), round(hit3_rate,4), round(std_dev,4)


# ==============================
# 第二區回測（單次真實預測版）
# ==============================

def second_zone_backtest(df_raw, mode="stable"):

    if len(df_raw) < 50:
        return 0

    hit = 0
    total = 0

    for i in range(30, len(df_raw)-1):

        train = df_raw.iloc[:i]

        # 正確取得第 i 期第二區（最後一欄）
        actual_second = df_raw.iloc[i, -1]

        # 每期只預測一次（真實策略）
        pred_second = generate_second_zone(train, mode=mode)

        if pred_second == actual_second:
            hit += 1

        total += 1

    if total == 0:
        return 0

    rate = hit / total

    return round(rate,4)
