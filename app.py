import json
import pymysql
import time
import yaml
import requests
from pathlib import Path
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

config = yaml.safe_load(Path("config.yml").read_text())
DB_HOST = config['db']['host']
DB_USER = config['db']['user']
DB_PASSWORD = config['db']['passwd']
DB_NAME = config['db']['db']

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME
    )

@app.route("/crime_category_per_city", methods=['GET'])   #http://127.0.0.1:5000/crime_category_per_city?key=123
def crime_category_per_city():
    key = request.args.get('key')
    if key != '123':
        return jsonify(code=0, msg='Invalid API key', req='crime_category_per_city', sqltime=0)
    start_time = time.time()
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT City, Crime_Category, COUNT(*) AS Crime_Count 
            FROM hovetl_crimes 
            GROUP BY City, Crime_Category
        """
        cur.execute(query)
        results = cur.fetchall()
        conn.close()
        return jsonify(
            code=1,
            msg="Success",
            data=results,
            req='crime_category_per_city',
            sqltime=time.time() - start_time
        )
    except Exception as e:
        return jsonify(
            code=0, 
            msg=f"Error: {str(e)}", 
            req='crime_category_per_city', 
            sqltime=time.time() - start_time
        )

@app.route("/crime_over_years", methods=['GET'])   #http://127.0.0.1:5000/crime_over_years?key=123
def crime_over_years():
    key = request.args.get('key')
    if key != '123':
        return jsonify(code=0, msg='Invalid API key', req='crime_over_years', sqltime=0)
    start_time = time.time()
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT DateYear, COUNT(*) AS Crime_Count 
            FROM hovetl_crimes 
            GROUP BY DateYear
        """
        cur.execute(query)
        results = cur.fetchall()
        conn.close()
        return jsonify(
            code=1,
            msg="Success",
            data=results,
            req='crime_over_years',
            sqltime=time.time() - start_time
        )    
    except Exception as e:
        return jsonify(
            code=0, 
            msg=f"Error: {str(e)}", 
            req='crime_over_years', 
            sqltime=time.time() - start_time
        )
    
@app.route("/crime_per_month", methods=['GET'])  #http:/127.0.0.1:5000/crime_per_month?key=123&city=Seattle
def crime_per_month():
    key = request.args.get('key')
    city = request.args.get('city')
    valid_cities = ["Seattle", "Chicago", "San Francisco"]
    if key != '123':
        return jsonify(code=0, msg='Invalid API key', req='crime_per_month', sqltime=0)
    if not city or city not in valid_cities:
        return jsonify(code=0, msg=f"Invalid city. Valid options: {', '.join(valid_cities)}", req='crime_per_month', sqltime=0)
    start_time = time.time()
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT DateMonth, COUNT(*) AS Crime_Count 
            FROM hovetl_crimes 
            WHERE City = %s 
            GROUP BY DateMonth
        """
        cur.execute(query, (city,))
        results = cur.fetchall()
        conn.close()
        return jsonify(
            code=1,
            msg="Success",
            data=results,
            req='crime_per_month',
            sqltime=time.time() - start_time
        )    
    except Exception as e:
        return jsonify(
            code=0, 
            msg=f"Error: {str(e)}", 
            req='crime_per_month', 
            sqltime=time.time() - start_time
        )

@app.route("/crime_by_date_range", methods=['GET'])  #http:/127.0.0.1:5000/crime_by_date_range?key=123&start_date=2020-01-01&end_date=2024-01-31
def crimes_by_date_range():
    key = request.args.get('key')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if key != '123':
        return jsonify(code=0, msg='Invalid API key', req='crime_by_date_range', sqltime=0)
    if not start_date or not end_date:
        return jsonify(code=0, msg='Start and end dates are required', req='crime_by_date_range', sqltime=0)
    start_time = time.time()
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT CrimeDate, COUNT(*) AS Crime_Count 
            FROM hovetl_crimes 
            WHERE CrimeDate BETWEEN %s AND %s
            GROUP BY CrimeDate
            ORDER BY CrimeDate
        """
        cur.execute(query, (start_date, end_date))
        results = cur.fetchall()
        conn.close()
        return jsonify(
            code=1,
            msg="Success",
            data=results,
            req='crime_by_date_range',
            sqltime=time.time() - start_time
        )   
    except Exception as e:
        return jsonify(
            code=0, 
            msg=f"Error: {str(e)}", 
            req='crime_by_date_range', 
            sqltime=time.time() - start_time
        )
    
