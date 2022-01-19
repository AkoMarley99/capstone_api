from flask import Flask, request, jsonify, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from io import BytesIO

from flask_cors import CORS
import os


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")


db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS (app)



class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False,)
    description = db.Column(db.String, nullable =False,)
    company = db.Column(db.String, nullable=False)

    def __init__(self, title, description, company):
        self.title = title
        self.description = description
        self.company = company

class JobSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "description", "company" )

job_schema = JobSchema()
multiple_job_schema = JobSchema(many=True)

class FileContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    data = db.Column(db.LargeBinary)

class LogIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False,)
    password = db.Column(db.String, nullable =False,)

    def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password



class LogInSchema(ma.Schema):
     class Meta:
        fields = ("id", "user_name", "password")


login_schema = LogInSchema()

@app.route('/job/add', methods=["POST"])
def add_job():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be sent as JSON')

    post_data = request.get_json()
    title = post_data.get('title')
    description = post_data.get('description')
    company = post_data.get('company')

    exissting_job_check = db.session.query(Job).filter(Job.title == title).filter(Job.company == company).first()
    if exissting_job_check is not None:
        return jsonify("Error: Job already exists ")

    new_record = Job(title, description, company)
    db.session.add(new_record)
    db.session.commit()

    return jsonify(job_schema.dump(new_record))

@app.route('/job/get', methods=["GET"])
def get_all_jobs():
    all_jobs = db.session.query(Job).all()
    return jsonify(multiple_job_schema.dump(all_jobs))
    
@app.route('/job/get/<id>', methods=["GET"])
def get_job(id):
    job = db.session.query(Job).filter(Job.id == id).first()
    return jsonify(job_schema.dump(job))


@app.route('/job/update/<name>', methods= ["PUT"])
def update_job(name):
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be sent as JSON')
    
    put_data = request.get_json()
    title = put_data.get('title')
    description = put_data.get_json('description')

    new_record = db.session.query(Job).filter(Job.title == title).first()

    job.description = description
    db.session.commit()
    return jsonify(job_schema.dump(job))

@app.route('/job/delete/<id>', methods=["DELETE"])
def delete_job_by_id(id):
    job_to_delete = db.session.query(Job).filter(Job.id == id).first()
    db.session.delete(job_to_delete)
    db.session.commit()

    return jsonify('Job Deleted!')






@app.route('/upload', methods= ['POST'])
def upload():
    file = request.files['inputFile']

    newFile = FileContent(name=file.filename, data=file.read())
    db.session.add(newFile)
    db.session.commit()


    return 'saved ' + file.filename + ' to the database!'

@app.route('/download/<id>', methods=["GET"])
def download(id):
    file_data = db.session.query(FileContent).filter(FileContent.id == id). first()
    return send_file(BytesIO(file_data.data), download_name="Resume.pdf", as_attachment=True)







@app.route('/login/add', methods=["POST"])
def add_login():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be sent as JSON')

    post_data = request.get_json()
    user_name = post_data.get('user_name')
    password = post_data.get('password')

    exissting_login_check = db.session.query(LogIn).filter(LogIn.user_name == user_name).filter(LogIn.password == password).first()
    if exissting_login_check is not None:
        return jsonify("created")

    new_record = LogIn(user_name, password)
    db.session.add(new_record)
    db.session.commit()

    return jsonify(login_schema.dump(new_record))

@app.route('/login/get/<user_name>', methods=['GET'])
def get_login(user_name):
    
    login = db.session.query(LogIn).filter(LogIn.user_name == user_name).first()
    return jsonify(login_schema.dump(login))

@app.route('/login/delete/<user_name>', methods=["DELETE"])
def login_to_delete(user_name):
    login_to_delete = db.session.query(LogIn).filer(LogIn.user_name == user_name).first()
    db.session.delete(login_to_delete)
    db.session.commit()

    return jsonify('Login Deleted!')





if __name__ == "__main__" : 
    app.run(debug=True)