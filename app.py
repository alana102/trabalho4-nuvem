import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

def get_db_connection():
    # Puxa as variáveis que configuramos no arquivo .env / docker-compose
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        port='5432'
    )
    return conn

def init_db():
    # Cria a tabela de tarefas automaticamente se ela não existir no RDS
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            title VARCHAR(150) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, title FROM todos ORDER BY created_at DESC;')
    todos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add_todo():
    title = request.form.get('title')
    if title:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO todos (title) VALUES (%s);', (title,))
        conn.commit()
        cur.close()
        conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000)