@app.route("/crime_comparison_per_year", methods=['GET']) #http://127.0.0.1:5000/crime_comparison_per_year?key=123
def crime_comparison_per_year():
    key = request.args.get('key')
    if key != '123':
        return jsonify(code=0, msg='Invalid API key', req='crime_comparison_per_year', sqltime=0)
    start_time = time.time()
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        query = """
        SELECT City, DateYear, Crime_Category, COUNT(*) AS Crime_Count
        FROM hovetl_crimes
        GROUP BY City, DateYear, Crime_Category
        """
        cur.execute(query)
        results = cur.fetchall()
        conn.close()
        return jsonify(
            code=1,
            msg="Success",
            data=results,
            req='crime_comparison_per_year',
            sqltime=time.time() - start_time
        )   
    except Exception as e:
        return jsonify(
            code=0,
            msg=f"Error: {str(e)}",
            req='crime_comparison_per_year',
            sqltime=time.time() - start_time
        )

@app.route("/crime_statistics_by_category", methods=['GET']) #http://127.0.0.1:5000/crime_statistics_by_category?key=123
def crime_statistics_by_category():
    key = request.args.get('key')
    if key != '123':
        return jsonify(code=0, msg='Invalid API key', req='crime_statistics_by_category', sqltime=0)
    start_time = time.time()
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        query = """
        SELECT Crime_Category, COUNT(*) AS Crime_Count
        FROM hovetl_crimes
        GROUP BY Crime_Category
        """
        cur.execute(query)
        results = cur.fetchall()
        conn.close()
        return jsonify(
            code=1,
            msg="Success",
            data=results,
            req='crime_statistics_by_category',
            sqltime=time.time() - start_time
        )  
    except Exception as e:
        return jsonify(
            code=0,
            msg=f"Error: {str(e)}",
            req='crime_statistics_by_category',
            sqltime=time.time() - start_time
        )
    
@app.route("/crime_per_city_category", methods=['GET']) #http://127.0.0.1:5000/crime_per_city_category?key=123
def crime_rate_per_city():
    key = request.args.get('key')
    if key != '123':
        return jsonify(code=0, msg='Invalid API key', req='crime_rate_per_city', sqltime=0)
    start_time = time.time()
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        query = """
        SELECT City, Crime_Category, COUNT(*) AS Crime_Count
        FROM hovetl_crimes
        GROUP BY City, Crime_Category
        """
        cur.execute(query)
        results = cur.fetchall()
        conn.close()
        return jsonify(
            code=1,
            msg="Success",
            data=results,
            req='crime_rate_per_city',
            sqltime=time.time() - start_time
        ) 
    except Exception as e:
        return jsonify(
            code=0,
            msg=f"Error: {str(e)}",
            req='crime_rate_per_city',
            sqltime=time.time() - start_time
        )


@app.route('/crime_by_day_of_week', methods=['GET']) #http://127.0.0.1:5000/crime_by_day_of_week?key=123
def crime_by_day_of_week():
    key = request.args.get('key')
    if key != '123':
        return jsonify(code=0, msg='Invalid API key', req='crime_by_day_of_week', sqltime=0)
    start_time = time.time()
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        query = """
        SELECT DAYOFWEEK(CrimeDate) AS Day_Of_Week, COUNT(*) AS Crime_Count
        FROM hovetl_crimes
        GROUP BY Day_Of_Week
        ORDER BY Day_Of_Week
        """
        cur.execute(query)
        results = cur.fetchall()
        conn.close()
        return jsonify(
            code=1,
            msg="Success",
            data=results,
            req='crime_by_day_of_week',
            sqltime=time.time() - start_time
        ) 
    except Exception as e:
        return jsonify(
            code=0,
            msg=f"Error: {str(e)}",
            req='crime_by_day_of_week',
            sqltime=time.time() - start_time
        )

