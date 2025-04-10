from flask import Flask, render_template, request, redirect, session, jsonify
import json
import os
from utils import haversine

app = Flask(__name__)
app.secret_key = 'supersecret'

USERS = {
    'admin': {'password': 'adminpass', 'role': 'admin'},
    'user': {'password': 'userpass', 'role': 'user'}
}

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        user = USERS.get(uname)
        if user and user['password'] == pwd:
            session['user'] = uname
            session['role'] = user['role']
            return redirect('/user_map' if user['role'] == 'user' else '/admin_map')
        return "Invalid credentials", 403
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