
import plotly.graph_objects as go
from flask import Flask, render_template
import requests
import pandas as pd
import plotly.express as px 
import numpy as np
import requests

app = Flask(__name__)

API_BASE_URL = "http://127.0.0.1:5000"

@app.route('/')  
def home():
    return render_template('dashboard.html')  

def crimecount_chart(data):
    cities = list(set(row['City'] for row in data))  
    categories = list(set(row['Crime_Category'] for row in data))  
    city_category_counts = {city: {category: 0 for category in categories} for city in cities}
    for row in data:
        city = row['City']
        category = row['Crime_Category']
        count = row['Crime_Count']
        city_category_counts[city][category] = count
    traces = []
    for category in categories:
        counts = [city_category_counts[city][category] for city in cities]
        traces.append(go.Bar(
            x=cities,
            y=counts,
            name=category
        ))
    fig = go.Figure(data=traces)
    fig.update_layout(
        title="Crime Counts by Category per City",
        xaxis_title="Cities",
        yaxis_title="Crime Count",
        barmode='stack', 
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='plotly',
        title_font=dict(size=20, color='black'),
        xaxis=dict(title_font=dict(color='black')),
        yaxis=dict(title_font=dict(color='black'))
    )
    return fig.to_html(full_html=False)


@app.route("/visualize_crime_category_per_city")
def visualize_crime_category_per_city():
    response = requests.get(f"{API_BASE_URL}/crime_category_per_city?key=123")
    if response.status_code == 200:
        api_data = response.json()
        if api_data.get('code') == 1:
            data = api_data.get('data')
            chart_html = crimecount_chart(data)
            return render_template("main.html", chart_html=chart_html)
        else:
            return f"API Error: {api_data.get('msg')}"
    else:
        return f"Failed to fetch data: {response.status_code}"
    

def crimeyears_chart(data):
    years = [row['DateYear'] for row in data]
    crime_counts = [row['Crime_Count'] for row in data]
    fig = go.Figure(data=[go.Bar(x=years, y=crime_counts, marker_color='skyblue')])
    fig.update_layout(
        title="Crime Counts Over the Years",
        xaxis_title="Year",
        yaxis_title="Crime Count",
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='plotly',
        title_font=dict(size=20, color='black'),
        xaxis=dict(title_font=dict(color='black')),
        yaxis=dict(title_font=dict(color='black'))
    )
    return fig.to_html(full_html=False)

@app.route("/visualize_crime_over_years")
def test_crime_over_years():    
    response = requests.get(f"{API_BASE_URL}/crime_over_years?key=123")
    if response.status_code == 200:
        api_data = response.json()
        if api_data.get('code') == 1:
            data = api_data.get('data')
            chart_html = crimeyears_chart(data)
            return render_template("main.html", chart_html=chart_html)
        else:
            return f"API Error: {api_data.get('msg')}"
    else:
        return f"Failed to fetch data: {response.status_code}"

def crime_per_month_chart(data):
    months = [row['DateMonth'] for row in data]
    crime_counts = [row['Crime_Count'] for row in data]
    fig = go.Figure(data=[go.Bar(x=months, y=crime_counts, marker_color='skyblue')])
    fig.update_layout(
        title="Crime Count Per Month",
        xaxis_title="Month",
        yaxis_title="Crime Count",
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='plotly',
        title_font=dict(size=20, color='black'),
        xaxis=dict(title_font=dict(color='black')),
        yaxis=dict(title_font=dict(color='black')),
        xaxis_tickmode='array',
        xaxis_tickvals=list(range(1, 13)), 
        xaxis_ticktext=[str(i) for i in range(1, 13)]
    )
    return fig.to_html(full_html=False)

@app.route("/visualize_crime_per_month")
def test_crime_per_month():    
    response = requests.get(f"{API_BASE_URL}/crime_per_month?key=123&city=Seattle")
    if response.status_code == 200:
        api_data = response.json()
        if api_data.get('code') == 1:
            data = api_data.get('data')
            chart_html = crime_per_month_chart(data)
            return render_template("main.html", chart_html=chart_html)
        else:
            return f"API Error: {api_data.get('msg')}"
    else:
        return f"Failed to fetch data: {response.status_code}"


def crime_by_date_range_chart(data):
    dates = [row['CrimeDate'] for row in data]
    crime_counts = [row['Crime_Count'] for row in data]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, 
        y=crime_counts, 
        mode='lines+markers',
        line=dict(color='skyblue', width=2),  
        marker=dict(size=5, color='skyblue')  
    ))
    fig.update_layout(
        title="Crime Count by Date Range",
        xaxis_title="Date",
        yaxis_title="Crime Count",
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='plotly',
        title_font=dict(size=20, color='black'),
        xaxis=dict(
            title_font=dict(color='black'),
            showgrid=False,
            tickvals=[], 
            showticklabels=False 
        ),
        yaxis=dict(title_font=dict(color='black')),
    )
    return fig.to_html(full_html=False)

