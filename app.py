from flask import Flask, render_template, request
import sqlite3
import pandas as pd
import requests

app = Flask(__name__)

dataset = "https://raw.githubusercontent.com/Siddharth1698/Coursera-Course-Dataset/master/UCoursera_Courses.csv"

def convert(value):
    if isinstance(value, str) and value.endswith('k'):
        return float(value[:-1]) * 1000
    return value


def load_data():
    response = requests.get(dataset)
    data = pd.read_csv()
    data['course_students_enrolled'] = data['course_students_enrolled'].apply(convert)
    conn = sqlite3.connect('courses.db')
    data.to_sql('courses', conn, if_exists='replace', index=False)
    conn.close()



@app.route('/', methods=['GET', 'POST'])
def organization():
    conn = sqlite3.connect('courses.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT course_organization FROM courses")
    organizations = [row[0] for row in cursor.fetchall()]
    org_details = None


    if request.method == 'POST':
        sel_org = request.form['organization']
        cursor.execute(
            "SELECT AVG(course_rating), SUM(course_students_enrolled) FROM courses WHERE course_organization = ?", (sel_org,)
        )
        avg_rating, total_enrolled = cursor.fetchone()
        cursor.execute(
            "SELECT course_difficulty, GROUP_CONCAT(course_title, ', ') FROM courses WHERE course_organization = ? GROUP BY course_difficulty", (sel_org,)
        )

        difficulty_courses = {row[0]: row[1].split(', ') if row[1] else [] for row in cursor.fetchall()}
        
        org_details = {
            'organization': sel_org,
            'avg_rating': round(avg_rating, 2) if avg_rating else 0,
            'total_enrolled': total_enrolled if total_enrolled else 0,
            'difficulty_courses': difficulty_courses
        }
    return render_template('index.html', organizations=organizations, org_details=org_details)



if __name__ == '__main__':
    app.run(debug=True)
