# To deploy from GitHub to PythonAnywhere:

# Example:
# $ git clone https://github.com/<your-github-username>/my-first-blog.git <your-pythonanywhere-username>.pythonanywhere.com
# Actual:
# git clone https://github.com/AndyPikeWork/Runs-Reads-Trips-Thoughts.git Runs-Reads-Trips-Thoughts
# Have to delete the Runs-Reads-Trips-Thoughts directory 
# Refresh the site on the Web tab of PythonAnywhere
#
# To run a local server
#
# In the Terminal, put: python -m flask run
# then open on browser: http://127.0.0.1:5000

# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime, timedelta, time
from time import gmtime, strftime
from jinja2.utils import markupsafe 
from flask_login import UserMixin
from flask_login import LoginManager
from flask import render_template, redirect, url_for, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import re
import os
import functions as f



markupsafe.Markup()
#Markup('')
# My python functions:



# Swich betwen 'local' and 'prod'
mode = "local"


app = Flask(__name__)
login_manager = LoginManager(app)
app.secret_key = 'your_secret_key'


if mode == "prod":
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="andrewpikework",
    password="Lilac2602!",
    hostname="andrewpikework.mysql.pythonanywhere-services.com",
    databasename="andrewpikework$db",
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
elif mode == "local":
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

class Books(db.Model):
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

class Words(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_added = db.Column(db.String(20))
    note_date = db.Column(db.String(20))
    note_time = db.Column(db.String(20))
    note_type = db.Column(db.String(200))
    note_category = db.Column(db.String(200))
    note_title = db.Column(db.String(200))
    note_text = db.Column(db.String(2000))
    note_status = db.Column(db.String(200))
    edit_date = db.Column(db.String(20))
    edit_time = db.Column(db.String(20))
    note_tags = db.Column(db.String(200))
    note_original = db.Column(db.Integer)

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_added = db.Column(db.String(20))
    task = db.Column(db.String(20))
    date_edited = db.Column(db.String(20))
    status = db.Column(db.String(200))
    category = db.Column(db.String(200))
    date_due = db.Column(db.String(200))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class CONFIG_TASK_CATEGORIES(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(200))
    color = db.Column(db.String(200))

class CONFIG_WORDS_OPTIONS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(200))
    category = db.Column(db.String(200))
    color = db.Column(db.String(200))
    

with app.app_context():
    db.create_all()

# Global Parameters
today_dt_yyyymmdd = datetime.today().strftime('%Y-%m-%d')


# Route for handling form submissions
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    reads = Books.query.where(Books.subcategory != "manga")
    number_of_books = reads.count()

    pages = reads.all()
    number_of_pages = f.add_thousand_comma(sum([page.pages for page in pages]))

    runs = Runs.query.all()
    number_of_runs = len(runs)

    km_run = f.add_thousand_comma(sum([run.distance for run in runs]))

    trips_data = Trips.query.all() 

    trips = [data.trip_name for data in trips_data]
    trips_visited = f.group_and_rank(trips, "FALSE", 1000)
    trips_made = len(trips_visited)

    places = [data.place for data in trips_data]
    places_visited_unique = f.group_and_rank(places, "FALSE", 1000)
    places_visited = len(places_visited_unique)

    countries = [data.place_country for data in trips_data]
    countries_visited_unique = f.group_and_rank(countries, "FALSE", 1000)
    countries_visited = len(countries_visited_unique)


    return render_template('index.html',number_of_books=number_of_books, number_of_pages=number_of_pages,number_of_runs=number_of_runs,km_run=km_run,trips_made=trips_made, places_visited=places_visited, countries_visited=countries_visited)


# STATS --------------------------------------------------------------------------------------------------

