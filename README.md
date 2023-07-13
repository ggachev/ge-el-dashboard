# ge-el-dashboard
Implementation of web-based dashboard for controlling a grid emulator (GE+ 10 vAC/DC) and electronic load (EL+ 10 vAC/DC) from cinergia according to my bachelor thesis at the TU Clausthal.

# Requirements
The project was developted on Python 3.11 and is working, with other versions probably also.
To start the project some python libraries are needed to be installed. Those are:
- pyModbusTCP
- Pandas
- Dash
- dash_bootstrap_components

These libraries can be installed with pip like:

python3 -m pip install $libraryname$

# Start the dashboard
To start the dashboard one should run the file dash_app.py.

python3 dash_app.py

It is important to adjust the ip adresses and port of the grid emulator and the electronic load in the file cinergiamodbus.py. Also important is to make sure the right path of the data folder is selected in the files dash_app.py and and metadata.py. To do that the variable UPLOAD_FOLDER_ROOT should be changed.

# Information about the dashboard
When the file is started the dashboard is available on the localhost on port 8050. This can be changed if wanted in the dash_app.py file.
Through the dashboard one is able to start and stop the GE and EL and to set specific voltage or current respectively. Energy data sampling on the connected appliances can be done throught the grid emulator. For the sampling metadata is needed which will be stored in a json file in the folder saved in UPLOAD_FOLDER_ROOT. The structure of the file is:

<img width="147" alt="image" src="https://github.com/ggachev/ge-el-dashboard/assets/38385295/5ab4853c-ecdd-485a-9111-721be7139ca6">

The samples are stored also there in csv files storing all outputs that the GE has. The names of the files are incremented after every sampling done and stored with the number as name.
