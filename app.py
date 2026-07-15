import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DB_FILE = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Access columns by name like dictionary
    return conn

# Initialize Database and Tables
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Students Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    
    # Instructors Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instructors (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
    ''')
    
    # Courses Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            instructor_id TEXT,
            FOREIGN KEY (instructor_id) REFERENCES instructors(id)
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

# --- API Endpoints ---

# Students
@app.route('/api/students', methods=['GET', 'POST'])
def handle_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        try:
            cursor.execute("INSERT INTO students (id, name, email) VALUES (?, ?, ?)",
                           (data['id'], data['name'], data['email']))
            conn.commit()
            return jsonify({"message": "Student added successfully!"}), 201
        except sqlite3.IntegrityError:
            return jsonify({"error": "Student ID already exists!"}), 400
        finally:
            conn.close()
            
    # GET Request
    students = cursor.execute("SELECT * FROM students").fetchall()
    conn.close()
    return jsonify([dict(row) for row in students])

# Instructors
@app.route('/api/instructors', methods=['GET', 'POST'])
def handle_instructors():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        try:
            cursor.execute("INSERT INTO instructors (id, name, department) VALUES (?, ?, ?)",
                           (data['id'], data['name'], data['department']))
            conn.commit()
            return jsonify({"message": "Instructor added successfully!"}), 201
        except sqlite3.IntegrityError:
            return jsonify({"error": "Instructor ID already exists!"}), 400
        finally:
            conn.close()
            
    instructors = cursor.execute("SELECT * FROM instructors").fetchall()
    conn.close()
    return jsonify([dict(row) for row in instructors])

# Courses
@app.route('/api/courses', methods=['GET', 'POST'])
def handle_courses():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        try:
            cursor.execute("INSERT INTO courses (code, name, instructor_id) VALUES (?, ?, ?)",
                           (data['code'], data['name'], data.get('instructor_id')))
            conn.commit()
            return jsonify({"message": "Course added successfully!"}), 201
        except sqlite3.IntegrityError:
            return jsonify({"error": "Course Code already exists!"}), 400
        finally:
            conn.close()
            
    # Fetch courses with their instructor's name using a SQL JOIN
    courses = cursor.execute('''
        SELECT courses.code, courses.name, instructors.name AS instructor_name 
        FROM courses 
        LEFT JOIN instructors ON courses.instructor_id = instructors.id
    ''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in courses])

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)