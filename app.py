from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask import send_file


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class ExperimentData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trial = db.Column(db.Integer)
    condition = db.Column(db.String(50))
    participantId = db.Column(db.String(50))
    x_positions = db.Column(db.PickleType)
    y_positions = db.Column(db.PickleType)
    z_positions = db.Column(db.PickleType)
    timestamps = db.Column(db.PickleType)
class ExperimentDataSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ExperimentData

experiment_schema = ExperimentDataSchema()
experiments_schema = ExperimentDataSchema(many=True)

db.create_all()

@app.route('/postdata', methods=['POST'])
def post_data():
    trial = request.json['trial']
    condition = request.json['condition']
    participantId = request.json['participantId']
    x_positions = request.json['x_positions']
    y_positions = request.json['y_positions']
    z_positions = request.json['z_positions']
    timestamps = request.json['timestamps']

    new_data = ExperimentData(
        trial=trial,
        condition=condition,
        participantId=participantId,
        x_positions=x_positions,
        y_positions=y_positions,
        z_positions=z_positions,
        timestamps=timestamps

    )

    db.session.add(new_data)
    db.session.commit()

    return experiment_schema.jsonify(new_data)

@app.route('/data/<int:trial>/<string:participant>/<string:condition>', methods=['GET'])
def get_data(trial, participant, condition):
    data = ExperimentData.query.filter_by(trial=trial, participantId=participant, condition=condition).first()
    return experiment_schema.jsonify(data)

@app.route('/', methods=['GET'])
def render_graph():
    return render_template('graph.html')

@app.route('/trials', methods=['GET'])
def get_trials():
    trials = db.session.query(ExperimentData.trial).distinct().all()
    return jsonify([trial[0] for trial in trials])

@app.route('/conditions', methods=['GET'])
def get_conditions():
    conditions = db.session.query(ExperimentData.condition).distinct().all()
    return jsonify([condition[0] for condition in conditions])

@app.route('/participants', methods=['GET'])
def get_participants():
    participants = db.session.query(ExperimentData.participantId).distinct().all()
    return jsonify([participant[0] for participant in participants])

@app.route('/download_database', methods=['GET'])
def download_database():
    db_path = app.config['SQLALCHEMY_DATABASE_URI'][10:]  # Extract the database file path from the URI
    return send_file(db_path, as_attachment=True)