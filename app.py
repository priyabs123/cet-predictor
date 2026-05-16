from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load data
df = pd.read_csv('cet_data.csv')

@app.route('/')
def home():
    districts = sorted(df['district'].unique().tolist())
    branches = sorted(df['branch_name'].unique().tolist())
    return render_template('index.html', districts=districts, branches=branches)

@app.route('/predict', methods=['POST'])
def predict():
    rank = int(request.form['rank'])
    category = request.form['category']
    branch = request.form['branch']
    district = request.form.get('district', 'All')

    # Filter by category
    filtered = df[df['category'] == category]

    # Filter by branch
    if branch != 'All':
        filtered = filtered[filtered['branch_name'] == branch]

    # Filter by district
    if district != 'All':
        filtered = filtered[filtered['district'] == district]

    # Filter colleges where cutoff rank >= student rank
    eligible = filtered[filtered['cutoff_rank'] >= rank].copy()

    # Sort by cutoff rank
    eligible = eligible.sort_values('cutoff_rank')

    # Add chance percentage
    def get_chance(cutoff, student_rank):
        diff = cutoff - student_rank
        if diff >= 5000:
            return 'High ✅'
        elif diff >= 2000:
            return 'Medium 🟡'
        else:
            return 'Low 🔴'

    eligible['chance'] = eligible.apply(
        lambda row: get_chance(row['cutoff_rank'], rank), axis=1)

    results = eligible[[
        'college_name', 'branch_name', 'cutoff_rank',
        'location', 'district', 'college_type', 'chance'
    ]].to_dict('records')

    return jsonify({
        'results': results,
        'total': len(results),
        'rank': rank,
        'category': category
    })

if __name__ == '__main__':
    app.run(debug=True)