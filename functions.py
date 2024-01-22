import matplotlib.pyplot as plt
plt.matplotlib.use('Agg')

from io import BytesIO
import base64
import pandas as pd
from mpl_toolkits.basemap import Basemap

def make_graph(data, chart_type, label_size=0.2, round_results=0, min_range="NULL", max_range="NULL",img_height=2, value_sorted="TRUE"):
    # split out the inbound data into category (x-axis) and the values (y-axis)
    categories, value = zip(*[(row[0], row[1]) for row in data])
    # Determine the size of the chart
    plt.subplots(figsize=(3, img_height))
    # For each occurence of the inputted category, make a column in the chart
    # Whether it's a Horizontal Bar Chart
    if chart_type == "hbar":
        # if the range is requested to move from 0 to X (with a parm) 
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
            if value_sorted == "TRUE":
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
    elif sort_by_count == "FALSE":
        # sort by the index (e.g. year)
        aggregated_array = list(category_counts.items())
        aggregated_array = sorted(aggregated_array, key=lambda item: item[0])

    ranked_array = create_weights(aggregated_array)   
    print(*ranked_array)
    return ranked_array




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
    
    
    result = sorted(list(result),key=lambda x: x[0], reverse=True)
    ranked_array = create_weights(result)   

    return ranked_array

def make_map(lat, lon, continent):
    plt.subplots(figsize=(3.6, 3)) 
    #fig, ax = plt.subplots(subplot_kw={'projection': ccrs.EuroPP()})

            # llcrnrlat - lower left corner latitude
            # llcrnrlon - lower left corner longitude
            # urcrnrlat - upper right corner latitude
            # urcrnrlon - upper right corner longitude
    
    if continent == "world":
            m = Basemap(projection='mill', llcrnrlat=-90, llcrnrlon=-180, urcrnrlat=90, urcrnrlon=180, resolution='c')
            #ax.set_extent([-90, 40, 35, 70])  # [lon_min, lon_max, lat_min, lat_max]

    elif continent == "europe":
            m = Basemap(projection='mill', llcrnrlat=29, llcrnrlon=-33, urcrnrlat=70, urcrnrlon=40, resolution='c')
            #ax.set_extent([-10, 40, 35, 70])  # [lon_min, lon_max, lat_min, lat_max]

    elif continent == "africa":
            m = Basemap(projection='mill', llcrnrlat=-37, llcrnrlon=-20, urcrnrlat=41, urcrnrlon=60, resolution='c')
            #ax.set_extent([-10, 40, 35, 70])  # [lon_min, lon_max, lat_min, lat_max]

    elif continent == "south america":
            m = Basemap(projection='mill', llcrnrlat=-60, llcrnrlon=-90, urcrnrlat=15, urcrnrlon=-35, resolution='c')
            #ax.set_extent([-10, 40, 35, 70])  # [lon_min, lon_max, lat_min, lat_max]

    elif continent == "north america":
            m = Basemap(projection='mill', llcrnrlat=10, llcrnrlon=-170, urcrnrlat=70, urcrnrlon=-50, resolution='c')
            #ax.set_extent([-10, 40, 35, 70])  # [lon_min, lon_max, lat_min, lat_max]

    elif continent == "asia":
            m = Basemap(projection='mill', llcrnrlat=-10, llcrnrlon=41, urcrnrlat=70, urcrnrlon=150, resolution='c') 
            #ax.set_extent([-10, 40, 35, 70])  # [lon_min, lon_max, lat_min, lat_max]

    


    for i in range(len(lat)):
        # Convert latitude and longitude to x, y coordinates
        x, y = m(float(lon[i]), float(lat[i]))
        # Plot points on the map
        #ax.scatter(float(lon[i]), float(lat[i]), color='red', marker='o', label='Cities')
        m.scatter(x, y, s=3, color='red', marker='.', label='Cities')

    # Draw coastlines, countries, and states
    m.drawcoastlines(linewidth=0.1) 
    m.drawcountries(linewidth=0.1) 
    #ax.coastlines()
    

    img = BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    map_url = base64.b64encode(img.getvalue()).decode()
    return map_url
 
def convert_time_to_float(time):
    total_seconds = time.total_seconds()
    total_minutes = total_seconds / 60
    return round(total_minutes, 2)  # rounding to 2 decimal places

def add_thousand_comma(value):
    return '{:,}'.format(value)


def create_weights(data):
    max_val = max(val[1] for val in data)
    min_val = max(val[1] for val in data)
    weighted_data = []
    category = ""
    for row in data:
        proportion = int((row[1]/max_val)*100)
        #print(proportion)
        if proportion == 100:
             category = "bar_High"
        elif row[1] == min_val:
             category = "bar_Low"
        else:
             category = "bar_Med"

        weighted_row = [row[0], row[1], proportion, category]  # Include both original and proportion
        print(*weighted_row)
        weighted_data.append(weighted_row)
        
    return weighted_data