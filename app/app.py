from flask import Flask, render_template, request, redirect, url_for
import pymysql
import pymysql.cursors
import os

app = Flask(__name__)

def get_db():
    return pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'todo_user'),
        password=os.environ.get('MYSQL_PASSWORD', 'todo_pass'),
        database=os.environ.get('MYSQL_DB', 'tododb'),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM todos ORDER BY created_at DESC")
    todos = cur.fetchall()
    conn.close()
    total   = len(todos)
    done    = sum(1 for t in todos if t['done'])
    pending = total - done
    return render_template('index.html', todos=todos, total=total, done=done, pending=pending)

@app.route('/add', methods=['POST'])
def add():
    task = request.form.get('task', '').strip()
    if task:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO todos (task) VALUES (%s)", (task,))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/done/<int:todo_id>')
def toggle_done(todo_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE todos SET done = NOT done WHERE id = %s", (todo_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/health')
def health():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)