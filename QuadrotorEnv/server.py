from flask import Flask, render_template, request, jsonify
import os
import feedback
from datetime import datetime
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    if not os.path.isdir("./static/data"):
        os.mkdir("./static/data")
    return render_template('index.html')

@app.route('/process_log', methods=['POST'])
def process_log():
    data = request.json
    user_id = data['user_id']
    message = data['message']
    
    add_log_entry(user_id, message)

    return jsonify({'message': "Log received"})

@app.route('/process_user_id', methods=['POST'])
def process_user_id():
    data = request.json
    user_id = data['user_id']
    condition = data['condition']

    # make folder for user data
    user_path = f"./static/data/{user_id}"
    if not os.path.isdir(user_path):
        os.mkdir(user_path)

    # save condition
    condition_path = "./static/data/conditions.csv"
    if not os.path.isfile(condition_path):
        with open(condition_path, "w") as f:
            f.write("time,user_id,condition\n")
    with open(condition_path, "a") as f:
        f.write(f"{datetime.now()},{user_id},{condition}\n")

    # start log file
    add_log_entry(user_id, "Received user ID and condition, start log")

    # create file for survey responses
    with open(f"./static/data/{user_id}/survey_responses.csv", "w") as f:
        f.write("trial,selfconfidence,account,increased,outcome\n")

    return jsonify({'message': "User ID processed"})

@app.route('/process_trial_start', methods=['POST'])
def process_trial_start():
    data = request.json
    user_id = data['user_id']
    trial = data['trial']

    # make folder for trial data
    trial_path = f"./static/data/{user_id}/trial_{trial}"
    if not os.path.isdir(trial_path):
        os.mkdir(trial_path)

    # start log file
    add_log_entry(user_id, f"Trial {trial} started")

    # create file for trial data
    with open(f"./static/data/{user_id}/trial_{trial}/trajectory.csv", "w") as f:
        f.write("x,y_js,vx,vy,phi,ux,uy_js\n")

    return jsonify({'message': "Trial started"})

@app.route('/process_survey_responses', methods=['POST'])
def process_survey_responses():
    data = request.json
    user_id = data['user_id']
    trial = data['trial']
    selfconfidence = data['selfconfidence']
    account = data['account']
    increased = data['increased']
    outcome = data['outcome']

    # start log file
    add_log_entry(user_id, f"Received survey responses")

    with open(f"./static/data/{user_id}/survey_responses.csv", "a") as f:
        f.write(f"{trial},{selfconfidence},{account},{increased},{outcome}\n")

    return jsonify({'message': "Survey responses received"})

@app.route('/save_trajectory', methods=['POST'])
def save_trajectory():
    data = request.json
    user_id = data['user_id']
    trial = data['trial']
    trialtime = data['trialTime']
    landvx = data['landVelocityX']
    landvy = data['landVelocityY']
    landattitude = data['landAttitude']
    landpx = data['landPositionX']
    landpy = data['landPositionY']
    successland = data['successLand']
    score = data['score']
    auto_on_off = data['auto_on_off']

    # start log file
    add_log_entry(user_id, f"Saved Trajectory for matlab")

    with open(f"./static/data/{user_id}/results.csv", "a") as f:
        f.write(f"{trial},{trialtime},{landvx},{landvy},{landattitude},{landpx},{landpy},{successland},{score},{auto_on_off},")

    return jsonify({'message': "Trajectory data for matlab stored"})



@app.route('/process_trajectory', methods=['POST'])
async def process_trajectory():
    data = request.json
    user_id = data['user_id']
    trial = data['trial']
    log = data['log']

    # start log file
    add_log_entry(user_id, f"Received trajectory data")

    with open(f"./static/data/{user_id}/trial_{trial}/trajectory.csv", "a") as f:
        f.write(log)

    # fix y positions
    df = pd.read_csv(f"./static/data/{user_id}/trial_{trial}/trajectory.csv")
    df['y_py'] = -(df['y_js'] - 600)
    df['uy_py'] = -df['uy_js']
    df.to_csv(f"./static/data/{user_id}/trial_{trial}/trajectory.csv", index=False)

    return jsonify({'message': "Trajectory data received"})

@app.route('/wait_for_feedback/<userid>/<trial>')
async def wait_for_feedback(userid, trial):
    await wait(userid, trial)
    return "Complete"

def add_log_entry(user_id, entry):
    with open(f"./static/data/{user_id}/log.txt", "a") as f:
        f.write(f"{datetime.now()}: {entry}\n")

async def wait(userid, trial):
    await feedback.main(userid, trial)
    return "Complete"


if __name__ == '__main__':
    app.run(debug=True)