# Route for handling form submissions
@app.route('/runs/stats', methods=['GET', 'POST'])
@login_required
def runs_stats():
    runs = Runs.query.all()
    
    # get all the years (inc. duplicates)
    years_array = [run.date.split('-')[0] for run in runs]
    years_of_runs = f.group_and_rank(years_array,"FALSE", 1000)
    # To make a Matplot lib chart (don't forget to pass runs_by_year on to the render function)
    #runs_by_year = f.make_graph(years_of_runs, "hbar", 0.2, 0, "NULL","NULL", 2, "FALSE")

    ave_array = [run.average_time_per_km for run in runs]
    ave_times_per_year = f.group_with_agg(years_array, ave_array, 100, "ave", "time", "lowest")
    # To make a Matplot lib chart (don't forget to pass mean_times_per_year on to the render function)
    #mean_times_per_year = f.make_graph(ave_times_per_year, "hbar", 0.2, 2, 5.5, 7, 2, "FALSE")

    distance_array = [run.distance for run in runs]
    total_distance_per_year_data = f.group_with_agg(years_array, distance_array, 100, "sum", "whole")
    # To make a Matplot lib chart (don't forget to pass total_distance_per_year on to the render function)
    #total_distance_per_year = f.make_graph(total_distance_per_year_data, "hbar", 0.2, 0, "NULL", "NULL", 2, "FALSE")

    #Average Distance per year
    distance_array_data = [run.distance for run in runs]
    years_array_data = [run.date.split('-')[0] for run in runs]
    average_distance_per_year_data = f.group_with_agg(years_array_data, distance_array_data, 100, "ave", "whole")


    list_5k = [run for run in runs if run.distance == 5]
    sorted_list_5k = sorted(list_5k, key=lambda x: x.time)[:10]
    latest = max(sorted_list_5k, key=lambda x: x.date)
    
    for run in sorted_list_5k:
        if run.date == latest.date:
            run.is_latest = "bar_Low"
        else: 
            run.is_latest = "bar_None"


    list_10k = [run for run in runs if run.distance == 10]
    sorted_list_10k = sorted(list_10k, key=lambda x: x.time)[:10]
    latest = max(sorted_list_10k, key=lambda x: x.date)
    
    for run in sorted_list_10k:
        if run.date == latest.date:
            run.is_latest = "bar_Low"
        else: 
            run.is_latest = "bar_None"

    list_15k = [run for run in runs if run.distance == 15]
    sorted_list_15k = sorted(list_15k, key=lambda x: x.time)[:15]
    latest = max(sorted_list_15k, key=lambda x: x.date)
    
    for run in sorted_list_15k:
        if run.date == latest.date:
            run.is_latest = "bar_Low"
        else: 
            run.is_latest = "bar_None"

    #sorted_list_10k = sorted(list_10k, key=lambda x: x.time)[:5]
    return render_template('runs_stats.html',total_distance_per_year_data=total_distance_per_year_data,years_of_runs=years_of_runs,ave_times_per_year=ave_times_per_year,sorted_list_5k=sorted_list_5k,sorted_list_10k=sorted_list_10k,sorted_list_15k=sorted_list_15k,average_distance_per_year_data=average_distance_per_year_data)

