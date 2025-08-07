from flask import Flask, render_template, request, session, redirect, url_for, flash
import random
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '5102'  # セッションを使うために必須

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
        flash('登録が完了しました。ログインしてください。')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            session['correct_count'] = 0
            session['total_count'] = 0
            return redirect(url_for('home'))
        else:
            flash('ユーザー名かパスワードが間違っています。')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
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

        if user_answer:
            is_correct = (user_answer.replace(' ', '') == str(correct_answer).replace(' ', ''))
            if is_correct:
                session['correct_count'] += 1
            result = '正解！' if is_correct else f'不正解。正しい答えは {correct_answer} です。'
        else:
            result = '入力が必要です。'

        accuracy = f"{session['correct_count']} / {session['total_count']}（{(session['correct_count'] / session['total_count'] * 100):.1f}%）"

        return render_template('index.html',
                               question=question,
                               correct_answer=correct_answer,
                               result=result,
                               problem_name=problem_name,
                               accuracy=accuracy,
                               username=session.get('username'))

    else:
        problem_name, question, correct_answer = generate_problem()
        accuracy = None
        if 'total_count' in session and session['total_count'] > 0:
            accuracy = f"{session['correct_count']} / {session['total_count']}（{(session['correct_count'] / session['total_count'] * 100):.1f}%）"

        return render_template('index.html',
                               question=question,
                               correct_answer=correct_answer,
                               result=None,
                               problem_name=problem_name,
                               accuracy=accuracy,
                               username=session.get('username'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/reset')
def reset():
    session.clear()  # セッションの情報をすべて削除（正答率もリセット）
    return redirect(url_for('home'))  # ホーム画面にリダイレクト

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
