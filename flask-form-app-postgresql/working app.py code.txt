from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, send_file
import csv
from io import BytesIO, StringIO # Add StringIO to the import
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import logging
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField
from wtforms.validators import DataRequired, Email
from flask_mail import Mail, Message

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()  # This will output to console as well
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Add a secret key for flash messages
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config['MAIL_USERNAME'] = "spacedragoncode@gmail.com"
app.config["MAIL_PASSWORD"] = "dzqg rkoq oyjd xdqh"

db = SQLAlchemy(app)

mail = Mail(app)

class Form(db.Model):
    __tablename__ = 'forms'  # Explicitly naming the table
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)
    occupation = db.Column(db.String(80), nullable=False)

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

            message_body = f"""Hello {first_name},

            Thank you for your submission!

            Here are the details you submitted:
            First Name: {first_name}
            Last Name: {last_name}
            Date: {date}

            Thank you!"""
            message = Message(subject="Form Submission",
                               sender=app.config["MAIL_USERNAME"],
                               recipients=[email],
                               body=message_body)
            mail.send(message)

            flash(f"{first_name}, your form was submitted successfully!", 'success')
            return redirect(url_for('index'))
        
        # Get filter and sort parameters
        filter_id = request.args.get('filter_id')
        filter_fname = request.args.get('filter_fname')
        filter_lname = request.args.get('filter_lname')
        filter_date = request.args.get('filter_date')
        sort_by = request.args.get('sort', 'id')  # Default sort by ID
        order = request.args.get('order', 'asc')  # Default ascending order
        
        # Start with base query
        query = Form.query
        
        # Apply filters if they exist
        if filter_id:
            query = query.filter(Form.id == filter_id)
        if filter_fname:
            query = query.filter(Form.first_name.ilike(f'%{filter_fname}%'))
        if filter_lname:
            query = query.filter(Form.last_name.ilike(f'%{filter_lname}%'))
        if filter_date:
            date_obj = datetime.strptime(filter_date, "%Y-%m-%d").date()
            query = query.filter(Form.date == date_obj)
        
        # Apply sorting
        sort_column = getattr(Form, sort_by)
        if order == 'desc':
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)
        
        # Add pagination
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Number of items per page
        
        # Modify your query to include pagination
        paginated_data = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template("index.html", 
                             form_data=paginated_data.items,
                             pagination=paginated_data,
                             sort_by=sort_by,
                             order=order)
                             
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        db.session.rollback()
        flash("An error occurred while submitting the form.", "error")
        return redirect(url_for('index'))

@app.route("/download")
def download():
    # Create a BytesIO object to write CSV data
    si = StringIO()
    cw = csv.writer(si)
    
    # Write headers
    cw.writerow(['ID', 'First Name', 'Last Name', 'Email', 'Date', 'Occupation'])
    
    # Get all records from database
    records = Form.query.all()
    
    # Write records
    for record in records:
        cw.writerow([record.id, record.first_name, record.last_name, 
                    record.email, record.date, record.occupation])
    
    output = si.getvalue()
    si.close()
    
    # Create a BytesIO object from the string output
    bio = BytesIO()
    bio.write(output.encode('utf-8'))
    bio.seek(0)
    
    return send_file(
        bio,
        mimetype='text/csv',
        as_attachment=True,
        download_name='form_data.csv'
    )

#Adding csv upload functionality
# Add this after your existing routes
@app.route("/upload", methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        if file and file.filename.endswith('.csv'):
            stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            for row in csv_reader:
                try:
                    # Try different date formats
                    date_str = row['Date']
                    try:
                        # Try YYYY-MM-DD format
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    except ValueError:
                        try:
                            # Try DD/MM/YYYY format
                            date_obj = datetime.strptime(date_str, "%d/%m/%Y").date()
                        except ValueError:
                            # Try MM/DD/YYYY format
                            date_obj = datetime.strptime(date_str, "%m/%d/%Y").date()
                    
                    form = Form(
                        first_name=row['First Name'],
                        last_name=row['Last Name'],
                        email=row['Email'],
                        date=date_obj,
                        occupation=row['Occupation']
                    )
                    db.session.add(form)
                
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error processing row: {str(e)}', 'error')
                    return redirect(url_for('index'))
            
            db.session.commit()
            flash(f"{first_name}, your CSV file has been uploaded and processed successfully!", "success")
        else:
            flash('Please upload a CSV file', 'error')
            
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Error uploading file: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == "__main__":
    print("Starting Flask application...")
    with app.app_context():
        db.create_all()
        print("Database tables created/verified")
    
    print("Server starting at http://127.0.0.1:5001")
    app.run(
        host='127.0.0.1',
        port=5001,
        debug=True,
        use_reloader=True
    )