@app.route('/reads/stats', methods=['GET', 'POST'])
@login_required
def reads_stats():
    reads = Books.query.where(Books.subcategory != "manga")

    # get all the years (inc. duplicates)
    reads_years_array = [read.date_ended.split('-')[0] for read in reads]
    years_grouped = f.group_and_rank(reads_years_array,"FALSE", 10,"highest")
    #books_by_year = f.make_graph(years_grouped, "hbar", 0.2, 0, "NULL", "NULL", 3, "FALSE")

    # pages read per year
    pages_array = [read.pages for read in reads]
    pages_per_year = f.group_with_agg(reads_years_array, pages_array, 10, "sum", "whole","highest")
    #pages_per_year = f.make_graph(pages_per_year, "hbar", 0.2, 0, "NULL", "NULL", 3, "FALSE")

    # get top 5 categories by books read
    #categories = [read.subcategory for read in reads]
    #categories = f.group_and_rank(categories, "TRUE", 5)
    #books_by_category = f.make_graph(categories, "hbar", 0.5, 0, "NULL", "NULL",2, "TRUE")

    # get top 5 writers by books read
    authors = [read.author for read in reads]
    authors = f.group_and_rank(authors, "TRUE", 10, "highest")
    #books_by_author = f.make_graph(authors, "hbar", 0.5, 0, "NULL", "NULL",2, "TRUE")

    # Fastest Reads

    reads_with_time_difference = []  # List to store reads along with their time differences
    pages_per_day = []  # List to store reads along with their time differences

    for read in reads:
        time_difference = f.difference_in_dates(read.date_started, read.date_ended)
        if time_difference is not None:
            pages_per_day = int(round(read.pages / time_difference, 0))
            reads_with_time_difference.append((read, time_difference, pages_per_day))

    # Sort reads based on the calculated time differences
    #pages_per_day.sort(key=lambda x: x[1] if x[1] is not None else float('inf'))  # Sort based on time difference (shortest first)
    reads_with_time_difference.sort(key=lambda x: x[2], reverse=True)  # Sort based on pages_per_day
    #pages_per_day.sort(key=lambda x: x[1] if x[1] is not None else float('inf'))


    
    # Extract the sorted reads
    sorted_reads = [(read, time_difference, pages_per_day) for read, time_difference, pages_per_day in reads_with_time_difference]
    # Take the top 10 fastest reads
    top_10_fastest_reads = sorted_reads[:10]

    # Pass the top 10 fastest reads to the group_and_rank function
    fastest_reads = [read for read in top_10_fastest_reads]

    return render_template('reads_stats.html', years_grouped=years_grouped, pages_per_year=pages_per_year,authors=authors,fastest_reads=fastest_reads) 

@app.route('/trips/stats', methods=['GET', 'POST'])
@login_required
def trips_stats():

    places = Trips.query.all()
    places_non_England = Trips.query.where(Trips.place_country != "England")

 

    # places by year
    years = [place.date_start.split('-')[0] for place in places]
    years_grouped = f.group_and_rank(years,"FALSE", 10)
    #places_by_year = f.make_graph(years_grouped, "hbar", 0.2, 0, "NULL", "NULL",5, "FALSE")

    # Unique countries by year

    years_array = [int(place_non_England.date_start.split('-')[0]) for place_non_England in places_non_England]
    countries_array = [place_non_England.place_country for place_non_England in places_non_England]

    # Dictionary to store occurrences of unique countries for each year
    countries_in_year = {}

    # Loop through the data
    for year, country in zip(years_array, countries_array):
        if year not in countries_in_year:
            # If the year is not in the dictionary, add it with an empty set
            countries_in_year[year] = set()

        # Add the country to the set if it hasn't been added for this year
        countries_in_year[year].add(country)

    countries_by_year = list(countries_in_year.items())
    countries_by_year = sorted(countries_by_year, key=lambda x: x[0], reverse=True)

    # Dictionary to store the count of unique country-trip combinations
    country_count = {}
    # Set to keep track of visited combinations (country, trip)
    visited_combinations = set()

    # Loop through the list and count unique occurrences
    for visit in places_non_England:
        key = (visit.place_country, visit.trip_name)
        
        if key not in visited_combinations:
            # Update the count for the country
            country_count[visit.place_country] = country_count.get(visit.place_country, 0) + 1
            
            # Mark the combination as visited
            visited_combinations.add(key)

    country_list = list(country_count.items())
    country_list = sorted(country_list, key=lambda x: x[1])

    country_list = sorted(country_list, key=lambda item: item[1], reverse=True)[:10]
    countries = f.create_weights(country_list, "highest") 
    #country_cnts = f.make_graph(country_list[-10:], "hbar", 0.5, 0, "NULL", "NULL",5, "FALSE")

    return render_template('trips_stats.html', years_grouped=years_grouped,countries_by_year=countries_by_year, countries=countries)

