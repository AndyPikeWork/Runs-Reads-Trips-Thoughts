# app.py
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime


app = Flask(__name__)

# Configure SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'

# Suppress warning about tracking modifications, which is not needed in this case
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy instance (the database handler)
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

class Runs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    distance = db.Column(db.Integer)
    location = db.Column(db.String(50))
    date_added = db.Column(db.String(20))
    average_time_per_km = db.Column(db.String(50))
    

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
    reads = Reads.query.all()
    # get all the years (inc. duplicates)
    years = [int(read.date_ended.split('-')[0]) for read in reads]
    years = sort_and_rank(years,"FALSE", 10)
    books_by_year = make_graph(years, "bar")
    # get top 5 categories by books read
    categories = [read.subcategory for read in reads]
    categories = sort_and_rank(categories, "TRUE", 5)
    books_by_category = make_graph(categories, "hbar", 0.5)
    # get top 5 writers by books read
    authors = [read.author for read in reads]
    authors = sort_and_rank(authors, "TRUE", 5)
    books_by_author = make_graph(authors, "hbar", 0.5)

    return render_template('reads_stats.html', books_by_year=books_by_year, books_by_category=books_by_category,books_by_author=books_by_author) 

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
    runs = Runs.query.all()
    return render_template('runs_history.html',runs=runs)

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
    if request.method == 'POST':
        try:
            date = request.form['date']
            time = request.form['time']
            distance = request.form['distance']
            location = request.form['location']
            date_added = datetime.today().strftime('%Y-%m-%d')
            average_time_per_km = 6.50
            runs_entry = Runs(date=date, time=time, distance=distance, location=location, date_added=date_added, average_time_per_km=average_time_per_km)
            print(runs_entry)
            db.session.add(runs_entry)
            db.session.commit()
            # Redirect to the runs_history page after successful form submission
            return redirect(url_for('runs_history'))
        except Exception as e:
            # Handle database or form processing errors
            runs_entry = db.session.rollback()
            print(f"Error: {str(e)}")
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
            date_added = datetime.today().strftime('%Y-%m-%d')
            
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



def make_graph(data, chart_type, label_size=0.2):
    print(data)
    # split out the inbound data into category (x-axis) and the values (y-axis)
    categories, value = zip(*data)
    # Determine the size of the chart
    fig, ax = plt.subplots(figsize=(3, 2))
    # For each occurence of the inputted category, make a column in the chart
    # Whether it's a Horizontal Bar Chart
    if chart_type == "hbar":
        bars = plt.barh(categories,value,color='lightblue')  
        for bar in bars:
            # where to position the data label
            yval = bar.get_y() + bar.get_height() / 2
            xval = bar.get_width() + 0.1    
            # for each bar, add a data label:
            plt.text(xval, yval, round(xval - 0.5), va='center', ha='left', fontsize=5, fontfamily='monospace', weight='light')
            # adjust the size of the label area to accomodate larger names (e.g. book titles, as opposed to years)
            plt.subplots_adjust(left=label_size)
            # remove left hand axis labels
            plt.tick_params(labelbottom = False, bottom = False)  
            # rank the highest sorted bar at the top (descending)
            plt.gca().invert_yaxis()
    # If it's a Vertical Bar Chart   
    elif chart_type == "bar":
        bars = plt.bar(categories,value,color='lightblue')
        for bar in bars:
            # where to position the data label
            yval = bar.get_height() + 0.5  
            xval = bar.get_x() + bar.get_width() / 2
            # for each bar, add a data label:
            plt.text(xval, yval, round(yval - 0.5), va='center', ha='left', fontsize=5, fontfamily='monospace', weight='light')
        # remove left hand axis labels
        plt.tick_params(labelleft = False, left = False) 
    # make all text and labels the same size: 6
    plt.tick_params(axis='both', labelsize=6)
    # remove the border of the chart  
    plt.gca().set_frame_on(False)
    # remove the tick marks on the left axis
    plt.tick_params(left = False, bottom = False) 
    img = BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return plot_url

def sort_and_rank(categories, sort_by_count, top_number):
    # Initialize an empty dictionary to store counts
    category_counts = {}
    # Count the occurrences of each category
    for category in categories:
        if category in category_counts:
            category_counts[category] += 1
        else:
            category_counts[category] = 1
    # If it needs to be sorted and take the top X only:
    if sort_by_count == "TRUE":
        # sort by the value of occurences and then return just the top X (defiend by parameter)
        aggregated_array = sorted(list(category_counts.items()), key=lambda item: item[1], reverse=True)[:top_number]
    else:
        aggregated_array = list(category_counts.items())

    return aggregated_array


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