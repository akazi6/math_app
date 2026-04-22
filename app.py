import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
import random
import json  # インポートは一番上にまとめるのがベスト
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '5102'

USER_FILE = 'users.json'
DATA_FILE = 'user_scores.json'

# --- データ管理用関数 ---
def load_users():
    global users
    try:
        with open(USER_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}

def save_users():
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_scores():
    global user_scores
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            user_scores = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        user_scores = {}

def save_scores():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_scores, f, ensure_ascii=False, indent=2)

# 初期化
users = {}
user_scores = {}

# --- 問題生成ロジック (省略せず保持) ---
# ... (generate_multiplicationなどの関数群) ...
# ※ここにお手持ちの generate_... 関数をすべて入れてください

def generate_problem(difficulty='normal'):
    easy_problems = [('足し算', generate_addition), ('引き算', generate_subtraction)]
    normal_problems = easy_problems + [
        ('掛け算', generate_multiplication), ('割り算', generate_division),
        ('比例', generate_proportional), ('反比例', generate_inverse_proportional)
    ]
    hard_problems = normal_problems + [
        ('一次方程式', generate_linear_equation), ('因数分解', generate_factoring),
        ('2次方程式', generate_quadratic_equation)
    ]
    
    if difficulty == 'easy':
        problem_types = easy_problems
    elif difficulty == 'hard':
        problem_types = hard_problems
    else:
        problem_types = normal_problems

    problem_name, func = random.choice(problem_types)
    question, answer = func()
    return problem_name, question, answer

# --- ルート定義 ---
@app.before_request
def load_data_once():
    if not users:
        load_users()
    if not user_scores:
        load_scores()

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    # ...登録処理...
    return render_template('register.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    difficulty = session.get('difficulty', 'normal')

    if request.method == 'POST':
        user_answer = request.form.get('answer')
        correct_answer = request.form.get('correct_answer')
        question = request.form.get('question')
        problem_name = request.form.get('problem_name')

        session['total_count'] = session.get('total_count', 0) + 1
        is_correct = False

        try:
            # 2次方程式などのセット比較ロジック
            if correct_answer.startswith("{"):
                correct_set = set(map(int, correct_answer.strip("{}").split(",")))
                user_set = set(int(x.replace('x', '').replace('=', '').strip()) for x in user_answer.replace('または', ',').split(','))
                is_correct = (user_set == correct_set)
            else:
                is_correct = (user_answer.replace(' ', '') == correct_answer.replace(' ', ''))
        except:
            is_correct = False

        if is_correct:
            session['correct_count'] = session.get('correct_count', 0) + 1

        # スコア保存処理
        if username not in user_scores:
            user_scores[username] = {'correct': 0, 'total': 0}
        user_scores[username]['total'] += 1
        if is_correct:
            user_scores[username]['correct'] += 1
        save_scores()

        result = '正解！' if is_correct else f'不正解。正しい答えは {correct_answer} です。'
        accuracy = f"{session['correct_count']} / {session['total_count']}（{(session['correct_count'] / session['total_count'] * 100):.1f}%）"

        return render_template('index.html', question=question, correct_answer=correct_answer, 
                               result=result, problem_name=problem_name, accuracy=accuracy, 
                               username=username, difficulty=difficulty)

    # GET時の処理
    difficulty = request.args.get('difficulty', difficulty)
    session['difficulty'] = difficulty
    problem_name, question, correct_answer = generate_problem(difficulty)
    
    return render_template('index.html', question=question, correct_answer=correct_answer, 
                           problem_name=problem_name, username=username, difficulty=difficulty)

# ... (register, login, logout, ranking などの他のルートはそのまま) ...

if __name__ == '__main__':
    # Renderなどの環境変数のポートを読み込み、なければ5000を使う
    port = int(os.environ.get("PORT", 5000))
    # host='0.0.0.0' は外部からのアクセスを許可するために必須です
    app.run(host='0.0.0.0', port=port)