@app.route('/trips/maps', methods=['GET', 'POST'])
@login_required
def trips_maps():
    
    places = Trips.query.all()

    # map of places
    lat = [place.lat for place in places]
    lon = [place.lon for place in places]  
    
    map_world = f.make_map(lat,lon, "world")
    map_europe = f.make_map(lat,lon, "europe")
    map_africa = f.make_map(lat,lon, "africa")
    map_north_america = f.make_map(lat,lon, "north america")
    map_south_america = f.make_map(lat,lon, "south america")
    map_asia = f.make_map(lat,lon, "asia") 

    return render_template('trips_maps.html', map_world=map_world, map_europe=map_europe, map_africa=map_africa, map_asia=map_asia, map_north_america=map_north_america, map_south_america=map_south_america)

@app.route('/thoughts/stats', methods=['GET', 'POST'])
@login_required
def thoughts_stats():
    thoughts = Thoughts.query.all()
    
    # get all the thoughts by category 
    thoughts_by_category = [category.strip() for thought in thoughts for category in thought.category.split(',')]

    thoughts_by_category = f.group_and_rank(thoughts_by_category,"TRUE", 10)
    #thoughts_by_category = f.make_graph(thoughts_by_category, "hbar", 0.5, 0, "NULL","NULL", 2, "FALSE")

    return render_template('thoughts_stats.html', thoughts_by_category=thoughts_by_category) 

@app.route('/words/stats', methods=['GET', 'POST'])
@login_required
def words_stats():
    words = Words.query.filter(Words.note_status=='latest', Words.note_category != '')
    thoughts = Words.query.filter(Words.note_type=='Thought')

    # get all the thoughts by tag
    thoughts_by_tags = [tag.strip() for note in thoughts for tag in note.note_tags.split(',')]
    thoughts_by_tags = f.group_and_rank(thoughts_by_tags,"TRUE", 10)
    
    # get all the notes by category 
    notes_by_category = [category.strip() for note in words for category in note.note_category.split(',')]
    notes_by_category = f.group_and_rank(notes_by_category,"TRUE", 10)
    #thoughts_by_category = f.make_graph(thoughts_by_category, "hbar", 0.5, 0, "NULL","NULL", 2, "FALSE")

    return render_template('words_stats.html', notes_by_category=notes_by_category,thoughts_by_tags=thoughts_by_tags)

# HISTORY ---------------------------------------------------------------------------------------------------

# Route for handling form submissions
@app.route('/runs/history', methods=['GET', 'POST'])
@login_required
def runs_history():
    runs = Runs.query.order_by(Runs.date.desc()).all()

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
@login_required
def reads_history():

    reads = Books.query.order_by(Books.date_ended.desc()).all()
    return render_template('reads_history.html',reads=reads)

@app.route('/trips/history', methods=['GET', 'POST'])
@login_required
def trips_history():
    trips = Trips.query.order_by(Trips.date_start.desc()).all()

    return render_template('trips_history.html',trips=trips)

@app.route('/thoughts/history', methods=['GET', 'POST'])
@login_required
def thoughts_history():
    thoughts = Thoughts.query.all()
    return render_template('thoughts_history.html',thoughts=thoughts)

@app.route('/words/history', methods=['GET', 'POST'])
@login_required
def words_history():
    words = Words.query.filter_by(note_status='latest').order_by(Words.note_date.desc())

    words_config = db.session.query(CONFIG_WORDS_OPTIONS.type,
                                func.group_concat(CONFIG_WORDS_OPTIONS.category, ',').label('categories'),
                                CONFIG_WORDS_OPTIONS.color).group_by(CONFIG_WORDS_OPTIONS.type, CONFIG_WORDS_OPTIONS.color).order_by(CONFIG_WORDS_OPTIONS.id).all()

    words_config_options = [{'type': config.type, 'categories': config.categories.split(','), 'color': config.color} for config in words_config]

    # adding the color to the words

    colored_words = []
    for word in words:
        word_dict = word.__dict__

        for option in words_config:
            if option.type == word.note_type:
                word_dict['color'] = option.color
        colored_words.append(word_dict)

    return render_template('words_history.html',words=colored_words,words_options=words_config_options)

