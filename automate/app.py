
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd
import os
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shifts.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SECRET_KEY'] = 'secret123'
db = SQLAlchemy(app)
class Employee(db.Model):
 id = db.Column(db.Integer, primary_key=True)
 name = db.Column(db.String(100), nullable=False)
 email = db.Column(db.String(100))
 department = db.Column(db.String(50), nullable=False)
class Shift(db.Model):
 id = db.Column(db.Integer, primary_key=True)
 employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
 start_time = db.Column(db.DateTime, nullable=False)
 end_time = db.Column(db.DateTime, nullable=False)
 department = db.Column(db.String(50), nullable=False)
 employee = db.relationship('Employee', backref=db.backref('shifts', lazy=True))

def get_department_colors():
 return {
'HR': 'blue',
'Finance': 'green',
'Reception': 'red',
'IT': 'purple',
'Support': 'orange',
}

@app.route('/')
def index():
 employees = Employee.query.all()
 shifts = Shift.query.all()
# Gantt chart data
 data = []
 for shift in shifts:
    data.append({
        'Task': f"{shift.employee.name} ({shift.department})",
        'Start': shift.start_time,
        'Finish': shift.end_time,
        'Department': shift.department
    })

 df = pd.DataFrame(data)
 color_map = get_department_colors()
 if not df.empty:
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Department", color_discrete_map=color_map)
    fig.update_yaxes(autorange="reversed")
    gantt_html = fig.to_html(full_html=False)
 else:
    gantt_html = "<p>No shifts to display.</p>"

 return render_template('index.html', employees=employees, shifts=shifts, gantt_html=gantt_html)

@app.route('/add_employee', methods=['POST'])
def add_employee():
 name = request.form['name']
 email = request.form['email']
 dept = request.form['department']
 new_emp = Employee(name=name, email=email, department=dept)
 db.session.add(new_emp)
 db.session.commit()
 return redirect(url_for('index'))
@app.route('/add_shift', methods=['POST'])
def add_shift():
 emp_id = request.form['employee_id']
 start = request.form['start_time']
 end = request.form['end_time']
 dept = request.form['department']
 start_dt = datetime.strptime(start, '%Y-%m-%dT%H:%M')
 end_dt = datetime.strptime(end, '%Y-%m-%dT%H:%M')
 new_shift = Shift(employee_id=emp_id, start_time=start_dt, end_time=end_dt, department=dept)
 db.session.add(new_shift)
 db.session.commit()
 return redirect(url_for('index'))
@app.route('/delete_shift/int:shift_id',methods=['POST'])
def delete_shift(shift_id):
 shift = Shift.query.get_or_404(shift_id)
 db.session.delete(shift)
 db.session.commit()
 return redirect(url_for('index'))
@app.route('/update_employee_department/<int:emp_id>', methods=['POST'])
def update_employee_department(emp_id):
    new_dept = request.form['new_department']
    employee = Employee.query.get_or_404(emp_id)
    employee.department = new_dept
    db.session.commit()
    return redirect(url_for('index'))
@app.route('/calendar_sync')
def calendar_sync():
# Placeholder: Integrate Google Calendar API here
 flash("Google Calendar integration is not configured yet.")
 return redirect(url_for('index'))
if __name__ == '__main__':
 if not os.path.exists(db_path):
  with app.app_context():
   db.create_all()
 app.run(host="0.0.0.0",port=int(os.environ.get('PORT',5000)))
