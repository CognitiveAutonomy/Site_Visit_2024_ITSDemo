# Demo
Code for NSF CPS Site Visit 2024 Quadrotor Demo 

Use yaml file to download all packages necessary.
To install the MATLAB Enginer api, you can use pip install from the system prompt (I used a conda terminal). Th
To install from the MATLAB folder, on Windows® type:
    cd "matlabroot\extern\engines\python"
    python -m pip install .
where matlabroot is something like: 'C:\Program Files\MATLAB\R2024b'
For more information go to:
    https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html

You will need some sort of game controller to play the game. If you are using Thrustmaster T.Hotas 4, you do not have to change the input device. HOWEVER, if you are using a different game controller, change the input_device variable on line 15 in main. You can refer to the comment on line 14.