# NEW ---------------------------------------------------------------------------------------------------

# Route for handling form submissions
@app.route('/runs/new', methods=['GET', 'POST'])
@login_required
def runs_new():
    if request.method == 'POST':
        try:
            date = request.form['date']
            time = request.form['time']
            distance = request.form['distance']
            location = request.form['location']
            date_added = datetime.today().strftime('%Y-%m-%d')
            average_time_per_km = f.average_time_per_kilometer(time, distance)
            runs_entry = Runs(date=date, time=time, distance=distance, location=location, date_added=date_added, average_time_per_km=average_time_per_km)
            db.session.add(runs_entry)
            db.session.commit()
            # Redirect to the runs_history page after successful form submission
            return redirect(url_for('runs_history'))
        except Exception as e:
            # Handle database or form processing errors
            runs_entry = db.session.rollback()
            print(f"Error: {str(e)}")
    return render_template('runs_new.html',today_dt_yyyymmdd=today_dt_yyyymmdd)

@app.route('/reads/new', methods=['GET', 'POST'])
@login_required
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
            
            reads_entry = Books(date_started=date_started, date_ended=date_ended, title=title,author=author,pages=pages,category=category,subcategory=subcategory,country=country,date_added=date_added,my_rating=my_rating,publication_year=publication_year)
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
@login_required
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

""" @app.route('/thoughts/new', methods=['GET', 'POST'])
@login_required
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
 """
@app.route('/words/new', methods=['GET', 'POST'])
@login_required
def words_new():
    current_time = datetime.now().strftime("%H:%M:%S")
    today_dt_yyyymmdd = datetime.today().strftime('%Y-%m-%d')
    key = datetime.now().strftime("%Y%m%d%H%M%S")

    if request.method == 'POST':
        try:
            date_added = datetime.today().strftime('%Y-%m-%d')
            note_date = request.form['note_date']
            note_time = current_time
            note_type = request.form['note_type']
            note_category = request.form['note_category']
            note_title = request.form['note_title']
            note_text = request.form['note_text']
            note_status = "latest"
            edit_date = ""
            edit_time = ""
            note_tags = request.form['note_tags']
            note_original = key
            
            words_entry = Words(note_date=note_date, 
                                note_time=note_time,
                                note_type=note_type, 
                                note_category=note_category,
                                note_title=note_title,
                                note_text=note_text,
                                note_tags=note_tags,
                                note_status=note_status,
                                edit_date=edit_date,
                                edit_time=edit_time,
                                date_added=date_added,
                                note_original=note_original)
            db.session.add(words_entry)
            db.session.commit()

            # Add any images
            IMAGE_FOLDER = "static/images/"  
            
            uploaded_images = [request.files.getlist('note_images')[i] for i in range(len(request.files.getlist('note_images')))]
            for image in uploaded_images:
                if image and image.filename:  # Check if image exists and has a filename
                    try:
                        filename = key+"_"+secure_filename(image.filename)
                        print(filename)
                        # Save the image to the folder
                        image.save(os.path.join(IMAGE_FOLDER, filename))
                    except Exception as e:
                        print(f"Error saving image: {e}")
                else:
                    print(f"Skipping empty image file.")
         

            # Redirect to the reads_history page after successful form submission
            return redirect(url_for('words_view', note_original=key))

            # return redirect(url_for('words_history'))
        except Exception as e:
            # Handle database or form processing errors
            words_entry = db.session.rollback()
            print(f"Error: {str(e)}")
    
    words_config = db.session.query(CONFIG_WORDS_OPTIONS.type,
                                func.group_concat(CONFIG_WORDS_OPTIONS.category, ',').label('categories'),
                                CONFIG_WORDS_OPTIONS.color).group_by(CONFIG_WORDS_OPTIONS.type, CONFIG_WORDS_OPTIONS.color).order_by(CONFIG_WORDS_OPTIONS.id).all()

    words_config_options = [{'type': config.type, 'categories': config.categories.split(','), 'color': config.color} for config in words_config]

    
    return render_template('words_new.html',today_dt_yyyymmdd=today_dt_yyyymmdd, words_options=words_config_options )

