from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Hardcoded users
admin_credentials = {'janani': '14062006'}
user_credentials = {
    'boobesh': '7010818371',
    'janani': '9884038287',
    'kaviya': '8778540191'
}

# Initialize database
def init_db():
    conn = sqlite3.connect('questions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS questions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, option1 TEXT, option2 TEXT, option3 TEXT, option4 TEXT, answer TEXT, category TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, mail TEXT, category TEXT, marks INTEGER)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']

        if userid in admin_credentials and admin_credentials[userid] == password:
            return redirect(url_for('admin'))
        elif userid in user_credentials and user_credentials[userid] == password:
            return redirect(url_for('user'))
        else:
            return "Invalid Credentials. Please try again."
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = sqlite3.connect('questions.db')
    c = conn.cursor()
    if request.method == 'POST':
        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']
        category = request.form['category']
        c.execute('INSERT INTO questions (question, option1, option2, option3, option4, answer, category) VALUES (?, ?, ?, ?, ?, ?, ?)',
                  (question, option1, option2, option3, option4, answer, category))
        conn.commit()
    c.execute('SELECT name, mail, category, marks FROM users')
    users = c.fetchall()
    conn.close()
    return render_template('admin.html', users=users)

@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        name = request.form['name']
        mail = request.form['mail']
        category = request.form['category']
        conn = sqlite3.connect('questions.db')
        c = conn.cursor()
        c.execute('SELECT * FROM questions WHERE category=?', (category,))
        questions = c.fetchall()
        conn.close()
        return render_template('questions.html', questions=questions, name=name, mail=mail, category=category)
    return render_template('user.html')

@app.route('/questions', methods=['POST'])
def questions():
    name = request.form['name']
    mail = request.form['mail']
    category = request.form['category']
    answers = dict(request.form)
    answers.pop('name', None)
    answers.pop('mail', None)
    answers.pop('category', None)

    conn = sqlite3.connect('questions.db')
    c = conn.cursor()
    marks = 0
    for qid, selected in answers.items():
        c.execute('SELECT answer FROM questions WHERE id=?', (qid,))
        correct_answer = c.fetchone()
        if correct_answer and selected == correct_answer[0]:
            if category == 'easy':
                marks += 1
            elif category == 'medium':
                marks += 2
            elif category == 'hard':
                marks += 5
    c.execute('INSERT INTO users (name, mail, category, marks) VALUES (?, ?, ?, ?)', (name, mail, category, marks))
    conn.commit()
    conn.close()

    return render_template('result.html', marks=marks, name=name)

@app.route('/clear_questions/<category>')
def clear_questions(category):
    conn = sqlite3.connect('questions.db')
    c = conn.cursor()
    c.execute('DELETE FROM questions WHERE category=?', (category,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/clear_users')
def clear_users():
    conn = sqlite3.connect('questions.db')
    c = conn.cursor()
    c.execute('DELETE FROM users')
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == "__main__":
    app.run(debug=True)
