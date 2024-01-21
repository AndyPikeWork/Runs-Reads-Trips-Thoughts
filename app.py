# app.py
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, time
from jinja2.utils import markupsafe 
markupsafe.Markup()
#Markup('')
# My python files:
import functions as f

# Swich betwen 'local' and 'prod'
mode = "prod"


app = Flask(__name__)

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
    

with app.app_context():
    db.create_all()

# Route for handling form submissions
@app.route('/', methods=['GET', 'POST'])
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
def runs_stats():
    runs = Runs.query.all()
    
    # get all the years (inc. duplicates)
    years_array = [run.date.split('-')[0] for run in runs]
    years = f.group_and_rank(years_array,"FALSE", 1000)
    runs_by_year = f.make_graph(years, "hbar", 0.2, 0, "NULL","NULL", 2, "FALSE")

    ave_array = [run.average_time_per_km for run in runs]
    mean_times_per_year = f.group_with_agg(years_array, ave_array, "ave", "time")
    mean_times_per_year = f.make_graph(mean_times_per_year, "hbar", 0.2, 2, 5.5, 7, 2, "FALSE")

    distance_array = [run.distance for run in runs]
    total_distance_per_year = f.group_with_agg(years_array, distance_array, "sum", "whole")
    total_distance_per_year = f.make_graph(total_distance_per_year, "hbar", 0.2, 0, "NULL", "NULL", 2, "FALSE")

    return render_template('runs_stats.html', runs_by_year=runs_by_year,mean_times_per_year=mean_times_per_year,total_distance_per_year=total_distance_per_year)

@app.route('/reads/stats', methods=['GET', 'POST'])
def reads_stats():
    reads = Books.query.where(Books.subcategory != "manga")

    # get all the years (inc. duplicates)
    reads_years_array = [read.date_ended.split('-')[0] for read in reads]
    years_grouped = f.group_and_rank(reads_years_array,"FALSE", 1000)
    books_by_year = f.make_graph(years_grouped, "hbar", 0.2, 0, "NULL", "NULL", 3, "FALSE")

    # pages read per year
    pages_array = [read.pages for read in reads]
    pages_per_year = f.group_with_agg(reads_years_array, pages_array, "sum", "whole")
    pages_per_year = f.make_graph(pages_per_year, "hbar", 0.2, 0, "NULL", "NULL", 3, "FALSE")

    # get top 5 categories by books read
    categories = [read.subcategory for read in reads]
    categories = f.group_and_rank(categories, "TRUE", 5)
    books_by_category = f.make_graph(categories, "hbar", 0.5, 0, "NULL", "NULL",2, "TRUE")

    # get top 5 writers by books read
    authors = [read.author for read in reads]
    authors = f.group_and_rank(authors, "TRUE", 5)
    books_by_author = f.make_graph(authors, "hbar", 0.5, 0, "NULL", "NULL",2, "TRUE")

    return render_template('reads_stats.html', books_by_year=books_by_year, pages_per_year=pages_per_year,books_by_category=books_by_category,books_by_author=books_by_author) 

@app.route('/trips/stats', methods=['GET', 'POST'])
def trips_stats():

    places = Trips.query.all()
    places_non_England = Trips.query.where(Trips.place_country != "England")

 

    # places by year
    years = [place.date_start.split('-')[0] for place in places]
    years_grouped = f.group_and_rank(years,"FALSE", 10)
    places_by_year = f.make_graph(years_grouped, "hbar", 0.2, 0, "NULL", "NULL",5, "FALSE")

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

    #country_list = sorted(country_list, key=lambda item: item[1], reverse=True)[:10]
    country_cnts = f.make_graph(country_list[-10:], "hbar", 0.5, 0, "NULL", "NULL",5, "FALSE")

    return render_template('trips_stats.html', places_by_year=places_by_year,countries_by_year=countries_by_year, country_cnts=country_cnts)

@app.route('/trips/maps', methods=['GET', 'POST'])
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
def thoughts_stats():
    thoughts = Thoughts.query.all()
    
    # get all the thoughts by category 
    thoughts_by_category = [thought.category for thought in thoughts]
    thoughts_by_category = f.group_and_rank(thoughts_by_category,"FALSE", 10)
    thoughts_by_category = f.make_graph(thoughts_by_category, "hbar", 0.5, 0, "NULL","NULL", 2, "FALSE")

    return render_template('thoughts_stats.html', thoughts_by_category=thoughts_by_category)

# HISTORY ---------------------------------------------------------------------------------------------------

# Route for handling form submissions
@app.route('/runs/history', methods=['GET', 'POST'])
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
def reads_history():

    reads = Books.query.order_by(Books.date_ended.desc()).all()
    return render_template('reads_history.html',reads=reads)

@app.route('/trips/history', methods=['GET', 'POST'])
def trips_history():
    trips = Trips.query.order_by(Trips.date_start.desc()).all()

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



