from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SECRET_KEY"] = "arthurmorganwasright69"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
db = SQLAlchemy(app)

class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(80))
    date = db.Column(db.Date)
    occupation = db.Column(db.String(80))

@app.route("/", methods=["GET", "POST"])
def index():
    try:
        if request.method == "POST":
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            email = request.form["email"]
            date = request.form["date"]
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            occupation = request.form["occupation"]
            
            form = Form(first_name=first_name, last_name=last_name, 
                       email=email, date=date_obj, occupation=occupation)
            db.session.add(form)
            db.session.commit()
            flash("Your form was submitted successfully!", "success")
            return redirect(url_for('index'))
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        db.session.rollback()
        flash("An error occurred while submitting the form.", "error")
    
    return render_template("index.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=False, port=5001)  # Set debug to False