# VIEW NOTE  ---------------------------------------------------------------------------------------------------

@app.route('/words/note/<int:note_original>')
@login_required
def words_view(note_original):
    note = Words.query.filter_by(note_original=note_original, note_status='latest').order_by(Words.id.desc()).first()

    # Get the notes with the same Type and Category
    # notes = Words.query.filter_by(note_status='latest', note_type=note.note_type, note_category=note.note_category).order_by(Words.note_date.desc())
    notes = Words.query.filter_by(note_status='latest').order_by(Words.note_date.desc())

    # Get Anchor links
    
    anchor_links = []

    for match in re.finditer(r'\*\*((?:[\w\s.,!?“”‘’\'\"\-\(\)]+?)\d*?(?:\s[\w\s.,!?“”‘’\'\"\-\(\)]+)*\??)\*\*', note.note_text):
        anchor_links.append(match.group(1))

    # Convert Regex to HTML notation

    # convert ** into <bold> tags
    note.note_text = re.sub(r'\*\*((?:[\w\s.,!?“”‘’\'\"\-\(\)]+?)\d*?(?:\s[\w\s.,!?“”‘’\'\"\-\(\)]+)*\??)\*\*', r'<b id="\1">\1</b>', note.note_text)
    # convert links to <a> elements
    note.note_text = re.sub(r"(https?:\/\/[^\s]+)",r"<a target='_blank' href='\1'>\1</a>", note.note_text).replace('</td>','')
    #note.note_text = note.note_text.replace('</td></a>', '</a></td>')
    # convert ___ into a new line
    note.note_text = re.sub(r'\_\_\_', r'<hr>', note.note_text)
    # convert __text__ into <u> tags (Underline)
    note.note_text = re.sub(r'\-\-(.*?)\-\-', r'<u>\1</u>', note.note_text)
    # convert _text_ into <i> tags (Italics)
    note.note_text = re.sub(r'\-(.*?)\-$', r'<i>\1</i>', note.note_text)
    # convert ## to <li> and </li>
    note.note_text = re.sub(r'^##(.*)', r'<li class="words_li">\1</li>', note.note_text, flags=re.MULTILINE)

    # convert <table> tag to <table class="words_content_table>"
    note.note_text = note.note_text.replace('<table>', '<table class="words_content_table">')
    # get rid of new lines after table elements (otherwise will create lots of white space before the Table)
    note.note_text = note.note_text.replace('<table>\r\n', '<table>')
    note.note_text = note.note_text.replace('<th>\r\n', '<th>')
    note.note_text = note.note_text.replace('<tr>\r\n', '<tr>')
    note.note_text = note.note_text.replace('<td>\r\n', '<td>')
    note.note_text = note.note_text.replace('</table>\r\n', '</table>')
    note.note_text = note.note_text.replace('</th>\r\n', '</th>')
    note.note_text = note.note_text.replace('</tr>\r\n', '</tr>')
    note.note_text = note.note_text.replace('</td>\r\n', '</td>')
    note.note_text = note.note_text.replace('</li>\n', '</li>')
    
    note.note_text = note.note_text.replace('Â£', '£')
    note.note_text = re.sub(r"image>>(.+)", lambda match: f"<img src={url_for('static', filename=f'images/{note.note_original}_{match.group(1).strip()}')} class='words_image center'>", note.note_text)

    # convert new lines to HTML line breaks
    note.note_text = note.note_text.replace('\n', '<br>')

    

    words_config = db.session.query(CONFIG_WORDS_OPTIONS.type,
                                func.group_concat(CONFIG_WORDS_OPTIONS.category, ',').label('categories'),
                                CONFIG_WORDS_OPTIONS.color).group_by(CONFIG_WORDS_OPTIONS.type, CONFIG_WORDS_OPTIONS.color).order_by(CONFIG_WORDS_OPTIONS.id).all()

    words_config_options = [{'type': config.type, 'categories': config.categories.split(','), 'color': config.color} for config in words_config]

    #note = Words.query.get_or_404(note_key)
    return render_template('words_view.html', note=note, notes=notes, words_options=words_config_options, anchors=anchor_links)

