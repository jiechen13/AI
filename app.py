from flask import Flask, render_template_string
import pandas as pd
import os
import random

app = Flask(__name__)

# ===============================
# 讀取資料（極簡）
# ===============================
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(BASE_DIR, "data", "history.csv")

    df = pd.read_csv(path)

    # 如果沒有 second 欄位，自動補
    if "second" not in df.columns:
        df["second"] = 1

    return df


# ===============================
# 群分類
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
# 計算簡化權重（只看近20期）
# ===============================
def calculate_weights(df):

    recent = df.tail(20)

    groups = ["A", "B", "C", "D", "E"]
    weights = {}

    for g in groups:
        count = 0
        for _, row in recent.iterrows():
            nums = row.iloc[:6]
            count += sum(1 for n in nums if classify_group(n) == g)

        weights[g] = count + 1  # 防止0

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
# HTML（極簡手機版）
# ===============================
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {
    font-family: -apple-system;
    background: #f4f6f9;
    padding: 15px;
}
.card {
    background: white;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 15px;
}
button {
    width: 100%;
    padding: 12px;
    border: none;
    background: #007aff;
    color: white;
    border-radius: 8px;
    font-size: 16px;
}
</style>
</head>
<body>

<h2>AI選號系統 Free 穩定版</h2>

<div class="card">
<h3>群權重</h3>
<ul>
{% for g,w in weights.items() %}
<li>{{g}} : {{w}}</li>
{% endfor %}
</ul>
</div>

<div class="card">
<h3>建議號碼</h3>
<p>{{numbers}}</p>
</div>

</body>
</html>
"""


@app.route("/")
def index():

    df = load_data()
    weights = calculate_weights(df)
    numbers = generate_numbers(weights)

    return render_template_string(
        HTML,
        weights=weights,
        numbers=numbers
    )


if __name__ == "__main__":
    app.run()
