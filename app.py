# app.py
from flask import Flask, render_template, request, redirect, url_for
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

class Reads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_started = db.Column(db.String(20))
    date_ended = db.Column(db.String(20))
    title = db.Column(db.String(50))
    author = db.Column(db.String(50))
    pages = db.Column(db.Integer)
    category = db.Column(db.String(50))
    subcategory = db.Column(db.String(50))
    country = db.Column(db.String(50))
    date_added = db.Column(db.String(50))

with app.app_context():
    db.create_all()

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
    reads = Reads.query.all()
    return render_template('reads_history.html',reads=reads)

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
    if request.method == 'POST':
        try:
            date_started = request.form['date_started']
            date_ended = request.form['date_ended']
            title = request.form['title']
            author = request.form['author']
            pages = request.form['pages']
            category = request.form['category']
            subcategory = request.form['subcategory']
            country = request.form['country']
            date_added = '2023-12-29'
            
            reads_entry = Reads(date_started=date_started, date_ended=date_ended, title=title,author=author,pages=pages,category=category,subcategory=subcategory,country=country,date_added=date_added)
            print(reads_entry)
            db.session.add(reads_entry)
            db.session.commit()
            # Redirect to the reads_history page after successful form submission
            return redirect(url_for('reads_history'))
        except Exception as e:
            # Handle database or form processing errors
            reads_entry = db.session.rollback()
            print(f"Error: {str(e)}")
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

print("start")