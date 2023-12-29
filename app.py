# app.py
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'

# Suppress warning about tracking modifications, which is not needed in this case
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy instance
db = SQLAlchemy(app)

# Define the Entry model
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    date = db.Column(db.String(10), nullable=False)
    distance = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(100), nullable=False)

# Route for handling form submissions
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Get form data
            date = request.form['date']
            distance = request.form['distance']
            time = request.form['time']
            location = request.form['location']

            # Create a new entry and add it to the database
            entry = Entry(date=date, distance=distance, time=time, location=location)
            db.session.add(entry)
            db.session.commit()

            return "Form submitted successfully!"
        except Exception as e:
            # Handle database or form processing errors
            db.session.rollback()
            return f"Error: {str(e)}"

    return render_template('index.html')


# STATS

# Route for handling form submissions
@app.route('/runs/stats', methods=['GET', 'POST'])
def runs_stats():
    return render_template('runs_stats.html')

@app.route('/reads/stats', methods=['GET', 'POST'])
def reads_stats():
    return render_template('reads_stats.html')

@app.route('/trips/stats', methods=['GET', 'POST'])
def trips_stats():
    return render_template('trips_stats.html')

@app.route('/thoughts/stats', methods=['GET', 'POST'])
def thoughts_stats():
    return render_template('thoughts_stats.html')


# HISTORY

# Route for handling form submissions
@app.route('/runs/history', methods=['GET', 'POST'])
def runs_history():
    return render_template('runs_history.html')

@app.route('/reads/history', methods=['GET', 'POST'])
def reads_history():
    return render_template('reads_history.html')

@app.route('/trips/history', methods=['GET', 'POST'])
def trips_history():
    return render_template('trips_history.html')

@app.route('/thoughts/history', methods=['GET', 'POST'])
def thoughts_history():
    return render_template('thoughts_history.html')

# NEW

# Route for handling form submissions
@app.route('/runs/new', methods=['GET', 'POST'])
def runs_new():
    return render_template('runs_new.html')

@app.route('/reads/new', methods=['GET', 'POST'])
def reads_new():
    return render_template('reads_new.html')

@app.route('/trips/new', methods=['GET', 'POST'])
def trips_new():
    return render_template('trips_new.html')

@app.route('/thoughts/new', methods=['GET', 'POST'])
def thoughts_new():
    return render_template('thoughts_new.html')


if __name__ == '__main__':
    # Create the database tables before running the app
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully.")
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")

    # Run the Flask app in debug mode
    app.run(debug=True)
