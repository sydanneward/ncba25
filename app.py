from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Email
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Screen 1: County Selection Form
class CountyForm(FlaskForm):
    county = HiddenField('County', validators=[DataRequired()])
    submit = SubmitField('Next')


# Screen 2: Acreage Submission Form
class AcreForm(FlaskForm):
    acres = IntegerField('Number of Acres', validators=[DataRequired()])
    submit = SubmitField('Next')

# Screen 4: Email Submission Form
class EmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


# Routes
@app.route("/", methods=["GET", "POST"])
def county():
    form = CountyForm()
    if form.validate_on_submit():
        session['county'] = form.county.data  # Store the county in session
        return redirect(url_for("acres"))
    return render_template("county.html", form=form, step=1)

@app.route("/acres", methods=["GET", "POST"])
def acres():
    form = AcreForm()
    if form.validate_on_submit():
        session['acres'] = form.acres.data  # Store the acres in session
        return redirect(url_for("policy"))
    return render_template("acres.html", form=form, step=2)

@app.route("/policy")
def policy():
    scenarios = {
        "Conservative": {
            "avg_net": 74145,
            "yearly_data": {
                2023: 114821, 2022: 133589, 2021: 75429, 2020: 113638,
                2019: 176969, 2018: 9047, 2017: 52377, 2016: 51234
                # Add more years as necessary
            }
        },
        "Moderate": {
            "avg_net": 76187,
            "yearly_data": {
                2023: 96112, 2022: 135757, 2021: 62176, 2020: 130808
                # Add more years as necessary
            }
        },
        "High Net": {
            "avg_net": 91408,
            "yearly_data": {
                2023: 23374, 2022: 71886, 2021: 106810, 2020: 143530
                # Add more years as necessary
            }
        }
    }
    
    max_value = max(
        max(scenarios['Conservative']['yearly_data'].values()),
        max(scenarios['Moderate']['yearly_data'].values()),
        max(scenarios['High Net']['yearly_data'].values())
    )
    
    return render_template("policy.html", scenarios=scenarios, max_value=max_value, step=3)

@app.route("/email", methods=["GET", "POST"])
def email():
    form = EmailForm()
    if form.validate_on_submit():
        session['email'] = form.email.data  # Store the email in session
        return redirect(url_for("thanks"))
    return render_template("email.html", form=form, step=4)



@app.route("/thanks")
def thanks():
    return "Thank you for submitting your information!"

if __name__ == "__main__":
    app.run(debug=True)
