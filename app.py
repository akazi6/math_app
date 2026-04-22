import os
import random
import json
from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '5102'

USER_FILE = 'users.json'
DATA_FILE = 'user_scores.json'

# --- 1. データ管理用関数 ---
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

users = {}
user_scores = {}

# --- 2. 具体的な問題生成ロジック ---
def generate_addition():
    a, b = random.randint(10, 99), random.randint(10, 99)
    return f"{a} + {b}", a + b

def generate_subtraction():
    a, b = random.randint(10, 99), random.randint(10, 99)
    if b > a: a, b = b, a
    return f"{a} - {b}", a - b

def generate_multiplication():
    a, b = random.randint(10, 99), random.randint(10, 99)
    return f"{a} × {b}", a * b

def generate_division():
    b = random.randint(2, 9)
    ans = random.randint(10, 99)
    return f"{b * ans} ÷ {b}", ans

def generate_linear_equation():
    a, x, b = random.randint(1, 10), random.randint(1, 10), random.randint(0, 20)
    return f"{a}x + {b} = {a * x + b} のときxは？", x

def generate_problem(difficulty='normal'):
    problems = [('足し算', generate_addition), ('引き算', generate_subtraction)]
    if difficulty != 'easy':
        problems += [('掛け算', generate_multiplication), ('割り算', generate_division)]
    if difficulty == 'hard':
        problems += [('方程式', generate_linear_equation)]
    
    name, func = random.choice(problems)
    q, a = func()
    return name, q, a

# --- 3. ルート定義 ---
@app.before_request
def init_data():
    if not users: load_users()
    if not user_scores: load_scores()

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('username'), request.form.get('password')
        if u in users and check_password_hash(users[u], p):
            session['username'] = u
            session['correct_count'] = 0
            session['total_count'] = 0
            return redirect(url_for('home'))
        flash('ログイン失敗')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u, p = request.form.get('username'), request.form.get('password')
        if u and p:
            users[u] = generate_password_hash(p)
            save_users()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    difficulty = request.args.get('difficulty', session.get('difficulty', 'normal'))
    session['difficulty'] = difficulty

    if request.method == 'POST':
        ans, correct, q, name = request.form.get('answer'), request.form.get('correct_answer'), request.form.get('question'), request.form.get('problem_name')
        is_correct = (ans.strip() == str(correct).strip())
        
        session['total_count'] = session.get('total_count', 0) + 1
        if is_correct: session['correct_count'] = session.get('correct_count', 0) + 1
        
        if username not in user_scores: user_scores[username] = {'correct': 0, 'total': 0}
        user_scores[username]['total'] += 1
        if is_correct: user_scores[username]['correct'] += 1
        save_scores()

        res = '正解！' if is_correct else f'不正解。正解は {correct}'
        acc = f"{session['correct_count']} / {session['total_count']}"
        return render_template('index.html', question=q, correct_answer=correct, result=res, problem_name=name, accuracy=acc, username=username, difficulty=difficulty)

    name, q, correct = generate_problem(difficulty)
    acc = f"{session.get('correct_count', 0)} / {session.get('total_count', 0)}"
    return render_template('index.html', question=q, correct_answer=correct, problem_name=name, username=username, accuracy=acc, difficulty=difficulty)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