@app.route("/visualize_crime_by_date_range")
def test_crime_by_date_range():
    response = requests.get(f"{API_BASE_URL}/crime_by_date_range?key=123&start_date=2020-01-01&end_date=2024-01-31")
    if response.status_code == 200:
        api_data = response.json()
        if api_data.get('code') == 1:
            data = api_data.get('data')
            chart_html = crime_by_date_range_chart(data)
            return render_template("main.html", chart_html=chart_html)
        else:
            return f"API Error: {api_data.get('msg')}"
    else:
        return f"Failed to fetch data: {response.status_code}"



def crime_comparison_chart(data):
    df = pd.DataFrame(data)
    pivot_df = df.pivot_table(index=['City', 'DateYear'], columns='Crime_Category', values='Crime_Count', aggfunc='sum', fill_value=0)
    pivot_df.reset_index(inplace=True)
    fig = go.Figure()
    color_palette = px.colors.qualitative.Set3 
    for i, category in enumerate(pivot_df.columns[2:]):  
        fig.add_trace(go.Bar(
            x=[f"{city} - {year}" for city, year in zip(pivot_df['City'], pivot_df['DateYear'])], 
            y=pivot_df[category], 
            name=category,
            marker=dict(color=color_palette[i % len(color_palette)]) 
        ))
    fig.update_layout(
        barmode='stack',  
        title="Crime Comparison Per Year",
        xaxis_title="City and Year",
        yaxis_title="Crime Count",
        xaxis_tickangle=-45, 
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='plotly',
        title_font=dict(size=20, color='black'),
        xaxis=dict(title_font=dict(color='black')),
        yaxis=dict(title_font=dict(color='black')),
    )
    return fig.to_html(full_html=False)


@app.route("/visualize_crime_comparison")
def test_crime_comparison():
    response = requests.get(f"{API_BASE_URL}/crime_comparison_per_year?key=123")
    if response.status_code == 200:
        api_data = response.json()
        if api_data.get('code') == 1:
            data = api_data.get('data')
            chart_html = crime_comparison_chart(data)
            return render_template("main.html", chart_html=chart_html)
        else:
            return f"API Error: {api_data.get('msg')}"
    else:
        return f"Failed to fetch data: {response.status_code}"
    

def crime_statistics_by_category_chart(data):
    categories = [row['Crime_Category'] for row in data]
    crime_counts = [row['Crime_Count'] for row in data]
    color_palette = px.colors.qualitative.Set3 
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories,  
        y=crime_counts, 
        marker=dict(color=color_palette[:len(categories)]), 
        name="Crime Count"
    ))
    fig.update_layout(
        title="Crime Statistics by Category",
        xaxis_title="Crime Category",
        yaxis_title="Crime Count",
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='plotly',
        title_font=dict(size=20, color='black'),
        xaxis=dict(title_font=dict(color='black'), tickangle=45),  
        yaxis=dict(title_font=dict(color='black')),
    )
    return fig.to_html(full_html=False)

@app.route("/visualize_crime_statistics_by_category")
def test_crime_statistics_by_category():
    response = requests.get(f"{API_BASE_URL}/crime_statistics_by_category?key=123")
    if response.status_code == 200:
        api_data = response.json()
        if api_data.get('code') == 1:
            data = api_data.get('data')
            chart_html = crime_statistics_by_category_chart(data)
            return render_template("main.html", chart_html=chart_html)
        else:
            return f"API Error: {api_data.get('msg')}"
    else:
        return f"Failed to fetch data: {response.status_code}"


def crime_count_by_day_of_week_chart(data):
    data = pd.DataFrame(data)
    day_mapping = {
        1: "Sunday", 2: "Monday", 3: "Tuesday", 4: "Wednesday",
        5: "Thursday", 6: "Friday", 7: "Saturday"
    }
    data['Day_Name'] = data['Day_Of_Week'].map(day_mapping)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data['Day_Name'],  
        y=data['Crime_Count'],  
        marker_color='skyblue'  
    ))
    fig.update_layout(
        title="Crime Counts by Day of the Week",
        xaxis_title="Day of the Week",
        yaxis_title="Number of Crimes",
        title_font=dict(size=16),
        xaxis=dict(title_font=dict(size=12)),
        yaxis=dict(title_font=dict(size=12)),
        template='plotly',
    )
    return fig.to_html(full_html=False)

@app.route("/visualize_crime_count_by_day_of_week")
def test_crime_count_by_day_of_week():
    response = requests.get(f"{API_BASE_URL}/crime_by_day_of_week?key=123")
    if response.status_code == 200:
        api_data = response.json()
        if api_data.get('code') == 1:
            data = api_data.get('data')
            chart_html = crime_count_by_day_of_week_chart(data)
            return render_template("main.html", chart_html=chart_html)
        else:
            return f"API Error: {api_data.get('msg')}"
    else:
        return f"Failed to fetch data: {response.status_code}"


