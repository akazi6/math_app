from flask import Flask, render_template, request, session, redirect, url_for, flash
import random
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '5102'  # セッションを使うために必須

USER_FILE = 'users.json'

def load_users():
    global users
    try:
        with open(USER_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}

def save_users():
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

import json

# ファイル名は自由に決めてOK
DATA_FILE = 'user_scores.json'

def save_scores():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_scores, f, ensure_ascii=False, indent=2)

def load_scores():
    global user_scores
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            user_scores = json.load(f)
    except FileNotFoundError:
        user_scores = {}

# 簡易ユーザーDB（本番ではDBを使うべき）
users = {
    'user1': generate_password_hash('password1'),
    'user2': generate_password_hash('password2'),
}

# ユーザーごとの成績管理（本来はDB）
user_scores = {}
def generate_multiplication():
    a = random.randint(10, 99)
    b = random.randint(10, 99)
    question = f"{a} × {b}"
    answer = a * b
    return question, answer

# アプリの冒頭付近に追加（user_scoresのところ）

user_scores = {}  # 例：{'user1': {'correct': 10, 'total': 15}, ...}

def generate_proportional():
    k = random.randint(1, 10)
    x = random.randint(1, 20)
    y = k * x
    question = f"y = {k}x のとき、x = {x} のときの y の値は？"
    answer = y
    return question, answer

def generate_inverse_proportional():
    k = random.randint(1, 100)
    x = random.randint(1, 20)
    y = k // x  # 整数にしたいので割り切れるように工夫
    k = y * x   # kを再計算して整数解に調整
    question = f"y = {k} ÷ x のとき、x = {x} のときの y の値は？"
    answer = y
    return question, answer

def generate_addition():
    a = random.randint(10, 99)
    b = random.randint(10, 99)
    question = f"{a} + {b}"
    answer = a + b
    return question, answer

def generate_subtraction():
    a = random.randint(10, 99)
    b = random.randint(10, 99)
    # 引き算は必ず正の答えになるよう調整
    if b > a:
        a, b = b, a
    question = f"{a} - {b}"
    answer = a - b
    return question, answer

def generate_division():
    b = random.randint(1, 9)  # 割る数は1〜9
    answer = random.randint(10, 99)
    a = b * answer  # 割り切れる数を作る
    question = f"{a} ÷ {b}"
    return question, answer

import random

def generate_linear_equation():
    # 例: ax + b = c の形でxを求める問題
    a = random.randint(1, 10)
    b = random.randint(0, 20)
    x = random.randint(1, 10)
    c = a * x + b
    question = f"{a}x + {b} = {c} のとき、xの値は？"
    answer = x
    return question, answer  # ✅ これで他と統一！

def generate_factoring():
    # (x + m)(x + n) の形で作り、展開して問題にする
    m = random.randint(1, 9)
    n = random.randint(1, 9)
    a = 1
    b = m + n
    c = m * n
    question = f"x² + {b}x + {c} を因数分解しなさい。"
    answer = f"(x + {m})(x + {n})" if m <= n else f"(x + {n})(x + {m})"  # 並び順を統一
    return question, answer

def generate_quadratic_equation():
    # (x + m)(x + n) = 0 形式で因数分解できる2次方程式を作成
    m = random.randint(-10, 10)
    n = random.randint(-10, 10)
    while m == 0 or n == 0:  # 0は避ける
        m = random.randint(-10, 10)
        n = random.randint(-10, 10)
    a = 1
    b = m + n
    c = m * n
    question = f"x² + {b}x + {c} = 0 の解を求めよ。"
    answer = f"x = {-m} または x = {-n}"
    return question, answer

def generate_problem():
    problem_types = [
        ('足し算', generate_addition),
        ('引き算', generate_subtraction),
        ('掛け算', generate_multiplication),
        ('割り算', generate_division),
        ('一次方程式', generate_linear_equation),
        ('因数分解', generate_factoring),
        ('2次方程式', generate_quadratic_equation),
        ('比例', generate_proportional),             # ← 追加
        ('反比例', generate_inverse_proportional),   # ← 追加
    ]
    problem_name, func = random.choice(problem_types)
    question, answer = func()
    return problem_name, question, answer

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('ユーザー名とパスワードは必須です。')
            return redirect(url_for('register'))

        if username in users:
            flash('このユーザー名は既に使われています。')
            return redirect(url_for('register'))

        # パスワードをハッシュ化して保存
        users[username] = generate_password_hash(password)
        save_users()
        flash('登録が完了しました。ログインしてください。')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f'Login attempt: username={username}, password={password}')
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            session['correct_count'] = 0
            session['total_count'] = 0
            return redirect(url_for('home'))
        else:
            flash('ユーザー名かパスワードが間違っています。')
            return redirect(url_for('login'))
    return render_template('login.html')

scores_loaded = False

@app.before_request
def load_scores_once():
    global scores_loaded
    if not scores_loaded:
        load_scores()
        load_users()
        scores_loaded = True

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    if 'correct_count' not in session:
        session['correct_count'] = 0
        session['total_count'] = 0

    if request.method == 'POST':
        user_answer = request.form.get('answer')
        correct_answer = request.form.get('correct_answer')
        question = request.form.get('question')
        problem_name = request.form.get('problem_name')

        session['total_count'] += 1

        is_correct = False
        if user_answer:
            is_correct = (user_answer.replace(' ', '') == str(correct_answer).replace(' ', ''))
            if is_correct:
                session['correct_count'] += 1
            result = '正解！' if is_correct else f'不正解。正しい答えは {correct_answer} です。'
        else:
            result = '入力が必要です。'

        # ユーザーのスコア更新
        username = session.get('username')
        if username not in user_scores:
            user_scores[username] = {'correct': 0, 'total': 0}

        user_scores[username]['total'] += 1
        if is_correct:
            user_scores[username]['correct'] += 1

        accuracy = f"{session['correct_count']} / {session['total_count']}（{(session['correct_count'] / session['total_count'] * 100):.1f}%）"

        save_scores()

        return render_template('index.html',
                               question=question,
                               correct_answer=correct_answer,
                               result=result,
                               problem_name=problem_name,
                               accuracy=accuracy,
                               username=username)

    # GETリクエストで新しい問題を出題
    problem_name, question, correct_answer = generate_problem()
    return render_template('index.html',
                           question=question,
                           correct_answer=correct_answer,
                           problem_name=problem_name,
                           username=session['username'])

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/reset')
def reset():
    # ユーザー名だけ保持して、他をリセット
    username = session.get('username')  # 一時保存

    session.clear()  # 全部消す

    if username:
        session['username'] = username  # ユーザー名だけ復元

    session['correct_count'] = 0
    session['total_count'] = 0

    return redirect(url_for('home'))

@app.route('/ranking')
def ranking():
    rankings = []
    for username, score in user_scores.items():
        correct = score['correct']
        total = score['total']
        if total == 0:
            accuracy = 0
        else:
            accuracy = correct / total * 100
        rankings.append((username, correct, total, accuracy))

    # 正答率でソート（降順）
    rankings.sort(key=lambda x: x[3], reverse=True)

    return render_template('ranking.html', rankings=rankings)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
