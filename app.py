# app.py
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime, timedelta, time
import pandas as pd


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
    my_rating = db.Column(db.Integer)
    publication_year = db.Column(db.Integer)
    date_added = db.Column(db.String(50))

class Runs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    distance = db.Column(db.Integer)
    location = db.Column(db.String(50))
    date_added = db.Column(db.String(20))
    average_time_per_km = db.Column(db.String(50))

class Trips(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_name = db.Column(db.String(100))
    date_start = db.Column(db.String(20))
    date_end = db.Column(db.String(20))
    place = db.Column(db.String(50))
    place_country = db.Column(db.String(20))
    place_continent = db.Column(db.String(20))
    lat = db.Column(db.String(50))
    lon = db.Column(db.String(50))
    date_added = db.Column(db.String(20))

class Thoughts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thought = db.Column(db.String(1000))
    category = db.Column(db.String(200))
    date_added = db.Column(db.String(20))
    

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


# STATS ---------------------------------------------------------------------------------------------------

# Route for handling form submissions
@app.route('/runs/stats', methods=['GET', 'POST'])
def runs_stats():
    runs = Runs.query.all()
    
    # get all the years (inc. duplicates)
    years_array = [int(run.date.split('-')[0]) for run in runs]
    years = group_and_rank(years_array,"FALSE", 10)
    runs_by_year = make_graph(years, "hbar", 0.2, 0, "NULL","NULL")

    ave_array = [run.average_time_per_km for run in runs]
    mean_times_per_year = group_with_agg(years_array, ave_array, "ave", "time")
    mean_times_per_year = make_graph(mean_times_per_year, "hbar", 0.2, 2, 5.5, 7)

    distance_array = [run.distance for run in runs]
    total_distance_per_year = group_with_agg(years_array, distance_array, "sum", "whole")
    total_distance_per_year = make_graph(total_distance_per_year, "hbar", 0.2, 0, "NULL", "NULL")

    return render_template('runs_stats.html', runs_by_year=runs_by_year,mean_times_per_year=mean_times_per_year,total_distance_per_year=total_distance_per_year)

@app.route('/reads/stats', methods=['GET', 'POST'])
def reads_stats():
    reads = Reads.query.where(Reads.subcategory != "manga")

    # get all the years (inc. duplicates)
    years_array = [int(read.date_ended.split('-')[0]) for read in reads]
    years = group_and_rank(years_array,"FALSE", 10)
    books_by_year = make_graph(years, "hbar", 0.2, 0, "NULL", "NULL")

    # pages read per year
    pages_array = [read.pages for read in reads]
    pages_per_year = group_with_agg(years_array, pages_array, "sum", "whole")
    pages_per_year = make_graph(pages_per_year, "hbar", 0.2, 0, "NULL", "NULL")

    # get top 5 categories by books read
    categories = [read.subcategory for read in reads]
    categories = group_and_rank(categories, "TRUE", 5)
    books_by_category = make_graph(categories, "hbar", 0.5, 0, "NULL", "NULL")

    # get top 5 writers by books read
    authors = [read.author for read in reads]
    authors = group_and_rank(authors, "TRUE", 5)
    books_by_author = make_graph(authors, "hbar", 0.5, 0, "NULL", "NULL")

    return render_template('reads_stats.html', books_by_year=books_by_year, pages_per_year=pages_per_year,books_by_category=books_by_category,books_by_author=books_by_author) 

@app.route('/trips/stats', methods=['GET', 'POST'])
def trips_stats():
    return render_template('trips_stats.html')

@app.route('/thoughts/stats', methods=['GET', 'POST'])
def thoughts_stats():
    thoughts = Thoughts.query.all()
    
    # get all the years (inc. duplicates)
    years_array = [int(thought.date_added.split('-')[0]) for thought in thoughts]
    years = group_and_rank(years_array,"FALSE", 10)
    thoughts_by_year = make_graph(years, "hbar", 0.2, 0, "NULL","NULL")



    return render_template('thoughts_stats.html', thoughts_by_year=thoughts_by_year)


# HISTORY ---------------------------------------------------------------------------------------------------

# Route for handling form submissions
@app.route('/runs/history', methods=['GET', 'POST'])
def runs_history():
    runs = Runs.query.all()

    for run in runs:
        pace = datetime.strptime(run.average_time_per_km, '%H:%M:%S').time()
        fast = datetime.strptime('00:06:00', '%H:%M:%S').time()
        med = datetime.strptime('00:07:00', '%H:%M:%S').time()
        slow = datetime.strptime('00:08:00', '%H:%M:%S').time()

        if pace < fast:
            run.pace = "fast"
        elif pace < med:
            run.pace = "med"
        elif pace < slow:
            run.pace = "slow"
    
              
    return render_template('runs_history.html',runs=runs)

@app.route('/reads/history', methods=['GET', 'POST'])
def reads_history():

    reads = Reads.query.order_by(Reads.date_ended.desc()).all()
    return render_template('reads_history.html',reads=reads)

@app.route('/trips/history', methods=['GET', 'POST'])
def trips_history():
    trips = Trips.query.all()
    return render_template('trips_history.html',trips=trips)

@app.route('/thoughts/history', methods=['GET', 'POST'])
def thoughts_history():
    thoughts = Thoughts.query.all()
    return render_template('thoughts_history.html',thoughts=thoughts)

# NEW ---------------------------------------------------------------------------------------------------

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
            my_rating = request.form['my_rating']
            publication_year = request.form['publication_year']
            date_added = datetime.today().strftime('%Y-%m-%d')
            
            reads_entry = Reads(date_started=date_started, date_ended=date_ended, title=title,author=author,pages=pages,category=category,subcategory=subcategory,country=country,date_added=date_added,my_rating=my_rating,publication_year=publication_year)
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
    # Don't redirect to History page (like others) 
    # because you want to keep the Trip details persistent to include with multiple places
    if request.method == 'POST':
        try:
            trip_name = request.form['trip_name']
            date_start = request.form['date_start']
            date_end = request.form['date_end']
            place = request.form['place']
            place_country = request.form['place_country']
            place_continent = request.form['place_continent']
            lat = request.form['lat']
            lon = request.form['lon']
            date_added = datetime.today().strftime('%Y-%m-%d')
            
            trips_entry = Trips(trip_name=trip_name,date_start=date_start, date_end=date_end, place=place, place_country=place_country, place_continent=place_continent, lat=lat, lon=lon, date_added=date_added)
            db.session.add(trips_entry)
            db.session.commit()
            
        except Exception as e:
            # Handle database or form processing errors
            reads_entry = db.session.rollback()
            print(f"Error: {str(e)}")
    return render_template('trips_new.html')

@app.route('/thoughts/new', methods=['GET', 'POST'])
def thoughts_new():
    if request.method == 'POST':
        try:
            thought = request.form['thought']
            category = request.form['category']
            date_added = datetime.today().strftime('%Y-%m-%d')
            
            thoughts_entry = Thoughts(thought=thought, category=category,date_added=date_added)
            db.session.add(thoughts_entry)
            db.session.commit()
            # Redirect to the reads_history page after successful form submission
            return redirect(url_for('thoughts_history'))
        except Exception as e:
            # Handle database or form processing errors
            reads_entry = db.session.rollback()
            print(f"Error: {str(e)}")
    return render_template('thoughts_new.html')

# FUNCTIONS -----------------------------------------------------------------------------------------------------

def make_graph(data, chart_type, label_size=0.2, round_results=0, min_range="NULL", max_range="NULL"):
    # split out the inbound data into category (x-axis) and the values (y-axis)
    categories, value = zip(*data)
    # Determine the size of the chart
    plt.subplots(figsize=(3, 2))
    # For each occurence of the inputted category, make a column in the chart
    # Whether it's a Horizontal Bar Chart
    if chart_type == "hbar":
        if min_range != "NULL":
            plt.xlim(min_range,max_range)
        bars = plt.barh(categories,value,color='lightblue')  
        for bar in bars:
            # where to position the data label
            yval = bar.get_y() + bar.get_height() / 2
            xval = bar.get_width() + 0.1    
            # for each bar, add a data label:
            plt.text(xval, yval, round(bar.get_width(),round_results), va='center', ha='left', fontsize=5, fontfamily='monospace', weight='light')
            # adjust the size of the label area to accomodate larger names (e.g. book titles, as opposed to years)
            plt.subplots_adjust(left=label_size)
            # remove left hand axis labels
            plt.tick_params(labelbottom = False, bottom = False)  
            # rank the highest sorted bar at the top (descending)
            plt.gca().invert_yaxis()
    # If it's a Vertical Bar Chart   
    elif chart_type == "bar":
        if min_range != "NULL":
            plt.ylim(min_range, max_range)
        bars = plt.bar(categories,value,color='lightblue')
        for bar in bars:
            # where to position the data label
            yval = bar.get_height() + 0.5  
            xval = bar.get_x() + bar.get_width() / 2
            # for each bar, add a data label:
            plt.text(xval, yval, round(bar.get_height(), round_results), va='center', ha='left', fontsize=5, fontfamily='monospace', weight='light')
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

def group_and_rank(categories, sort_by_count, top_number):
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




def group_with_agg(categories, values, agg_type, data_type):

    # Create a dictionary to store aggregated data
    aggregated_data = {}
    i = 0
    # Aggregate and find the mean of "average_time" per year
    for category in categories:
        # initiate 
        if category not in aggregated_data:
            if data_type == "time":
                aggregated_data[category] = [pd.Timedelta(0),0]
            elif data_type == "whole":
                aggregated_data[category] = [0,0]
        
        if data_type == "time":
            # the total time
            aggregated_data[category][0] += pd.to_timedelta(values[i])
        elif data_type == "whole":
            aggregated_data[category][0] += values[i]
        # the count (occurences)
        aggregated_data[category][1] += 1
        i += 1

    if agg_type == "ave":
        # Calculate the mean for each category
        for category, data in aggregated_data.items():
            data[0] = data[0] / data[1]

    if data_type == "time":
        result = [(category, convert_time_to_float(data[0])) for category, data in aggregated_data.items()]
    elif data_type == "whole":
        result = [(category, data[0]) for category, data in aggregated_data.items()]

    return result

def convert_time_to_float(time):
    total_seconds = time.total_seconds()
    total_minutes = total_seconds / 60
    return round(total_minutes, 2)  # rounding to 2 decimal places

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