@app.route('/words/note/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def words_edit(note_id):
    note = Words.query.get_or_404(note_id)

    today_dt_yyyymmdd = datetime.today().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime("%H:%M:%S")

    if request.method == 'POST':
        try:
            date_added = today_dt_yyyymmdd 
            note_date = request.form['note_date']
            note_time = request.form['note_time']
            note_type = request.form['note_type']
            note_category = request.form['note_category']
            note_title = request.form['note_title']
            note_text = request.form['note_text']
            note_status = "latest"
            edit_date = today_dt_yyyymmdd 
            edit_time = current_time
            note_tags = request.form['note_tags']
            note_original = int(request.form['note_key'])

            words_edit = Words(date_added=date_added,
                               note_date=note_date,
                               note_time=note_time,
                               note_type=note_type,
                               note_category=note_category,
                               note_title=note_title,
                               note_text=note_text,
                               note_status=note_status,
                               edit_date=edit_date,
                               edit_time=edit_time,
                               note_tags=note_tags,
                               note_original=note_original)
            
            db.session.add(words_edit)
            db.session.commit()

            # change the current note to 'existing' (so it dissapears from original view list)
            note.note_status="edited"
            db.session.commit()

            # Add any images
            IMAGE_FOLDER = "static/images/"  
            
            uploaded_images = [request.files.getlist('note_images')[i] for i in range(len(request.files.getlist('note_images')))]
            for image in uploaded_images:
                try:
                    filename = str(note_original)+"_"+secure_filename(image.filename)
                    print(filename)
                    # Save the image to the folder
                    image.save(os.path.join(IMAGE_FOLDER, filename))
                except Exception as e:
                    print(f"Error saving image: {e}")

            # Redirect to the reads_history page after successful form submission
            return redirect(url_for('words_view', note_original=note_original))
            #return redirect(url_for('words_history'))
        except Exception as e:
            # Handle database or form processing errors
            words_edit = db.session.rollback()
            print(f"Error: {str(e)}")

    words_config = db.session.query(CONFIG_WORDS_OPTIONS.type,
                                func.group_concat(CONFIG_WORDS_OPTIONS.category, ',').label('categories'),
                                CONFIG_WORDS_OPTIONS.color).group_by(CONFIG_WORDS_OPTIONS.type, CONFIG_WORDS_OPTIONS.color).order_by(CONFIG_WORDS_OPTIONS.id).all()

    words_config_options = [{'type': config.type, 'categories': config.categories.split(','), 'color': config.color} for config in words_config]

    return render_template('words_edit.html', note=note, words_options=words_config_options)



@app.route('/words/note/<int:note_id>/delete', methods=['GET', 'POST'])
@login_required
def words_delete(note_id):
    note = Words.query.get_or_404(note_id)

    today_dt_yyyymmdd = datetime.today().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime("%H:%M:%S")


    if request.method == 'POST':
        try:
            # change the current note to 'existing' (so it dissapears from original view list)
            note.edit_date = today_dt_yyyymmdd
            note.edit_time = current_time
            note.note_status="deleted"
            db.session.commit()

            # Redirect to the reads_history page after successful form submission
            return redirect(url_for('words_history'))
        except Exception as e:
            # Handle database or form processing errors
            print(f"Error: {str(e)}")
    return render_template('words_delete.html', note=note)


# TASKS ------------------------------------------------------------------------------------------------------------

@app.route('/words/tasks', methods=['GET', 'POST'])
@login_required
def words_tasks():
    tasks = return_tasks()
    
    if request.method == 'POST':
        today_dt_yyyymmdd = datetime.today().strftime('%Y-%m-%d')
        # When it's an AJAX request, use JSON
        data = request.get_json() 
        print(data['id'])

        if(data['status']) == "new":
            new_task = Tasks(date_added=today_dt_yyyymmdd,task=data['task'],date_edited="",status="new", category=data['category'], date_due=data['due'])
            db.session.add(new_task)
            db.session.commit()

        if(data['status']) == "done":
            task = Tasks.query.get(data['id'])  # Fetch task using ID
            if not task:
                return jsonify({'error': 'Task not found'}), 404
            # Update task attributes (modify as needed)
            task.date_edited = today_dt_yyyymmdd  
            task.status = "done"
            db.session.commit()

        if(data['status']) == "delete":
            task = Tasks.query.get(data['id'])  # Fetch task using ID
            if not task:
                return jsonify({'error': 'Task not found'}), 404
            # Update task attributes (modify as needed)
            task.date_edited = today_dt_yyyymmdd  
            task.status = "deleted"
            db.session.commit()

        tasks = return_tasks()
        return jsonify(tasks)
    task_categories = CONFIG_TASK_CATEGORIES.query.all() 
    tasks_options = [{'category': category.category, 'color': category.color} for category in task_categories]

    return render_template('words_tasks.html', tasks=tasks, task_categories=tasks_options)

def return_tasks():
    existing_tasks = [
            {
                "id": task.id,  # Include task ID if needed
                "task": task.task,
                "date_added": task.date_added,
                "status": task.status,
                "category": task.category,
                "date_due": task.date_due
                # Add other task properties as needed
            }
            for task in Tasks.query.filter(Tasks.status != "deleted").order_by(Tasks.date_due.asc()).all()
        ]
    return existing_tasks




# AUTHENTICATION  ---------------------------------------------------------------------------------------------------


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('login.html')

@app.before_request
def before_request():
    if not current_user.is_authenticated and request.endpoint not in ['login', 'static']:
        return redirect(url_for('login'))
    

# SETTINGS  ---------------------------------------------------------------------------------------------------


@app.route('/settings',methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        data = request.get_json() 

        if(data['update']) == "task_color_change":
            config_cat = CONFIG_TASK_CATEGORIES.query.get(data['id'])  # Fetch task using ID
            if not config_cat:
                return jsonify({'error': 'Task not found'}), 404
            # Update task attributes (modify as needed)
            config_cat.color = data['color']  
            db.session.commit()
            return jsonify(data['color'])
        
        if(data['update']) == "word_color_change":
            config_cat = CONFIG_WORDS_OPTIONS.query.get(data['id'])  # Fetch task using ID
            if not config_cat:
                return jsonify({'error': 'Task not found'}), 404
            # Update task attributes (modify as needed)
            config_cat.color = data['color']  
            db.session.commit()
            return jsonify(data['color'])
        
        if(data['update']) == "new_task_category":
            new_task_category = CONFIG_TASK_CATEGORIES(category=data['category'],color=data['color'])
            db.session.add(new_task_category)
            db.session.commit()
            return jsonify(data)
        
        if(data['update']) == "new_word_category":
            new_word_category = CONFIG_WORDS_OPTIONS(type=data['type'], category=data['category'],color=data['color'])
            db.session.add(new_word_category)
            db.session.commit()
            return jsonify(data)

    config_tasks = CONFIG_TASK_CATEGORIES.query.all()
    config_words = CONFIG_WORDS_OPTIONS.query.all()
    return render_template('settings.html', config_tasks=config_tasks, config_words=config_words)


# SETUP  ---------------------------------------------------------------------------------------------------



if __name__ == '__main__':
    # Create the database tables before running the app
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully.")
        except Exception as e:
            print(f"Error creating database tables: {str(e)}") 


if mode == "local":
    # Run the Flask app in debug mode
    app.run(debug=True)



