import pandas as pd
import logging
from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Email
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
import os
# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define forms
class CountyForm(FlaskForm):
    county = HiddenField('County', validators=[DataRequired()])
    state = HiddenField('State', validators=[DataRequired()])
    submit = SubmitField('Next')


class AcreForm(FlaskForm):
    acres = IntegerField('Number of Acres', validators=[DataRequired()])
    submit = SubmitField('Next')

class EmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

# Load data from CSV at the start of the app
data = pd.read_csv('static/county_scenarios.csv')  # Adjust path if needed

# Create a directory for plots if not exists
if not os.path.exists('static/plots'):
    os.makedirs('static/plots')

def get_scenario_data(state, county):
    # Filter data based on the selected county and state
    county_data = data[(data['State'] == state) & (data['County'] == county)]
    
    if county_data.empty:
        logging.warning(f"No data found for County: {county}, State: {state}")
        return {}

    # Group by Scenario and Year, then calculate average values
    avg_data = county_data.groupby(['Scenario', 'Year'])['Value'].mean().reset_index()

    # Create bar plots for each scenario
    scenarios = ['Conservative', 'Moderate', 'High Net']
    plot_paths = {}
    for scenario in scenarios:
        scenario_data = avg_data[avg_data['Scenario'] == scenario]
        if not scenario_data.empty:
            plt.figure(figsize=(10, 6))
            plt.bar(scenario_data['Year'], scenario_data['Value'], color='skyblue')
            plt.title(f'{scenario} Scenario for {county}, {state}')
            plt.xlabel('Year')
            plt.ylabel('Average Value')
            plt.xticks(rotation=45)
            plot_path = f'static/plots/{county}_{state}_{scenario}.png'
            plt.savefig(plot_path)
            plt.close()
            plot_paths[scenario] = plot_path

    return plot_paths, avg_data.groupby('Scenario')['Value'].mean().to_dict()



@app.route("/", methods=["GET", "POST"])
def county():
    form = CountyForm()
    if request.method == "POST":
        # Print form data for debugging
        print("Form data received:", request.form)

    if form.validate_on_submit():
        county = request.form.get('county')
        state = request.form.get('state')

        # Check if county and state are correctly passed
        if not county or not state:
            print("County or state not received.")
            return render_template("county.html", form=form, step=1)  # Re-render form if data is missing

        print(f"County submitted: {county}")
        print(f"State submitted: {state}")

        session['county'] = county
        session['state'] = state

        return redirect(url_for("acres"))
    
    return render_template("county.html", form=form, step=1)



@app.route("/acres", methods=["GET", "POST"])
def acres():
    form = AcreForm()
    if form.validate_on_submit():
        session['acres'] = form.acres.data  # Store the acres in session
        # Log the acreage to console
        logging.info(f"Acreage entered: {form.acres.data}")
        return redirect(url_for("policy"))
    return render_template("acres.html", form=form, step=2)

@app.route("/policy", methods=["GET", "POST"])
def policy():
    county = session.get('county')
    state = session.get('state')
    plot_paths, averages = get_scenario_data(state, county)

    form = EmailForm()
    if form.validate_on_submit():
        session['email'] = form.email.data
        return redirect(url_for("thanks"))

    # Prepare data for JavaScript
    scenario_data = {
        "labels": list(averages.keys()),
        "values": list(averages.values())
    }

    return render_template("policy.html", plot_paths=plot_paths, averages=averages, scenario_data=scenario_data, step=3, form=form)





@app.route("/thanks")
def thanks():
    return render_template("thanks.html")

if __name__ == "__main__":
    app.run(debug=True)
