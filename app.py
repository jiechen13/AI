from flask import Flask, render_template_string, request, redirect
import pandas as pd

from engine import load_data, calculate_weights, generate_numbers, generate_second_zone
from backtest import rolling_backtest, build_group_df, second_zone_backtest

app = Flask(__name__)

DATA_PATH = "data/history.csv"

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>

body {
    font-family: -apple-system, BlinkMacSystemFont;
    background-color: #f4f6f9;
    margin: 15px;
}

h1 {
    text-align: center;
}

.card {
    background: white;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

button {
    width: 100%;
    padding: 12px;
    background: #007aff;
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 16px;
}

input {
    width: 100%;
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 8px;
    border: 1px solid #ccc;
}

ul {
    padding-left: 15px;
}

.small {
    font-size: 14px;
    color: #666;
}

</style>
</head>

<body>

<h1>AI選號系統 V6</h1>

<div class="card">
<h3>📌 最新一期</h3>
<p>
第一區：{{latest_zone1}}<br>
第二區：{{latest_zone2}}
</p>
</div>

<div class="card">
<h3>➕ 新增一期</h3>
<form method="post" action="/add" onsubmit="return confirmSubmit()">
第一區（6碼逗號分隔）：
<input name="zone1" required>

第二區（1-8）：
<input name="zone2" required>

<button type="submit">新增資料</button>
</form>
</div>

<div class="card">
<h3>📊 模式：{{mode}}</h3>

<h4>群權重</h4>
<ul>
{% for g,w in weights.items() %}
<li>{{g}} : {{w}}</li>
{% endfor %}
</ul>
</div>

<div class="card">
<h3>🎯 10組建議號</h3>
<ul>
{% for row in numbers %}
<li>{{row}}</li>
{% endfor %}
</ul>

<h4>第二區建議號：{{second}}</h4>
</div>

<div class="card">
<h3>📈 回測數據</h3>
平均命中：{{avg}}<br>
中2比例：{{hit2}}<br>
中3比例：{{hit3}}<br>
波動標準差：{{std}}<br>
第二區命中率：{{second_rate}}
<p class="small">（第二區理論隨機基準 0.125）</p>
</div>

<script>
function confirmSubmit() {
    return confirm("確認新增這一期資料？");
}
</script>

</body>
</html>
"""

@app.route("/")
def index():

    df_raw = load_data()

    if len(df_raw) == 0:
        return "尚未有歷史資料"

    df_group = build_group_df(df_raw)

    # 最新一期（安全 iloc）
    latest_row = df_raw.iloc[-1]
    latest_zone1 = list(latest_row.iloc[:-1])
    latest_zone2 = latest_row.iloc[-1]

    # 自動模式判斷
    recent = df_group.tail(5)
    dominance_score = sum(1 for _, row in recent.iterrows() if row.max() >= 3)

    if dominance_score >= 2:
        mode = "aggressive"
    else:
        mode = "stable"

    weights = calculate_weights(df_group, mode=mode)
    numbers = [generate_numbers(weights) for _ in range(10)]
    second_zone = generate_second_zone(df_raw, mode=mode)

    avg_hit, hit2_rate, hit3_rate, std_dev = rolling_backtest(df_raw, mode=mode)
    second_hit_rate = second_zone_backtest(df_raw, mode=mode)

    return render_template_string(
        HTML,
        weights=weights,
        numbers=numbers,
        second=second_zone,
        avg=avg_hit,
        hit2=hit2_rate,
        hit3=hit3_rate,
        std=std_dev,
        second_rate=second_hit_rate,
        mode=mode,
        latest_zone1=latest_zone1,
        latest_zone2=latest_zone2
    )


@app.route("/add", methods=["POST"])
def add_data():

    zone1 = request.form.get("zone1")
    zone2 = request.form.get("zone2")

    if not zone1 or not zone2:
        return "輸入不完整"

    try:
        numbers = [int(x.strip()) for x in zone1.split(",")]

        if len(numbers) != 6:
            return "第一區必須6個號碼"

        second = int(zone2)

        if second < 1 or second > 8:
            return "第二區必須1-8"

        new_row = numbers + [second]

        df = pd.read_csv(DATA_PATH)
        df.loc[len(df)] = new_row
        df.to_csv(DATA_PATH, index=False)

    except:
        return "格式錯誤，請確認輸入為數字"

    return redirect("/")

if __name__ == "__main__":
        app.run()

   