@app.route('/crime_details_by_city_category', methods=['GET']) #http://127.0.0.1:5000/crime_details_by_city_category?key=123&city=Seattle&category=Theft
def crime_details_by_city_category():
    key = request.args.get('key')
    city = request.args.get('city')
    category = request.args.get('category')
    if key != '123':
        return jsonify(code=0, msg='Invalid API key', req='crime_details_by_city_category', sqltime=0)
    if not city or not category:
        return jsonify({"error": "Please provide both city and category parameters."}), 400
    allowed_cities = ['Seattle', 'Chicago', 'San Francisco']
    if city not in allowed_cities:
        return jsonify({"error": f"Sorry, we do not have data for the city '{city}'. Supported cities are: {', '.join(allowed_cities)}."}), 400
    start_time = time.time()
    try:
        query = f"""
        SELECT Sub_Category, COUNT(*) AS Crime_Count
        FROM hovetl_crimes
        WHERE City = '{city}' AND LOWER(Crime_Category) LIKE LOWER('%{category}%')
        GROUP BY Sub_Category
        ORDER BY Crime_Count DESC
        """
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query)
        results = cur.fetchall()
        conn.close()
        return jsonify(
            code=1,
            msg="Success",
            data=results,
            req='crime_details_by_city_category',
            sqltime=time.time() - start_time
        ) 
    except Exception as e:
        return jsonify(
            code=0,
            msg=f"Error: {str(e)}",
            req='crime_details_by_city_category',
            sqltime=time.time() - start_time
        )

@app.route('/crime_location_density_by_city', methods=['GET']) #http://127.0.0.1:5000/crime_location_density_by_city?key=123&city=Chicago
def crime_location_density_by_city():
    key = request.args.get('key')
    city = request.args.get('city')

    if key != '123':
        return jsonify(code=0, msg='Invalid API key', req='crime_location_density_by_city', sqltime=0)

    if not city:
        return jsonify({"error": "Please provide a city parameter."}), 400

    allowed_cities = ['Seattle', 'Chicago', 'San Francisco']
    if city not in allowed_cities:
        return jsonify({"error": f"Sorry, we do not have data for the city '{city}'. Supported cities are: {', '.join(allowed_cities)}."}), 400
    start_time = time.time()
    try:
        query = f"""
        SELECT Latitude, Longitude FROM hovetl_crimes
        WHERE City = '{city}'
        """
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query)
        results = cur.fetchall()
        conn.close()
        return jsonify(
            code=1,
            msg="Success",
            data=results,
            req='crime_location_density_by_city',
            sqltime=time.time() - start_time
        ) 
    except Exception as e:
        return jsonify(
            code=0,
            msg=f"Error: {str(e)}",
            req='crime_location_density_by_city',
            sqltime=time.time() - start_time
        )

@app.route('/geocode', methods=['GET'])   #http://127.0.0.1:5000/geocode?key=123&city=Chicago&sub_category=Assault
def geocode():
    key = request.args.get('key')
    city = request.args.get('city')
    sub_category = request.args.get('sub_category')

    if key != '123':
        return jsonify(
            code=0,
            msg='Invalid API key',
            req='geocode'
        )
    if not city or not sub_category:
        return jsonify({
            "error": "Please provide both city and sub-category parameters."
        }), 400
    start_time = time.time()
    try:
        query_cities = "SELECT DISTINCT City FROM hovetl_crimes"
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query_cities)
        cities = [row['City'] for row in cur.fetchall()]
        conn.close()

        if city not in cities:
            return jsonify({
                "error": f"City '{city}' not found in the database. Available cities are: {', '.join(cities)}."
            }), 400
        query = f"""
        SELECT Latitude, Longitude FROM hovetl_crimes
        WHERE City = '{city}' AND LOWER(Sub_Category) LIKE LOWER('%{sub_category}%')
        """
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query)
        results = cur.fetchall()
        conn.close()
        if not results:
            return jsonify({
                "error": "No crimes found for the provided city and sub-category."
            }), 404
        latitude = results[0]['Latitude']
        longitude = results[0]['Longitude']
        url = f'https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json&addressdetails=1'
        response = requests.get(url, headers={'User-Agent': 'Geocoding API client'})
        data = response.json()
        if response.status_code == 200 and 'address' in data:
            address = data['address']
            return jsonify({
                "latitude": latitude,
                "longitude": longitude,
                "address": address
            })
        else:
            return jsonify({
                "error": "Address not found or API limit exceeded."
            }), 404
    except Exception as e:
        return jsonify(
            code=0,
            msg=f"Error: {str(e)}",
            req='geocode'
        )

if __name__ == "__main__":
    app.run(debug=True)