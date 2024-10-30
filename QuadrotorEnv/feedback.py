import base64
import requests
import dotenv

import pathlib
import textwrap3
import random

from datetime import datetime
from diagnostics import *
from visual_feedback import *

# import tracemalloc

# tracemalloc.start()

# async def wait_for_feedback(userid, trial):
#     await wait(userid, trial)
#     return "Complete"

# def add_log_entry(userid, entry):
#     with open(f"../assets/records/trial_data/{userid}_log.txt", "a") as f:
#         f.write(f"{datetime.now()}: {entry}\n")

# async def wait(userid, trial):
#     await main(userid, trial)
#     return "Complete"

# async def main(userid, trial=1):
def main(userid, trial=1, LS=1, SC=0, control_mode = 'manual', landing = 'Safe Landing'):
  # OpenAI API Key
  # config = dotenv.dotenv_values(".env")
  api_key = 'ENTER API KEY'
  if api_key == 'ENTER API KEY':
    print('update API key')
  

  # Function to encode the image
  def encode_image(image_path):
      with open(image_path, "rb") as image_file:
          return base64.b64encode(image_file.read()).decode('utf-8')

  # Path to files
  diagnostics = Diagnostics(userid, trial)
  diagnostics.run()
  with open(f"../assets/records/trial_data/{userid}_log.txt", "a") as f:
      f.write(f"{datetime.now()}: Improvement area is {diagnostics.improvement_area}\n")

  visuals = VisualFeedback(userid, trial)
  visuals.plot_trajectory()

  # Getting the base64 string
  base64_image = encode_image(f"../assets/records/trial_data/{userid}_trial_{trial}_trajectory.png")

  headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}"
  }

  feedback_prompt = """
  You are a critical evaluator. You are giving feedback to a drone pilot who is learning to fly a drone."""

  num = random.randrange(1, 10)
  feedbacktype = ""
  # if num <= 3:
  if (LS == 1 and SC < 30) or (LS == 2 and SC <= 65 and SC > 30) or (LS == 3 and SC > 65 and landing == 'Unsafe Landing'):
    if landing == 'Unsafe Landing' or landing == 'Safe Landing':
      if control_mode == 'manual':
        feedback_prompt += """
        Give feedback to a drone pilot in the following format:
        compliment, improvement area, actionable, confidence, neutral
        """
      else:
        feedback_prompt += """
        Give feedback to a drone pilot in the following format:
        compliment, improvement area, actionable, confidence, neutral, automation
        """
    else:
      if control_mode == 'manual':
        feedback_prompt += """
        Give feedback to a drone pilot in the following format:
        improvement area, actionable, confidence, neutral
        """
      else:
        feedback_prompt += """
        Give feedback to a drone pilot in the following format:
        improvement area, actionable, confidence, neutral, automation
        """
    feedbacktype = "neutral"
  # elif num <= 6:
  elif (LS == 1 and SC >= 30) or (LS == 2 and SC > 65):
    if control_mode == 'manual':
      feedback_prompt += """
      Give feedback to a drone pilot in the following format: 
      improvement area, actionable, reflection, negative
      """
    else:
      feedback_prompt += """
      Give feedback to a drone pilot in the following format: 
      improvement area, actionable, reflection, negative, automation
      """
    feedbacktype = "negative"
  elif (LS == 2 and SC < 30) or (LS == 3 and SC < 65 and landing == 'Unsafe Landing'):
    if landing == 'Unsafe Landing' or landing == 'Safe Landing':
      if control_mode == 'manual':
        feedback_prompt += """
        Give feedback to a drone pilot in the following format: 
        compliment, actionable, confidence, positive
        """
      else:
        feedback_prompt += """
        Give feedback to a drone pilot in the following format: 
        compliment, confidence, positive, automation
        """
    else:
        if control_mode == 'manual':
          feedback_prompt += """
          Give feedback to a drone pilot in the following format: 
          actionable, confidence, positive
          """
        else:
          feedback_prompt += """
          Give feedback to a drone pilot in the following format: 
          actionable, confidence, positive, automation
          """
    feedbacktype = "positive"
  else:
     if control_mode == 'manual':
      if SC < 65:
        feedback_prompt += """
        Give feedback to a drone pilot in the following format: 
        compliment
        """
        feedbacktype = "short positive"
      else:
        feedback_prompt += """
        Give feedback to a drone pilot in the following format: 
        compliment
        """
        feedbacktype = "short neutral"
     else:
      if SC < 65:
        feedback_prompt += """
        Give feedback to a drone pilot in the following format: 
        compliment, automation
        """
        feedbacktype = "short positive"
      else:
        feedback_prompt += """
        Give feedback to a drone pilot in the following format: 
        compliment, automation
        """
        feedbacktype = "short neutral"
  
  feedback_prompt += """
  Image Context:
  1. The left vertical black line corresponds to x = -30.
  2. The right vertical black line corresponds to x = 30.
  3. The top horizontal black line corresponds to y = 33.75.
  4. The bottom horizontal black line corresponds to y = 0.
  5. The gray rectangle is the landing pad with coordinates -7.25 < x < 7.25 and 0 < y < 4.
  6. The green star is the starting position of the drone.
  7. The red star is the ending position of the drone.
  8. The black curve is the trajectory of the drone as the pilot attempts to complete the target task.

  Target Task:
  1. The state variables are the drone's x position in meters (x), y position in meters (y), speed in meters per second (s), and tilt angle in degrees (\phi)
  2. The task is defined using signal temporal logic specifications, which are indicated using $…$
  3. Safety component: $P_1 = x > -30 \land x < 30 \land y > 0 \land y < 33.75$
  4. Landing component: $P_2 = x > -6.5 \land x < 6.5 \land y < 33.75 \land s <= 5 \land \phi > -\pi/18 \land \phi < \pi/18$
  5. Complete task: $P_1 Until P_2$
  6. An unsuccessful landing or crash is when the drone's ending x and y positions are not within the bounds of $x > -6.5 \land x < 6.5 \land y < 33.75 \land$.
  7. An unsafe landing is when the drone's ending x and y positions are within the bounds of $x > -6.5 \land x < 6.5 \land y < 33.75 \land$, but the end speed and tilt angle are not violate $\land s > 5 \land \phi > -\pi/18 \land \phi < \pi/18$
  8. a safe landing is when the drone's end state variables are all within $P_1$ and $P_2$

  """

  feedback_prompt += """
  Rules:
  1. Make decisions using the provided image of the drone trajectory, image context, and target task information.
  2. You can assume the dynamics of the drone allow the pilot to achieve the task. 
  3. Do not add additional elements to the feedback not shown above. Only use the elements given in the template.
  4. Do not use mention math, logic, or robustness terms when describing the task. Only use natural language to describe elements of the task.
  """

  # if num <= 3:
  if (LS == 1 and SC < 30) or (LS == 2 and SC <= 65 and SC > 30) or (LS == 3 and SC > 65 and landing == 'Unsafe Landing'):
    if landing == 'Unsafe Landing':
      feedback_prompt += """
      1. The area the pilot can most improve in is """ + diagnostics.improvement_area + """. This will be referred to as {top_improvement}.
      2. Replace {compliment} with one sentence describing a positive aspect of the pilot's performance relative to the target task. If {top_improvement} is smoothness or efficiency, congratulate the pilot on successfully completing the task. If {top_improvement} is landing, congratulate the pilot on avoiding a crash.
      3. Replace {improvement_area} with a one sentence description of which part of the target task the pilot can most improve in, which I identified as {top_improvement}. Specifically refer to a component of the task rather than an overall assessment of the performance.
      4. Replace {actionable} with a one sentence specific control action strategy the pilot can make to improve in {top_improvement}. The possible control actions are thrust (the force applied perpendicular to the top surface of the drone) and tilt (controls the angular acceration of the drone). Only reference these control actions. Do not reference other control actions. Some examples are:
        a. To prevent drifting in one direction, tilt the drone in the opposite direction of the drone's movement and use thrust to stop the drone.
        b. Increase thrust as needed to slow down when descending towards the landing pad. 
        c. Adjust the tilt to align the drone's flight path to the landing pad.
        d. Try adjusting the tilt in small increments in the beginning to keep the drone stable when aligning the drone to the landing pad.
      5. Replace {confidence} with one sentence expressing confidence in the pilot's abilities to achieve at a high level on the target task. Only include such expressions when the {confidence} tag is present.
      6. {neutral} means to provide feedback in a neutral, unbiased, and unprejudiced way.
      """
      if control_mode != 'manual':
        feedback_prompt += """
        7. Replace {automation} with acknowledgement that the pilot recieved assistance and may need more practice manually landing the drone.
        """
    else:
      feedback_prompt += """
      1. The area the pilot can most improve in is """ + diagnostics.improvement_area + """. This will be referred to as {top_improvement}.
      2. Replace {improvement_area} with a one sentence description of which part of the target task the pilot can most improve in, which I identified as {top_improvement}. Specifically refer to a component of the task rather than an overall assessment of the performance.
      3. Replace {actionable} with a one sentence specific control action strategy the pilot can make to improve in {top_improvement}. The possible control actions are thrust (the force applied perpendicular to the top surface of the drone) and tilt (controls the angular acceration of the drone). Only reference these control actions. Do not reference other control actions. Some examples are:
        a. To prevent drifting in one direction, tilt the drone in the opposite direction of the drone's movement and use thrust to stop the drone.
        b. Increase thrust as needed to slow down when descending towards the landing pad. 
        c. Adjust the tilt to align the drone's flight path to the landing pad.
        d. Try adjusting the tilt in small increments in the beginning to keep the drone stable when aligning the drone to the landing pad.
      4. Replace {confidence} with one sentence expressing confidence in the pilot's abilities to achieve at a high level on the target task. Only include such expressions when the {confidence} tag is present.
      5. {neutral} means to provide feedback in a neutral, unbiased, and unprejudiced way.
      """
      if control_mode != 'manual':
        feedback_prompt += """
        6. Replace {automation} with acknowledgement that the pilot recieved assistance and may need more practice manually landing the drone.
        """
  elif (LS == 1 and SC >= 30) or (LS == 2 and SC > 65):
     feedback_prompt += """
     1. The area the pilot can most improve in is """ + diagnostics.improvement_area + """. This will be referred to as {top_improvement}.
     2. Replace {improvement_area} with a one sentence description of which part of the target task the pilot can most improve in, which I identified as {top_improvement}. Specifically refer to a component of the task rather than an overall assessment of the performance.
     3. Replace {actionable} with a one sentence specific control action strategy the pilot can make to improve in {top_improvement}. The possible control actions are thrust (the force applied perpendicular to the top surface of the drone) and tilt (controls the angular acceration of the drone). Only reference these control actions. Do not reference other control actions. Some examples are:
        a. To prevent drifting in one direction, tilt the drone in the opposite direction of the drone's movement and use thrust to stop the drone.
        b. Increase thrust as needed to slow down when descending towards the landing pad. 
        c. Adjust the tilt to align the drone's flight path to the landing pad.
        d. Try adjusting the tilt in small increments in the beginning to keep the drone stable when aligning the drone to the landing pad.
     4. Replace {reflection} with a one sentence task or question that encourages the pilot to reflect on their performance and decide what they can improve on their next attempt.
     5. {negative} means to provide feedback in an unapathetic, cold, and dismissive, way.
     """
     if control_mode != 'manual':
      feedback_prompt += """
      6. Replace {automation} with acknowledgement that the pilot recieved assistance and may need more practice manually landing the drone.
      """
     feedback_prompt += """
     Feedback Examples in {negative} Tone:
     "The drone drifted to the right, indicating some difficulty with tilt control. Try to stop the drifting by tilting in the direction opposite to the drive while increasing thrust to prevent this in the future. Reflect on why the drone moved off course and how improved control could lead to better outcomes. Pay closer attention to the basics controls."
     "The landing speed was excessive. You need to reduce thrust earlier to slow down before reaching the designated landing area. Reflect on how better speed management could ensure a successful landing. This attempt fell short as the speed was not properly controlled, causing the drone to miss the target. It’s crucial to improve your control over thrust to achieve a more precise landing."
     "The drone’s landing angle was not well-controlled, causing an unstable approach to the pad. You need to adjust the tilt to achieve a more level descent and you can use thrust force in the opposite direction of the drift to stabilize the quadrotor. Reflect on how controlling the tilt can help stabilize your landing. A smoother, more controlled descent will result from better angle management."
     "You need to improve in the landing component, as the drone's descent was not always aligned to the landing pad. Specifically, you should focus on making more precise tilt adjustments to center the drone over the target area as well as use thrust force to prevent drifting. Reflect on how your control inputs influenced the final moments of the flight and consider what changes can help achieve a more accurate landing next time. The landing was adequate, but there is room for improvement in achieving a smoother and more controlled descent."
     """

  elif (LS == 2 and SC < 30) or (LS == 3 and SC < 65 and landing == 'Unsafe Landing'):
    if landing == 'Safe Landing' or landing == 'Unsafe Landing':
      feedback_prompt += """
      1. The area the pilot can most improve in is """ + diagnostics.improvement_area + """. This will be referred to as {top_improvement}.
      2. Replace {compliment} with one sentence describing a positive aspect of the pilot's performance relative to the target task. If {top_improvement} is smoothness or efficiency, congratulate the pilot on successfully completing the task. If {top_improvement} is landing, congratulate the pilot on avoiding a crash.
      3. Replace {confidence} with one sentence expressing confidence in the pilot's abilities to achieve at a high level on the target task. Only include such expressions when the {confidence} tag is present.
      4. {positive} means to provide feedback in a positive, encouraging, supportive, and inspiring way.
      """
      if control_mode != 'manual':
        feedback_prompt += """
        5. Replace {actionable} with a one sentence specific control action strategy the pilot can make to improve in {top_improvement}. The possible control actions are thrust (the force applied perpendicular to the top surface of the drone) and tilt (controls the angular acceration of the drone). Only reference these control actions. Do not reference other control actions. Some examples are:
          a. To prevent drifting in one direction, tilt the drone in the opposite direction of the drone's movement and use thrust to stop the drone.
          b. Increase thrust as needed to slow down when descending towards the landing pad. 
          c. Adjust the tilt to align the drone's flight path to the landing pad.
          d. Try adjusting the tilt in small increments in the beginning to keep the drone stable when aligning the drone to the landing pad.
        6. Replace {automation} with acknowledgement that the pilot recieved assistance and may need more practice manually landing the drone.
        """
      else:
        feedback_prompt += """
        5. Replace {actionable} with a one sentence specific control action strategy the pilot can make to improve in {top_improvement}. The possible control actions are thrust (the force applied perpendicular to the top surface of the drone) and tilt (controls the angular acceration of the drone). Only reference these control actions. Do not reference other control actions. For example, to prevent drifting too much in one direction, tilt the drone in the opposite direction while increasing thrust to stop the drifting.
        6"""
    else:
      feedback_prompt += """
      1. The area the pilot can most improve in is """ + diagnostics.improvement_area + """. This will be referred to as {top_improvement}.
      2. Replace {confidence} with one sentence expressing confidence in the pilot's abilities to achieve at a high level on the target task. Only include such expressions when the {confidence} tag is present.
      3. {positive} means to provide feedback in a positive, encouraging, supportive, and inspiring way.
      """
      if control_mode != 'manual':
        feedback_prompt += """
        4. Replace {actionable} with a one sentence specific control action strategy the pilot can make to improve in {top_improvement}. The possible control actions are thrust (the force applied perpendicular to the top surface of the drone) and tilt (controls the angular acceration of the drone). Only reference these control actions. Do not reference other control actions. Some examples are:
          a. To prevent drifting in one direction, tilt the drone in the opposite direction of the drone's movement and use thrust to stop the drone.
          b. Increase thrust as needed to slow down when descending towards the landing pad. 
          c. Adjust the tilt to align the drone's flight path to the landing pad.
          d. Try adjusting the tilt in small increments in the beginning to keep the drone stable when aligning the drone to the landing pad.
        5. Replace {automation} with acknowledgement that the pilot recieved assistance and may need more practice manually landing the drone.
        """
      else:
        feedback_prompt += """
        4. Replace {actionable} with a one sentence specific control action strategy the pilot can make to improve in {top_improvement}. The possible control actions are thrust (the force applied perpendicular to the top surface of the drone) and tilt (controls the angular acceration of the drone). Only reference these control actions. Do not reference other control actions. For example, to prevent drifting too much in one direction, tilt the drone in the opposite direction while increasing thrust to stop the drifting.
        """

  else:
    if SC < 65:
      feedback_prompt += """
      1. Replace {compliment} with one sentence describing a positive aspect of the pilot's performance relative to the target task in a positive tone.
      2. Do not suggest any improvements.
      """
    else:
      feedback_prompt += """
      1. Replace {compliment} with one sentence describing a positive aspect of the pilot's performance relative to the target task in a neutral tone.
      2. Do not suggest any improvements.
      """
    if control_mode != 'manual':
      feedback_prompt += """
      3. Replace {automation} with acknowledgement that the pilot recieved assistance and may need more practice manually landing the drone.
      """

  if (LS >= 3 and landing == "Safe Landing"):
    feedback_prompt += """
    Keep the feedback very short. If possible, you can combine two sentences into one sentence as long as information isn't reduced in a significant way. Remember, your feedback should be in the form of a sentence or very short paragraph. Do not use the phrase "top_improvement" or "{top_improvement}" in your feedback. Replace these with the actual improvement area you identified.
    """
  else:
    feedback_prompt += """
    The shorter the feedback the better. If possible, you can combine two sentences into one sentence as long as information isn't reduced in a significant way. If two sentences seem repetative, remove one. Remember, your feedback should be in the form of a short paragraph. Do not use the phrase "top_improvement" or "{top_improvement}" in your feedback. Replace these with the actual improvement area you identified.
    """

  payload = {
      "model": "gpt-4o-mini",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": feedback_prompt
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
              }
            }
          ]
        }
      ],
      "max_tokens": 1000
  }
  # if LS == 4 or (LS == 3 and landing == 'Safe Landing'):
  #    output = 'Keep up the good work!'
  #    feedbacktype = "short"
  # else:
  response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
  output = response.json()['choices'][0]['message']['content']
  output = output.replace('\u2014', '-')
  output = output.replace('\u2013', '-')
  output = output.replace('\u2019', "'")

  # catch any other unicode characters
  try:
    output.encode('ascii')
  except UnicodeEncodeError as e:
    print(e)

  # generate visual feedback
  visuals.improvement_area = diagnostics.improvement_area
  visuals.generate_visual_feedback()

  # output = "test"

  # save feedback to file
  with open(f"../assets/records/trial_data/{userid}_trial_{trial}_feedback.txt", "w") as f:
      f.write(output)

  with open(f"../assets/records/trial_data/{userid}_trial_{trial}_results.csv", "a") as f:
      f.write(f"{feedbacktype}\n")


  with open(f"../assets/records/trial_data/{userid}_log.txt", "a") as f:
      f.write(f"{datetime.now()}: Saved feedback to file.\n")
