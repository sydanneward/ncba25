import pandas as pd
import logging
from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Email

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

def get_scenario_data(state, county):
    # Filter data based on the selected county and state
    county_data = data[(data['State'] == state) & (data['County'] == county)]
    
    if county_data.empty:
        print(f"No data found for State: {state}, County: {county}. Available counties in {state}:",
              data[data['State'] == state]['County'].unique())
        logging.warning(f"No data found for County: {county}, State: {state}")
        return {
            'Conservative': {'value': 0},
            'Moderate': {'value': 0},
            'High Net': {'value': 0}
        }

    # Organize the data in a dictionary by Scenario for the template
    scenarios = {
        scenario: {
            "value": county_data[county_data['Scenario'] == scenario]['Value'].sum()
        }
        for scenario in ['Conservative', 'Moderate', 'High Net']
    }
    return scenarios



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
    scenarios = get_scenario_data(state, county)  # Use both state and county

    form = EmailForm()
    if form.validate_on_submit():
        session['email'] = form.email.data
        return redirect(url_for("thanks"))

    acres = session.get('acres', 1)
    print(f"Acres retrieved from session: {acres}")

    adjusted_scenarios = {
        key: {'value': value['value'] * acres}
        for key, value in scenarios.items()
    }

    return render_template("policy.html", scenarios=adjusted_scenarios, step=3, form=form)


@app.route("/thanks")
def thanks():
    return render_template("thanks.html")

if __name__ == "__main__":
    app.run(debug=True)
