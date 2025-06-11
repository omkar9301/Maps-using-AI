from flask import Flask, render_template, request, redirect, session, jsonify,flash
import json
import os
from utils import haversine
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'supersecret'

def create_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('admin', 'user'))
        )
    ''')

    conn.commit()
    conn.close()

create_database()

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row  # This lets you use dict-like access: user['email']
    return conn


@app.route('/')
def home():
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone_number = request.form['phone_number']
        role = request.form['role']

        if not username or not password or not email or not phone_number or not role:
            flash('All fields including role are required!')
            return redirect('/register')

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO users (username, password, email, phone_number, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, hashed_password, email, phone_number, role))
            conn.commit()
            flash('Registration successful! You can now log in.')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Username or email already exists.')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if not username or not password or not role:
            flash('All fields including role are required!')
            return redirect('/login')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND role = ?', (username, role)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login successful!')

            if user['role'] == 'admin':
                return redirect('/admin_map')
            else:
                return redirect('/user_map')
        else:
            flash('Invalid credentials or role mismatch.')

    return render_template('login.html')



@app.route('/user_map')
def user_map():
    if session.get('role') != 'user':
        return redirect('/login')
    return render_template('user_map.html')

@app.route('/admin_map')
def admin_map():
    if session.get('role') != 'admin':
        return redirect('/login')
    return render_template('admin_map.html')

@app.route('/api/hazards')
def get_hazards():
    with open('data/hazards.json') as f:
        hazards = json.load(f)
    return jsonify(hazards)

@app.route('/api/nearby', methods=['POST'])
def check_nearby():
    user_lat = float(request.json['lat'])
    user_lng = float(request.json['lng'])
    nearby = []
    with open('data/hazards.json') as f:
        hazards = json.load(f)
    for hazard in hazards:
        dist = haversine(user_lat, user_lng, hazard['lat'], hazard['lng'])
        if dist <= 500:
            nearby.append(hazard)
    return jsonify(nearby)

@app.route('/add_hazard', methods=['POST'])
def add_hazard():
    new = request.json
    with open('data/hazards.json') as f:
        hazards = json.load(f)
    hazards.append(new)
    with open('data/hazards.json', 'w') as f:
        json.dump(hazards, f, indent=2)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)