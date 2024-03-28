# app.py
from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import re
app = Flask(__name__)

# Load Excel file
excel_data = pd.read_excel('seismicDataForExam-1.xlsx')

# Define global variables for pagination
PER_PAGE = 10

def paginate_dataframe(df, page, per_page):
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    total_pages = -(-len(df) // per_page)  # Ceiling division to get total pages
    return df.iloc[start_index:end_index], total_pages

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/search', methods=['GET'])
def search():
    if request.method == 'GET':
        query = request.args.get('query', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

    print("query is=", query)
    filtered_data = excel_data
    
    #checking for - operations
    if query.startswith('-'):
        extracted_string = query.split('"')[1]
        print("Extracted:", extracted_string)
        filtered_data = filtered_data[~filtered_data['BLOCK'].str.contains(extracted_string, case=False)]
    
    elif re.match(r'^PM\d+\s+PM\d+\s+"\d+\.\.\d+"$', query):
        pm_numbers = re.findall(r'PM\d+', query)
        numbers = re.findall(r'\d+', query)
        quoted_numbers = re.findall(r'"([^"]*)"', query)[0].split('..')

        all_numbers = numbers + quoted_numbers

        start, end = map(int, all_numbers[-2:])
        filtered_data = filtered_data[filtered_data['BLOCK'].str.contains('|'.join(pm_numbers), case=False)]
        filtered_data = filtered_data[(filtered_data['LENGTH_KM'] >= start) & (filtered_data['LENGTH_KM'] <= end)]
    
    elif '*' in query:
         # Split the query into parts
        start_string, end_string = query.split('*')
        
        # Construct regex pattern
        regex_pattern = f'^{re.escape(start_string)}.*{re.escape(end_string)}$'
        print("regex pattern: {}".format(regex_pattern))
        
        # Filter the data based on the regex pattern
        filtered_data = filtered_data[filtered_data['BLOCK'].str.match(regex_pattern, case=False)]
    


    else:
        data = re.findall(r'"([^"]*)"', query)
        print(data[0])
        filtered_data = filtered_data[filtered_data['BLOCK'].str.contains(data[0], case=False)]

      

       
            
   
    
    total_results = len(filtered_data)
    total_pages = -(-total_results // per_page)  # Ceiling division
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_results)
    paginated_data = filtered_data[start_idx:end_idx]

    # Convert filtered data to JSON
    results_list = paginated_data.to_dict(orient='records')
    
    return jsonify({
        "results": results_list,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    })

    
if __name__ == '__main__':
    app.run(debug=True)
