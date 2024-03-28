from flask import Flask, request, jsonify, render_template
import pandas as pd
import re
from flask_cors import CORS

app = Flask(__name__)

# Load the sample data from the Excel file
data = pd.read_excel('seismicDataForExam-1.xlsx')
CORS(app)  # Enable CORS for all routes


@app.route('/check_data')
def check_data():
    return jsonify(data.to_dict(orient='records'))


def process_search_term(term):
    exact_phrase_match = False

    # Check if the term is enclosed within double quotes
    if term.startswith('"') and term.endswith('"'):
        # Double Quotes: Exact phrase matching
        processed_term = term[1:-1]
        return [processed_term], True

    # If not enclosed within double quotes, split the term as before
    terms = []
    if ',' in term:
        # Split by comma only if it's not enclosed within double quotes
        terms = [t.strip('"') for t in term.split(',')]
    else:
        terms = [term.strip('"')]

    processed_terms = []
    for t in terms:
        # Check if the term contains '..' indicating a numeric range
        if '..' in t:
            # Double Dots: Numeric range search
            try:
                range_start, range_end = map(float, t.split('..'))
                processed_terms.append((range_start, range_end))
            except ValueError:
                # Handle the case where the string cannot be converted to floats
                processed_terms.append(t)
        else:
            # Regular search term
            processed_terms.append(t)

    return processed_terms, exact_phrase_match


@app.route('/search', methods=['GET'])
def search_data():
    query = request.args.get('query', '')
    min_length, max_length = map(float, request.args.get('length_range', '10..49').split('..'))

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    terms = [term.strip() for term in query.split(',')]

    results = data.copy()

    filtered_results = None

    for term in terms:
        processed_term, exact_phrase_match = process_search_term(term)
        sub_results = None

        for p_term in processed_term:
            if isinstance(p_term, tuple):
                range_start, range_end = p_term
                sub_results_temp = results[
                    (results.select_dtypes(include='number') >= range_start) &
                    (results.select_dtypes(include='number') <= range_end)].dropna()
            elif isinstance(p_term, str):
                if exact_phrase_match:
                    sub_results_temp = results[results.apply(lambda row: p_term in str(row), axis=1)]
                else:
                    sub_results_temp = results[results.apply(lambda row: bool(re.search(p_term, str(row))), axis=1)]

            if sub_results is None:
                sub_results = sub_results_temp
            else:
                sub_results = pd.concat([sub_results, sub_results_temp])

        if filtered_results is None:
            filtered_results = sub_results
        else:
            filtered_results = pd.merge(filtered_results, sub_results, how='inner',
                                        on=data.columns.tolist())

    # Filter results to exclude those with more than two terms in the "BLOCK" field
    if filtered_results is not None and not filtered_results.empty:
        filtered_results['BLOCK_terms'] = filtered_results['BLOCK'].apply(lambda x: len(x.split(', ')))
        filtered_results = filtered_results[filtered_results['BLOCK_terms'] <= 2]

    if filtered_results is not None and not filtered_results.empty:
        paginated_results = filtered_results.to_dict(orient='records')
        total_pages = (len(paginated_results) - 1) // per_page + 1
        paginated_results = paginated_results[(page - 1) * per_page:page * per_page]

        return jsonify({
            "results": paginated_results,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        })

    return jsonify({
        "results": [],
        "page": page,
        "per_page": per_page,
        "total_pages": 0
    })


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
