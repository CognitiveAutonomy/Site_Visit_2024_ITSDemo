# Demo
Code for NSF CPS Site Visit 2024 Quadrotor Demo 

Use Quadrotor_FF.yaml file to download all packages necessary. You can refer to instructions here: 
    https://saturncloud.io/blog/how-to-install-packages-from-yaml-file-in-conda-a-guide/
Alternative, I have also provided a spec-file named spec-file.txt which can also be used to download the correct packages (but sometimes I've had bugs with this method on my laptop)

For now, you will also need a working copy of MATLAB 2023 or 2024 for the learning stage classification. To install the MATLAB Enginer api, you can use pip install from the system prompt (I used a conda terminal). To install from the MATLAB folder, on Windows® type:
    cd "matlabroot\extern\engines\python"
    python -m pip install .
For me, matlabroot is 'C:\Program Files\MATLAB\R2024b'
For more information go to:
    https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html

You will need some sort of game controller to play the game. If you are using Thrustmaster T.Hotas 4, you do not have to change the input device. HOWEVER, if you are using a different game controller, change the input_device variable on line 15 in main. You can refer to the comment on line 14.

You will also need the API key for the feedback to generate. Please message me on Slack for the key as I am unable to share it on Github. You will need to enter the key into the api_key variable around line 33 of the feedback.py file in QuadrotorEnv.

You can play the game by just running the main file. The code is set to have users play through 15 trials. Currently, the instructions are not updated to include information on learning stage classification or formative feedback generation. This will be added later. 

IF POSSIBLE, when a user has completed all 15 trials, please send me the contents of ./Demo/assets/records. It would really help me :) If you think the feedback has some issues, please let me know which trials you have comments on so that I can look into it.

If there are any questions, feel free to message me!

