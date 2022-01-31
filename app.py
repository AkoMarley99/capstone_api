from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://plwebiwmmkuzbc:81b1f9ce067c158920942919e3890c0182e028b8a354c0565f57739046333dce@ec2-34-194-171-47.compute-1.amazonaws.com:5432/df23ldq2ho0j0v")

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
CORS (app)
# _______________________JOB_______________________
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

# _______________________USER_______________________
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ("username", "password")

user_schema = UserSchema()
multiple_user_schema = UserSchema(many=True)

# _______________________JOB_______________________
@app.route('/job/add', methods=["POST"])
def add_job():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be sent as JSON')

    post_data = request.get_json()
    title = post_data.get('title')
    description = post_data.get('description')
    company = post_data.get('company')

    existing_job_check = db.session.query(Job).filter(Job.title == title).filter(Job.company == company).first()
    if existing_job_check is not None:
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

@app.route('/job/update/<id>', methods= ["PUT"])
def update_job_by_id(id):
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be sent as JSON')

    put_data = request.get_json()
    title = put_data.get('title')
    description = put_data.get('description')

    job_to_update = db.session.query(Job).filter(Job.id == id).first()

    if title != None:
        job_to_update.title = title
    if description != None:
        job_to_update.description = description
   
    db.session.commit()

    return jsonify(job_schema.dump(job_to_update))

@app.route('/job/delete/<id>', methods=["DELETE"])
def delete_job_by_id(id):
    job_to_delete = db.session.query(Job).filter(Job.id == id).first()
    db.session.delete(job_to_delete)
    db.session.commit()

    return jsonify('Job Deleted!')

# _______________________Verification_______________________

@app.route("/user/add", methods=["POST"])
def add_user():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")

    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    new_record = User(username, pw_hash)
    db.session.add(new_record)
    db.session.commit()

    return jsonify(user_schema.dump(new_record))

@app.route("/user/verification", methods=["POST"])
def verification():
    if request.content_type != "application/json":
        return jsonify("Error: Check your headers!")

    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")

    user = db.session.query(User).filter(User.username == username).first()

    if user is None:
        return jsonify("User NOT verified")

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify("User NOT verified")

    return jsonify("User verified")

@app.route("/user/get", methods=["GET"])
def get_all_users():
    all_users = db.session.query(User).all()
    return jsonify(multiple_user_schema.dump(all_users))

@app.route("/user/get/<username>", methods=["GET"])
def get_user(username):
    user = db.session.query(User).filter(User.username == username).first()
    return jsonify(user_schema.dump(user))

@app.route("/user/updatePassword/<id>", methods=["PUT"])
def update_password(id):
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    password = request.get_json().get("password")
    user = db.session.query(User).filter(User.id == id).first()
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user.password = pw_hash

    db.session.commit()

    return jsonify(user_schema.dump(user))


if __name__ == "__main__" : 
    app.run(debug=True)