def crime_details_by_city_category_chart(data):
    df = pd.DataFrame(data)
    fig = px.bar(
        df,
        x='Crime_Count',
        y='Sub_Category',
        orientation='h',  
        color='Sub_Category',
        title="Crime Details by Sub-Category",
        labels={'Crime_Count': 'Number of Crimes', 'Sub_Category': 'Crime Sub-Category'},
        color_discrete_sequence=px.colors.qualitative.Set2 
    )
    fig.update_layout(
        title_font=dict(size=16),
        xaxis=dict(title='Number of Crimes', title_font=dict(size=12)),
        yaxis=dict(title='Crime Sub-Category', title_font=dict(size=12)),
        legend_title_text='Sub-Category'
    )
    return fig.to_html(full_html=False)


@app.route("/visualize_crime_details_by_city_category")
def test_crime_details_by_city_category():
    response = requests.get(f"{API_BASE_URL}/crime_details_by_city_category?key=123&city=Seattle&category=Theft")
    if response.status_code == 200:
        api_data = response.json()
        if api_data.get('code') == 1:
            data = api_data.get('data')
            chart_html = crime_details_by_city_category_chart(data)
            return render_template("main.html", chart_html=chart_html)
        else:
            return f"API Error: {api_data.get('msg')}"
    else:
        return f"Failed to fetch data: {response.status_code}"


def crime_location_density_by_city_chart(data):
    df = pd.DataFrame(data)
    df = df[(df['Latitude'] != 0.0) | (df['Longitude'] != 0.0)]
    Q1_lat, Q3_lat = np.percentile(df['Latitude'], 25), np.percentile(df['Latitude'], 75)
    Q1_lon, Q3_lon = np.percentile(df['Longitude'], 25), np.percentile(df['Longitude'], 75)
    IQR_lat, IQR_lon = Q3_lat - Q1_lat, Q3_lon - Q1_lon
    df = df[
        (df['Latitude'] >= Q1_lat - 1.5 * IQR_lat) & (df['Latitude'] <= Q3_lat + 1.5 * IQR_lat) &
        (df['Longitude'] >= Q1_lon - 1.5 * IQR_lon) & (df['Longitude'] <= Q3_lon + 1.5 * IQR_lon)
    ]
    lat_bin_size = 0.01
    lon_bin_size = 0.01
    df['lat_bin'] = np.floor(df['Latitude'] / lat_bin_size) * lat_bin_size
    df['lon_bin'] = np.floor(df['Longitude'] / lon_bin_size) * lon_bin_size
    bin_counts = df.groupby(['lat_bin', 'lon_bin']).size().reset_index(name='count')
    fig = px.density_mapbox(
        bin_counts,
        lat='lat_bin',
        lon='lon_bin',
        z='count',
        radius=10,
        center=dict(lat=df['Latitude'].mean(), lon=df['Longitude'].mean()),
        zoom=10,
        mapbox_style="carto-positron",
        title="Crime Location Density"
    )
    return fig.to_html(full_html=False)


@app.route("/visualize_crime_location_density_by_city")
def test_crime_location_density_by_city():
    response = requests.get(f"{API_BASE_URL}/crime_location_density_by_city?key=123&city=Chicago")
    if response.status_code == 200:
        api_data = response.json()
        if api_data.get('code') == 1:
            data = api_data.get('data')
            chart_html = crime_location_density_by_city_chart(data)
            return render_template("main.html", chart_html=chart_html)
        else:
            return f"API Error: {api_data.get('msg')}"
    else:
        return f"Failed to fetch data: {response.status_code}"
    

def geocode_location(latitude, longitude, address):
    data = pd.DataFrame({
        'Latitude': [latitude],
        'Longitude': [longitude],
        'Address': [f"{address.get('road', '')}, {address.get('city', '')}, {address.get('state', '')}"]
    })
    fig = px.scatter_mapbox(
        data,
        lat="Latitude",
        lon="Longitude",
        hover_name="Address",
        zoom=14,
        mapbox_style="carto-positron",
        title="Geocoded Crime Location"
    )
    return fig.to_html(full_html=False)


@app.route('/visualize_geocode', methods=['GET'])
def visualize_geocode():
    response = requests.get(f"{API_BASE_URL}/geocode?key=123&city=Chicago&sub_category=Assault" )
    if response.status_code == 200:
        geocode_data = response.json()
        if 'latitude' in geocode_data and 'longitude' in geocode_data:
            latitude = geocode_data['latitude']
            longitude = geocode_data['longitude']
            address = geocode_data['address']
            chart_html = geocode_location(latitude, longitude, address)
            return render_template("main.html", chart_html=chart_html)
        else:
            return f"Geocode Error: {geocode_data.get('error', 'Unknown error')}", 404
    else:
        return f"Failed to fetch geocode data: {response.status_code}", 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
