import cinergiamodbus
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dcc
import dash, metadata, os, base64, json, pandas, time
from read_threading import RepeatedTimer
from flask import Flask, send_from_directory
from urllib.parse import quote as urlquote
from pathlib import Path

server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "GE & EL Dashboard"

# Define global variables, used for the time left
iterations = 0
spacing = 0
time_rem = 0
time_rem1 = 0
filepath_csv = Path()
filepath_json = Path()

# Define upload folder and upload settings
UPLOAD_FOLDER_ROOT = r"/home/cube/Desktop/ge_el_dash/data/"
@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(UPLOAD_FOLDER_ROOT, path, as_attachment=True)

# Define function to get the files in a directory
def get_files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

# Save all files in /data in a list and sort them
list_of_files = []
for file in get_files(UPLOAD_FOLDER_ROOT):
    if 'csv' in file:
        list_of_files.append(file)
list_of_files.sort()

def update_files_list():
    global list_of_files
    list_of_files = []
    for file in get_files(UPLOAD_FOLDER_ROOT):
        if 'csv' in file:
            list_of_files.append(file)
    list_of_files.sort()

# Table for EU voltage
table_header = [
    html.Thead(html.Tr([html.Th("Denomination"), html.Th("Value")]))
]

row1 = html.Tr([html.Td("Frequency_Ramp_Output"), html.Td("1 Hz/s")])
row2 = html.Tr([html.Td("Frequency_Output_SP"), html.Td("50 Hz")])
row3 = html.Tr([html.Td("Grid_Output_Resistance"), html.Td("0 Ohm")])
row4 = html.Tr([html.Td("Voltage_Ramp_AC_Output_SP"), html.Td("100 V/ms")])
row5 = html.Tr([html.Td("Voltage_Ramp_Phase_Angle_Output_SP"), html.Td("10 deg/ms")])
row6 = html.Tr([html.Td("Voltage_Fundamental_Phase_Angle_SP"), html.Td("0, -120, -240 deg")])
row7 = html.Tr([html.Td("Voltage_Fundamental_AC_SP"), html.Td("230 V")])

table_body = [html.Tbody([row1, row2, row3, row4, row5, row6, row7])]

# Set voltage manually input
input_groups = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div("U"),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="F_Ramp_Output", id="u-f-ramp-output"),
                                dbc.InputGroupText("Hz/s"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="F_Output_SP", id="u-f-output-sp"),
                                dbc.InputGroupText("Hz"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="G_Output_Resistance", id="u-g-output-resist"),
                                dbc.InputGroupText("Ohm"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Voltage_Ramp_AC", id="u-voltage-ramp-ac"),
                                dbc.InputGroupText("V/ms"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Voltage_Ramp_Phase", id="u-voltage-ramp-fund"),
                                dbc.InputGroupText("deg/ms"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Voltage_Fund_Phase", id="u-voltage-fund-phase"),
                                dbc.InputGroupText("deg"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Voltage_Fund_AC", id="u-voltage-fund-ac"),
                                dbc.InputGroupText("V"),
                            ],
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.Div("V"),
                         dbc.InputGroup(
                            [
                                dbc.Input(placeholder="F_Ramp_Output", id="v-f-ramp-output"),
                                dbc.InputGroupText("Hz/s"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="F_Output_SP", id="v-f-output-sp"),
                                dbc.InputGroupText("Hz"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="G_Output_Resistance", id="v-g-output-resist"),
                                dbc.InputGroupText("Ohm"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Voltage_Ramp_AC", id="v-voltage-ramp-ac"),
                                dbc.InputGroupText("V/ms"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Voltage_Ramp_Phase", id="v-voltage-ramp-fund"),
                                dbc.InputGroupText("deg/ms"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Voltage_Fund_Phase", id="v-voltage-fund-phase"),
                                dbc.InputGroupText("deg"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Voltage_Fund_AC", id="v-voltage-fund-ac"),
                                dbc.InputGroupText("V"),
                            ],
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.Div("W"),
                         dbc.InputGroup(
                            [
                                dbc.Input(placeholder="F_Ramp_Output", id="w-f-ramp-output", type="number"),
                                dbc.InputGroupText("Hz/s"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="F_Output_SP", id="w-f-output-sp", type="number"),
                                dbc.InputGroupText("Hz"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="G_Output_Resistance", id="w-g-output-resist", type="number"),
                                dbc.InputGroupText("Ohm"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Voltage_Ramp_AC", id="w-voltage-ramp-ac", type="number"),
                                dbc.InputGroupText("V/ms"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Voltage_Ramp_Phase", id="w-voltage-ramp-fund"),
                                dbc.InputGroupText("deg/ms"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Voltage_Fund_Phase", id="w-voltage-fund-phase"),
                                dbc.InputGroupText("deg"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Voltage_Fund_AC", id="w-voltage-fund-ac"),
                                dbc.InputGroupText("V"),
                            ],
                            className="mb-3",
                        ),
                    ]
                ),
            ]
        ),
    ]
)

# Set current manually input
input_groups_el = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div("U"),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Current_Ramp_AC_Output", id="u-current-ramp-output"),
                                dbc.InputGroupText("A/ms"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Current_Ramp_Phase_Angle_Output", id="u-current-ramp-phase"),
                                dbc.InputGroupText("deg/ms"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Current_Fundamental_Phase_Angle", id="u-current-fund-phase"),
                                dbc.InputGroupText("deg"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Current_Fundamental_AC", id="u-current-fundamental"),
                                dbc.InputGroupText("A"),
                            ],
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.Div("V"),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Current_Ramp_AC_Output", id="v-current-ramp-output"),
                                dbc.InputGroupText("A/ms"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Current_Ramp_Phase_Angle_Output", id="v-current-ramp-phase"),
                                dbc.InputGroupText("deg/ms"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Current_Fundamental_Phase_Angle", id="v-current-fund-phase"),
                                dbc.InputGroupText("deg"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Current_Fundamental_AC", id="v-current-fundamental"),
                                dbc.InputGroupText("A"),
                            ],
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.Div("W"),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Current_Ramp_AC_Output", id="w-current-ramp-output"),
                                dbc.InputGroupText("A/ms"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Current_Ramp_Phase_Angle_Output", id="w-current-ramp-phase"),
                                dbc.InputGroupText("deg/ms"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Current_Fundamental_Phase_Angle", id="w-current-fund-phase"),
                                dbc.InputGroupText("deg"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Current_Fundamental_AC", id="w-current-fundamental"),
                                dbc.InputGroupText("A"),
                            ],
                            className="mb-3",
                        ),
                    ]
                ),
            ]
        ),
    ]
)

# Tabs for grid emulator
tab1_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("EU Grid voltage will be set as follows for all 3 phases (U, V, W), with phase angle shift of 120 degrees and activated:", className="card-text"),
            dbc.Table(table_header + table_body, bordered=True),
            dbc.Button("Set voltage", color="success", id="eu-grid-set-voltage", n_clicks=0),
            html.P(id='voltage-status'),
        ]
    ),
    className="mt-3",
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("Please select the voltage values (BE VERY CAREFUL!):", className="card-text"),
            input_groups,
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Button("Set Voltage", color="success", id="set-manual-voltage", n_clicks=0),
                            html.P(id='voltage-status-manual'),
                        ],
                    ),
                    dbc.Col(
                        [
                            dbc.Button("Populate with 230 V EU", color="info", id="set-default-voltage", n_clicks=0),
                            html.P(id='voltage-status-default'),
                        ],
                    ),
                ],
            ),
        ]
    ),
    className="mt-3",
)

tab3_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("Please select on which phases there is an appliance connected that should be sampled:", className="card-text"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.InputGroup(
                                [dbc.InputGroupText(dbc.RadioButton(id="collapse-button-u" ,label="Phase U", value=False)),],
                                className="mb-3",
                            ),
                        ],
                    ),
                    dbc.Col(
                        [
                            dbc.InputGroup(
                                [dbc.InputGroupText(dbc.RadioButton(id="collapse-button-v" ,label="Phase V", value=False)),],
                                className="mb-3",
                            ),
                        ],
                    ),
                    dbc.Col(
                        [
                            dbc.InputGroup(
                                [dbc.InputGroupText(dbc.RadioButton(id="collapse-button-w" ,label="Phase W", value=False)),],
                                className="mb-3",
                            ),
                        ],
                    ),
                ],
            ),
            dbc.Collapse(
                dbc.Card(dbc.CardBody(
                    [
                        html.P("Metadata for phase U:"),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Type"),
                                dbc.Input(placeholder="Type", id="appliance-phase-u-type"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Brand"),
                                dbc.Input(placeholder="Brand", id="appliance-phase-u-brand"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Manufacture year"),
                                dbc.Input(placeholder="Year", id="appliance-phase-u-year"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Model Number"),
                                dbc.Input(placeholder="Number", id="appliance-phase-u-model"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Voltage",),
                                dbc.Input(placeholder="Voltage", id="appliance-phase-u-voltage"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Wattage"),
                                dbc.Input(placeholder="Wattage", id="appliance-phase-u-wattage"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Notes"),
                                dbc.Input(placeholder="Notes", id="appliance-phase-u-notes"),
                            ],
                            className="mb-3",
                        ),
                    ])),
                id="collapse-u",
                is_open=False,
            ),
            dbc.Collapse(
                dbc.Card(dbc.CardBody(
                    [
                        html.P("Metadata for phase V:"),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Type"),
                                dbc.Input(placeholder="Type", id="appliance-phase-v-type"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Brand"),
                                dbc.Input(placeholder="Brand", id="appliance-phase-v-brand"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Manufacture year"),
                                dbc.Input(placeholder="Year", id="appliance-phase-v-year"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Model Number"),
                                dbc.Input(placeholder="Number", id="appliance-phase-v-model"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Voltage"),
                                dbc.Input(placeholder="Voltage", id="appliance-phase-v-voltage"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Wattage"),
                                dbc.Input(placeholder="Wattage", id="appliance-phase-v-wattage"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Notes"),
                                dbc.Input(placeholder="Notes", id="appliance-phase-v-notes"),
                            ],
                            className="mb-3",
                        ),
                    ])),
                id="collapse-v",
                is_open=False,
            ),
            dbc.Collapse(
                dbc.Card(dbc.CardBody(
                    [
                        html.P("Metadata for phase W:"),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Type"),
                                dbc.Input(placeholder="Type", id="appliance-phase-w-type"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Brand"),
                                dbc.Input(placeholder="Brand", id="appliance-phase-w-brand"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Manufacture year"),
                                dbc.Input(placeholder="Year", id="appliance-phase-w-year"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Model Number"),
                                dbc.Input(placeholder="Number", id="appliance-phase-w-model"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Voltage"),
                                dbc.Input(placeholder="Voltage", id="appliance-phase-w-voltage"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Appliance Wattage"),
                                dbc.Input(placeholder="Wattage", id="appliance-phase-w-wattage"),
                            ],
                            className="mb-3",
                        ),
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Notes"),
                                dbc.Input(placeholder="Notes", id="appliance-phase-w-notes"),
                            ],
                            className="mb-3",
                        ),
                    ])),
                id="collapse-w",
                is_open=False,
            ),
            html.P(children=''),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Overall notes for the sampling"),
                    dbc.Textarea(id="appliance-overall-notes"),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Location of the sampling"),
                    dbc.Input(placeholder="location", value="IfI, TU Clausthal", id="appliance-location"),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Sampling duration in s (min = 1 s)"),
                    dbc.Input(type="number", min=1, step=1, value=60, id="appliance-iterations"),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Spacing between samples in s (min = 0.10 s)"),
                    dbc.Input(type="number", min=0.1, step=0.01, value=0.10, id="appliance-spacing"),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Button("Calibrate", color="warning", id="button-calibrate", n_clicks=0),
                            html.P(id="calibrate-status"),
                        ],
                    ),
                    dbc.Col(
                        [
                            dbc.Button("Start sampling", color="success", id="button-start-sampling", n_clicks=0),
                        ],
                    ),
                ],
            ),
            html.P(id="sampling-status"),
            html.Div(
                [
                    dcc.Interval(id='interval1', interval=1 * 1000, n_intervals=0, disabled=True),
                    html.P(id='hidden-p-callback', children='', n_clicks=0),
                    html.P(id='div-out', children='', n_clicks=0),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Button("Download CSV", color="primary", id="button-download-csv", n_clicks=0, disabled=True),
                            dcc.Download(id="download-csv"),
                        ],
                    ),
                    dbc.Col(
                        [
                            dbc.Button("Download Metadata", color="primary", id="button-download-metadata", n_clicks=0, disabled=True),
                            dcc.Download(id="download-metadata"),
                        ],
                    ),
                ],
            ),
        ],
    ),
    className="mt-3",
)

# Tabs for electronic load
tab1_content_el = dbc.Card(
    dbc.CardBody(
        [
            html.P("Please select the current values. After clicking set current the values will be set and activated. You can also use the button to populate with -4 A. BE VERY CAREFUL!", className="card-text"),
            input_groups_el,
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Button("Set current", color="success", id="set-manual-current", n_clicks=0),
                            html.P(id='current-status-manual'),
                        ],
                    ),
                    dbc.Col(
                        [
                            dbc.Button("Populate with -4 A", color="info", id="set-default-current", n_clicks=0),
                            html.P(id='current-status-default'),
                        ],
                    ),
                ],
            ),
        ],
    ),
    className="mt-3",
)

tab2_content_el = dbc.Card(
    dbc.CardBody(
        [
            html.P("Please select current file, that will be used to simulate on the Electronic Load. If you want to upload your own files, then be sure to upload both the .csv and a .json file for the metadata, having the same name. For example: 1.csv and 1.json (BE VERY CAREFUL!):", className="card-text"),
            dcc.Upload(
                id="button-upload-csv",
                children=html.Div(
                    ["Upload CSV and Metadata (.json)"]
                ),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                },
                multiple=True,
                accept=".json, .csv",
            ),
            html.Ul(id='upload-status-csv'),
            dcc.Dropdown(
                id='fileselector', 
                options=list_of_files,
                value=list_of_files[0],
            ),
            html.P("Metadata for the selected CSV:"),
            html.Div(id="data-table-uvw"),
            html.Div(id="data-table-notes"),
            html.P("Select multiplicator (the multiplicator will be multiplied with the values of Fundamental Amps for UVW respectively):"),
            dbc.InputGroup(
                            [
                                dbc.Input(placeholder="Multiply number", id="multiply-number", type="number", min=1, step=1, value=1),
                                dbc.InputGroupText("x Fundamental Amps from CSV"),
                            ],
                            className="mb-3",
                        ),
            dbc.Button("Start emulation on EL with selected file", color="success", id="button-start-emulation", n_clicks=0),
            html.P(id="emulation-status"),
            html.Div(
                [
                    dcc.Interval(id='interval2', interval=1 * 1000, n_intervals=0, disabled=True),
                    html.P(id='hidden-p1-callback', children='', n_clicks=0),
                    html.P(id='div-out1', children='', n_clicks=0),
                ],
            ),
        ],
    ),
    className="mt-3",
)

app.layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Div(html.Img(src="assets/Logo_TUC_de_RGB.jpg", width=250)), md=1),
                dbc.Col(
                    html.Div("Grid Emulator and Electronic Load Dashboard"),
                    style={"text-align": "center",
                        "font-weight": "bold",
                        "font-size": "40px",
                        },
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(html.Div(
                    [
                        html.Div("Grid Emulator:", style={"font-weight": "bold"}),
                        dbc.ButtonGroup(
                            [
                                dbc.Button("STOP", color="danger", id='stop-grid-emulator', n_clicks=0, disabled=True),
                                dbc.Button("START", color="success", id='start-grid-emulator', n_clicks=0, disabled=False),
                            ],
                        ),
                    ],
                )),
                dbc.Col(html.Div(
                    [
                        html.Div("Grid Emulator status:", style={"font-weight": "bold"}),
                        html.H3(dbc.Badge("Off", color="danger", className="me-1", id='status-grid-badge')),
                    ],
                )),
                dbc.Col(html.Div(
                    [
                        html.Div("Electronic Load:", style={"font-weight": "bold"}),
                        dbc.ButtonGroup(
                            [
                                dbc.Button("STOP", color="danger", id='stop-electronic-load', n_clicks=0),
                                dbc.Button("START", color="success", id='start-electronic-load', n_clicks=0),
                            ],
                        ),
                    ],
                )),
                dbc.Col(html.Div(
                    [
                        html.Div("Electronic Load status:", style={"font-weight": "bold"}),
                        html.H3(dbc.Badge("Off", color="danger", className="me-1", id='status-load-badge')),
                    ],
                )),
            ],
            style={"margin-top": "3em", "margin-left": "1em"},
        ),
        dbc.Row(
            [
                dbc.Col(html.Div(
                    [
                        dbc.Tabs(
                            [
                                dbc.Tab(tab1_content, label="Set EU Grid voltage"),
                                dbc.Tab(tab2_content, label="Set voltage manually"),
                                dbc.Tab(tab3_content, label="Sampling"),
                            ],
                        ),
                    ]
                )),
                dbc.Col(html.Div(
                    [
                        dbc.Tabs(
                            [
                                dbc.Tab(tab1_content_el, label="Set manual current"),
                                dbc.Tab(tab2_content_el, label="Set automatic current from file"),
                            ],
                        ),
                    ]
                )),
            ],
            style={"margin-top": "1em", "margin-left": "1em"},
        ),
        dbc.Row(
            [
                html.P("Prototype by Gabriel Gachev | 2023")
            ],
            style={"textAlign": "center",
                   "margin-top": "3em"},
        ),
    ],
    style={"margin-right": "1em"}
)

# Callback for file selection electronic load
@app.callback([Output("data-table-uvw", "children"),
               Output("data-table-notes", "children"),],
              Input("fileselector", "value"))
def update_fileselection(selected_dropdown_value):
    # Global Timer value used for countdown in the emulation
    global time_rem1

    # Extracting file number from the input
    file_number = selected_dropdown_value.split(".", 1)[0]
    path_selected_csv = Path(UPLOAD_FOLDER_ROOT + selected_dropdown_value)
    path_selected_json = Path(UPLOAD_FOLDER_ROOT + file_number + ".json")

    # Reading the json file and creating dictionarys with the values
    f = open(path_selected_json)
    dict_json = json.load(f)
    f.close()
    
    dict_phase_u = dict_json["meta"]["appliance_phase_U"]
    dict_phase_v = dict_json["meta"]["appliance_phase_V"]
    dict_phase_w = dict_json["meta"]["appliance_phase_W"]
    dict_overall_notes = dict_json["meta"]["header"]

    # Calculation of the time remaining for time_rem1
    spacing = 1 / dict_overall_notes["sampling_frequency_Hz"]
    # Round spacing because of floatpoint arithmentic accuracy
    spacing = round(spacing, 2)
    iterations = dict_overall_notes["number_samples"]
    time_rem1 = iterations * spacing

    # Creating pandas dataframes to return to the table
    # Frame for UVW
    json_dataframe = pandas.DataFrame([{"Values": values, "U": u} for values, u in dict_phase_u.items()])
    json_dataframe["V"] = pandas.DataFrame([{u} for values, u in dict_phase_v.items()])
    json_dataframe["W"] = pandas.DataFrame([{u} for values, u in dict_phase_w.items()])

    # Frame for ovarall metadata
    json_dataframe_overall = pandas.DataFrame([{"Header": values, "Values": u} for values, u in dict_overall_notes.items()])

    return (dbc.Table.from_dataframe(json_dataframe, striped=True, bordered=True, hover=True)), (dbc.Table.from_dataframe(json_dataframe_overall, striped=True, bordered=True, hover=True))

# Upload Files functions als callbacks
def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_FOLDER_ROOT, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_FOLDER_ROOT):
        path = os.path.join(UPLOAD_FOLDER_ROOT, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)


@app.callback(
    Output("upload-status-csv", "children"),
    [Input("button-upload-csv", "filename"), Input("button-upload-csv", "contents")],
)
def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""
    files = []
    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            files.append(name)
            save_file(name, data)
        return (str(files) + " uploaded!")
    else:
        return ""

# Set default current with -4 A
@app.callback(
    [Output("current-status-default", "children"),
     Output("set-default-current", "children"),
     Output("u-current-ramp-output", "value"),
     Output("u-current-ramp-phase", "value"),
     Output("u-current-fund-phase", "value"),
     Output("u-current-fundamental", "value"),
     Output("v-current-ramp-output", "value"),
     Output("v-current-ramp-phase", "value"),
     Output("v-current-fund-phase", "value"),
     Output("v-current-fundamental", "value"),
     Output("w-current-ramp-output", "value"),
     Output("w-current-ramp-phase", "value"),
     Output("w-current-fund-phase", "value"),
     Output("w-current-fundamental", "value")],
    Input("set-default-current", "n_clicks"),
    prevent_initial_call=True,)
def func(n_clicks):
    if n_clicks % 2 == 0:
        return "Default current populated with 0 A!", "Populate with -4 A", 10.0, 1, 0, 0, 10.0, 1, 0, 0, 10.0, 1, 0, 0
    return "Default current populated with -4 A!", "Populate with 0 A", 10.0, 1, 0, -4, 10.0, 1, 0, -4, 10.0, 1, 0, -4

# Set default voltage with 230 V
@app.callback(
    [Output("voltage-status-default", "children"),
     Output("set-default-voltage", "children"),
     Output("u-f-ramp-output", "value"),
     Output("u-f-output-sp", "value"),
     Output("u-g-output-resist", "value"),
     Output("u-voltage-ramp-ac", "value"),
     Output("u-voltage-ramp-fund", "value"),
     Output("u-voltage-fund-phase", "value"),
     Output("u-voltage-fund-ac", "value"),
     Output("v-f-ramp-output", "value"),
     Output("v-f-output-sp", "value"),
     Output("v-g-output-resist", "value"),
     Output("v-voltage-ramp-ac", "value"),
     Output("v-voltage-ramp-fund", "value"),
     Output("v-voltage-fund-phase", "value"),
     Output("v-voltage-fund-ac", "value"),
     Output("w-f-ramp-output", "value"),
     Output("w-f-output-sp", "value"),
     Output("w-g-output-resist", "value"),
     Output("w-voltage-ramp-ac", "value"),
     Output("w-voltage-ramp-fund", "value"),
     Output("w-voltage-fund-phase", "value"),
     Output("w-voltage-fund-ac", "value")],
    Input("set-default-voltage", "n_clicks"),
    prevent_initial_call=True,)
def func(n_clicks):
    if n_clicks % 2 == 0:
        return "Populated with 0 V!", "Populate with 230 V EU", 1, 50, 0, 100, 10, 0, 0, 1, 50, 0, 100, 10, -120, 0, 1, 50, 0, 100, 10, -240, 0
    else:
        return "Default voltage 230V EU populated!", "Populate with 0 V", 1, 50, 0, 100, 10, 0, 230, 1, 50, 0, 100, 10, -120, 230, 1, 50, 0, 100, 10, -240, 230

# Download CSV Callback
@app.callback(
    Output("download-csv", "data"),
    Input("button-download-csv", "n_clicks"),
    prevent_initial_call=True,)
def func(n_clicks):
    return dcc.send_file(
        filepath_csv
    )

# Download Metadata Callback
@app.callback(
    Output("download-metadata", "data"),
    Input("button-download-metadata", "n_clicks"),
    prevent_initial_call=True,)
def func(n_clicks):
    return dcc.send_file(
        filepath_json
    )

# Console output at sampling
@app.callback([Output("div-out", "children"),
                Output("interval1", "disabled"),
                Output("hidden-p-callback", "n_clicks"),
                Output("button-download-csv", "disabled"),
                Output("button-download-metadata", "disabled")],
            [Input("interval1", "n_intervals"),
             Input("hidden-p-callback", "children")])
def update_interval(n, children):
    # Global timer value that will be counted backwards to show how long will the sampling take
    global time_rem
    if time_rem > 0:
        time_rem -= 1
        if time_rem > 0:
            return ("Time remaining: " + str(int(time_rem)) + " s"), False, 0, True, True
        else:
            update_files_list()
            return "Sampling Done!", True, 1, False, False
    else:
        return "", True, 0, True, True
    
# Callback to save the datafile
@app.callback([Output("div-out", "n_clicks"),
               Output("fileselector", "options")],
            [Input("hidden-p-callback", "n_clicks")])
def update_interval(n):
    if n > 0:
        global filepath_csv
        #Save the data to the CSV
        cinergiamodbus.save_dataframe_to_csv(filepath_csv)
        # Updating the file list on the file selector to have the new one added
        update_files_list()
        print("Datafile saved!")
    return (0, list_of_files)

# Set EU grid voltage for grid emulator
@app.callback(
    Output("voltage-status", "children"),
    [Input("eu-grid-set-voltage", "n_clicks")],
)
def show_voltage_status(n_clicks):
    if n_clicks > 0:
        # Set EU voltage and activate the config
        cinergiamodbus.set_voltage(1, [], [], [])
        cinergiamodbus.grid_emulator_activate_config()
        return "Voltage setted!"
    else:
        return ""
    
# Set manual voltage for grid emulator
@app.callback(
    Output("voltage-status-manual", "children"),
    [Input("set-manual-voltage", "n_clicks")],
    [State("u-f-ramp-output", "value"),
     State("u-f-output-sp", "value"),
     State("u-g-output-resist", "value"),
     State("u-voltage-ramp-ac", "value"),
     State("u-voltage-ramp-fund", "value"),
     State("u-voltage-fund-phase", "value"),
     State("u-voltage-fund-ac", "value"),
     State("v-f-ramp-output", "value"),
     State("v-f-output-sp", "value"),
     State("v-g-output-resist", "value"),
     State("v-voltage-ramp-ac", "value"),
     State("v-voltage-ramp-fund", "value"),
     State("v-voltage-fund-phase", "value"),
     State("v-voltage-fund-ac", "value"),
     State("w-f-ramp-output", "value"),
     State("w-f-output-sp", "value"),
     State("w-g-output-resist", "value"),
     State("w-voltage-ramp-ac", "value"),
     State("w-voltage-ramp-fund", "value"),
     State("w-voltage-fund-phase", "value"),
     State("w-voltage-fund-ac", "value"),
     ]
)
def show_voltage_status(n_clicks, u_value1, u_value2, u_value3, u_value4, u_value5, u_value6, u_value7, v_value1, v_value2, v_value3, v_value4, v_value5, v_value6, v_value7, w_value1, w_value2, w_value3, w_value4, w_value5, w_value6, w_value7):
    if n_clicks > 0:
        # Check if all of the values are setted
        list_of_values = u_value1, u_value2, u_value3, u_value4, u_value5, u_value6, u_value7, v_value1, v_value2, v_value3, v_value4, v_value5, v_value6, v_value7, w_value1, w_value2, w_value3, w_value4, w_value5, w_value6, w_value7
        for value in list_of_values:
            if value is None or value == '':
                return "Error, please check the inputs!"

        voltages_list_u = [int(u_value1), int(u_value2), int(u_value3), int(u_value4), int(u_value5), int(u_value6), int(u_value7)]
        print(voltages_list_u)
        voltages_list_v = [int(v_value1), int(v_value2), int(v_value3), int(v_value4), int(v_value5), int(v_value6), int(v_value7)]
        print(voltages_list_v)
        voltages_list_w = [int(w_value1), int(w_value2), int(w_value3), int(w_value4), int(w_value5), int(w_value6), int(w_value7)]
        print(voltages_list_w)
            
        # Add function to set manual voltage values and activate config
        cinergiamodbus.set_voltage(0, voltages_list_u, voltages_list_v, voltages_list_w)
        cinergiamodbus.grid_emulator_activate_config()
        return ("Voltage setted! " + "U: " + str(voltages_list_u) + " V: " + str(voltages_list_v) + "W: " + str(voltages_list_w))
    else:
        return ""

# Set manual current for grid emulator
@app.callback(
    Output("current-status-manual", "children"),
    [Input("set-manual-current", "n_clicks")],
    [State("u-current-ramp-output", "value"),
     State("u-current-ramp-phase", "value"),
     State("u-current-fund-phase", "value"),
     State("u-current-fundamental", "value"),
     State("v-current-ramp-output", "value"),
     State("v-current-ramp-phase", "value"),
     State("v-current-fund-phase", "value"),
     State("v-current-fundamental", "value"),
     State("w-current-ramp-output", "value"),
     State("w-current-ramp-phase", "value"),
     State("w-current-fund-phase", "value"),
     State("w-current-fundamental", "value")]
)
def show_voltage_status(n_clicks, u_value1, u_value2, u_value3, u_value4, v_value1, v_value2, v_value3, v_value4, w_value1, w_value2, w_value3, w_value4):
    if n_clicks > 0:
        if (u_value1 and u_value2 and u_value3 and u_value4 ) is not None:
            current_list_u = [int(u_value1), int(u_value2), int(u_value3), int(u_value4)]
        else:
            return "Error, please check the inputs!"
        
        if (v_value1 and v_value2 and v_value3 and v_value4) is not None:
            current_list_v = [int(v_value1), int(v_value2), int(v_value3), int(v_value4)]
        else:
            return "Error, please check the inputs!"
        
        if (w_value1 and w_value2 and w_value3 and w_value4) is not None:
            current_list_w = [int(w_value1), int(w_value2), int(w_value3), int(w_value4)]
        else:
            return "Error, please check the inputs!"

        # Set manual current values and activate config
        cinergiamodbus.set_current(current_list_u, current_list_v, current_list_w)
        cinergiamodbus.electronic_load_activate_config()

        return ("Current setted! " + "U: " + str(current_list_u) + " V: " + str(current_list_v) + "W: " + str(current_list_w))
    else:
        return ""

# Function for testing
def print_hello():
  print("Hello")

# Function for getting the files in a directory
def get_files(path):
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)):
                yield file

#Calibrate grid emulator
@app.callback(
        Output("calibrate-status", "children"),
        Input("button-calibrate", "n_clicks"),
)
def calibrate_ge(n_clicks):
    if n_clicks > 0:
        list_calibration = cinergiamodbus.grid_emulator_calibrate()
        return "Calibration offset: " + str(list_calibration)
    else:
        return ""

# Start sampling from grid emulator
@app.callback(
    [Output("sampling-status", "children"),
    Output("hidden-p-callback", "children")],
    [Input("button-start-sampling", "n_clicks"),],
    [State("collapse-button-u", "value"),
     State("collapse-button-v", "value"),
     State("collapse-button-w", "value"),
     State("appliance-phase-u-type", "value"),
     State("appliance-phase-u-brand", "value"),
     State("appliance-phase-u-year", "value"),
     State("appliance-phase-u-model", "value"),
     State("appliance-phase-u-voltage", "value"),
     State("appliance-phase-u-wattage", "value"),
     State("appliance-phase-u-notes", "value"),
     State("appliance-phase-v-type", "value"),
     State("appliance-phase-v-brand", "value"),
     State("appliance-phase-v-year", "value"),
     State("appliance-phase-v-model", "value"),
     State("appliance-phase-v-voltage", "value"),
     State("appliance-phase-v-wattage", "value"),
     State("appliance-phase-v-notes", "value"),
     State("appliance-phase-w-type", "value"),
     State("appliance-phase-w-brand", "value"),
     State("appliance-phase-w-year", "value"),
     State("appliance-phase-w-model", "value"),
     State("appliance-phase-w-voltage", "value"),
     State("appliance-phase-w-wattage", "value"),
     State("appliance-phase-w-notes", "value"),
     State("appliance-overall-notes", "value"),
     State("appliance-location", "value"),
     State("appliance-iterations", "value"),
     State("appliance-spacing", "value")]
)
def start_sampling(n_clicks, value_phase_u, value_phase_v, value_phase_w, phase_u_type, phase_u_brand, phase_u_year, phase_u_model, phase_u_voltage, phase_u_wattage, phase_u_notes, phase_v_type, phase_v_brand, phase_v_year, phase_v_model, phase_v_voltage, phase_v_wattage, phase_v_notes, phase_w_type, phase_w_brand, phase_w_year, phase_w_model, phase_w_voltage, phase_w_wattage, phase_w_notes, overall_notes, location, iterations_new, spacing_new):
    if n_clicks > 0:
        global spacing
        global iterations
        global time_rem
        global filepath_csv
        global filepath_json

        iterations = iterations_new / spacing_new
        spacing = spacing_new
        time_rem = iterations * spacing + 1

        metadata_u = ["", "", "", "", "", "", ""]
        metadata_v = ["", "", "", "", "", "", ""]
        metadata_w = ["", "", "", "", "", "", ""]

        # Check if phase u is selected
        if value_phase_u:
            metadata_u = [phase_u_type, phase_u_brand, phase_u_year, phase_u_model, phase_u_voltage, phase_u_wattage, phase_u_notes]
            i = 0
            for value in metadata_u:
                if value is None:
                    metadata_u[i] = ""
                i += 1
        
        # Check if phase v is selected
        if value_phase_v:
            metadata_v = [phase_v_type, phase_v_brand, phase_v_year, phase_v_model, phase_v_voltage, phase_v_wattage, phase_v_notes]
            i = 0
            for value in metadata_v:
                if value is None:
                    metadata_v[i] = ""
                i += 1
        
        # Check if phase w is selected
        if value_phase_w:
            metadata_w = [phase_w_type, phase_w_brand, phase_w_year, phase_w_model, phase_w_voltage, phase_w_wattage, phase_w_notes]
            i = 0
            for value in metadata_w:
                if value is None:
                    metadata_w[i] = ""
                i += 1
        
        # Read ambient temperature
        appliance_ambient_temperature = cinergiamodbus.read_grid_emulator_temp()
        # appliance_ambient_temperature = 23

        #Check the files in the directory to know the new file number
        number_of_file = 0
        list_of_files = []
        for file in get_files(UPLOAD_FOLDER_ROOT):
            if 'csv' in file:
                number_of_file += 1
                list_of_files.append(file)

        print(list_of_files)
        print("Number of files in the directory: ", number_of_file)

        update_files_list()

        #Increment to have the actual file number
        number_of_file += 1

        #Create the new CSV and JSON filepath
        filepath_csv = Path(UPLOAD_FOLDER_ROOT + str(number_of_file) + '.csv')
        filepath_json = Path(UPLOAD_FOLDER_ROOT + str(number_of_file) + '.json')

        #Check for null values
        if overall_notes is None:
            overall_notes = ""
        if location is None:
            location = ""

        #Threading to read the values
        timesched = RepeatedTimer(spacing, iterations, cinergiamodbus.read_all_outputs, value_phase_u, value_phase_v, value_phase_w)
        # timesched = RepeatedTimer(spacing, iterations, cinergiamodbus.test_func, value_phase_u, value_phase_v, value_phase_w)
        timesched.start()

        # Save the metadata
        metadata.save_to_json(number_of_file, metadata_u, metadata_v, metadata_w, overall_notes, iterations, spacing, appliance_ambient_temperature, location)

        return ("Sampling started! " + "File number: " + str(number_of_file) + ". Please wait the sampling to complete!"), " "
    else:
        return "", ""

# Toggle collapse for sampling U
@app.callback(
    Output("collapse-u", "is_open"),
    [Input("collapse-button-u", "value")],
)
def toggle_collapse(value):
    if value:
         return True
    else:
         return False
    
# Toggle collapse for sampling V
@app.callback(
    Output("collapse-v", "is_open"),
    [Input("collapse-button-v", "value")],
)
def toggle_collapse(value):
    if value:
         return True
    else:
         return False
    
# Toggle collapse for sampling W
@app.callback(
    Output("collapse-w", "is_open"),
    [Input("collapse-button-w", "value")],
)
def toggle_collapse(value):
    if value:
         return True
    else:
         return False

# Start Electronic Load Emulation of the selected file
@app.callback(
    Output("hidden-p1-callback", "hidden"),
    [Input("hidden-p1-callback", "children")],
    [State("fileselector", "value"),
     State("multiply-number", "value")],
    prevent_initial_call = True
)
def start_emulation(n_clicks, selected_dropdown_value, multiplicator):
    global time_rem1
    current_dict = {"U": "",
                    "V": "",
                    "W": ""}
    file_number = selected_dropdown_value.split(".", 1)[0]
    path_selected_csv = Path(UPLOAD_FOLDER_ROOT + selected_dropdown_value)
    path_selected_json = Path(UPLOAD_FOLDER_ROOT + file_number + ".json")

    # Read current, iteratons and spacing between them from file for uvw
    metadata_dict = metadata.read_metadata(path_selected_json)
    sampling_data = pandas.read_csv(path_selected_csv)

    spacing = 1 / metadata_dict["meta"]["header"]["sampling_frequency_Hz"]
    # Round spacing because of floatpoint arithmentic accuracy
    spacing = round(spacing, 2)
    iterations = metadata_dict["meta"]["header"]["number_samples"]
    time_rem1 = iterations * spacing

    # Save the currents from the dataframe in a dictionary with 3 lists
    current_dict["U"] = sampling_data["Current_Output_U_RMS"]
    current_dict["V"] = sampling_data["Current_Output_V_RMS"]
    current_dict["W"] = sampling_data["Current_Output_W_RMS"]

    # Send the data to the electronic load
    old_u = 0
    old_v = 0
    old_w = 0
    value_changed = True
    for i in range(0, iterations):
        # Round on the 3rd decimal
        new_u = round(current_dict["U"][i], 3)
        new_v = round(current_dict["V"][i], 3)
        new_w = round(current_dict["W"][i], 3)

        # Check if there is a change
        if old_u != new_u:
            old_u = new_u
            value_changed = True
        if old_v != new_v:
            old_v = new_v
            value_changed = True
        if old_w != new_w:
            old_w = new_w
            value_changed = True

        # If there is a change set it for all phases "simultaneously"
        if value_changed:            
            current_list_u = [10, 1, 0, -round(new_u * multiplicator, 3)]
            current_list_v = [10, 1, 0, -round(new_v * multiplicator, 3)]
            current_list_w = [10, 1, 0, -round(new_w * multiplicator, 3)]
            print(i, current_list_u, current_list_v, current_list_w, spacing)
            cinergiamodbus.set_current(current_list_u, current_list_v, current_list_w)
            cinergiamodbus.electronic_load_activate_config()
        value_changed = False
        time.sleep(spacing)
    # Turn the load after the emulation back to 0
    cinergiamodbus.set_current([10, 1, 0, 0], [10, 1, 0, 0], [10, 1, 0, 0])
    cinergiamodbus.electronic_load_activate_config()

# Hidden emulation done callback
@app.callback(
    [Output("emulation-status", "children"),
     Output("hidden-p1-callback", "n_clicks"),
     Output("hidden-p1-callback", "children")],
    [Input("button-start-emulation", "n_clicks"),],
    prevent_initial_call = True
)
def toggle_collapse(n_clicks):
    return "Emulation started!", 1, " "

# Console output at emulation
@app.callback([Output("div-out1", "children"),
                Output("interval2", "disabled")],
            [Input("interval2", "n_intervals"),
             Input("hidden-p1-callback", "n_clicks")],
             prevent_initial_call = True
)
def update_interval(n, children):
    global time_rem1
    if time_rem1 > 0:
        time_rem1 -= 1
        if time_rem1 > 0:
            return ("Time remaining: " + str(int(time_rem1)) + " s"), False
        else:
            return "Emulation Done!", True
    else:
        return "", True

# Callback to STOP and START the Grid Emulator button
@app.callback([Output('stop-grid-emulator','disabled'),
                Output('start-grid-emulator', 'disabled'),
                Output('status-grid-badge', 'children'),
                Output('status-grid-badge', 'color')],
            [Input('stop-grid-emulator','n_clicks'),
             Input('start-grid-emulator', 'n_clicks')])
def stop_grid_emulator(n_clicks1, n_clicks2):
        n_clicks = n_clicks1 + n_clicks2
        if n_clicks % 2 == 1 and n_clicks != 0:
            # Call function to start the grid emulator
            cinergiamodbus.start_grid_emulator()
            return False, True, "Run", "success"
        else:
            # Call function to stop the grind emulator
            if n_clicks > 0:
                cinergiamodbus.set_voltage(0, [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0])
                cinergiamodbus.grid_emulator_activate_config
                cinergiamodbus.stop_grid_emulator()
            return True, False, "Off", "danger"

# Callback to STOP and START the Electronic Load button
@app.callback([Output('stop-electronic-load','disabled'),
                Output('start-electronic-load', 'disabled'),
                Output('status-load-badge', 'children'),
                Output('status-load-badge', 'color')],
            [Input('stop-electronic-load','n_clicks'),
             Input('start-electronic-load', 'n_clicks')])
def stop_electronic_load(n_clicks1, n_clicks2):
        n_clicks = n_clicks1 + n_clicks2
        if n_clicks % 2 == 1 and n_clicks != 0:
            # Call function to start the electronic load
            cinergiamodbus.start_electronic_load()
            return False, True, "Run", "success"
        else:
            # Call function to stop the electronic load
            if n_clicks > 0:
                cinergiamodbus.set_current([10, 1, 0, 0], [10, 1, 0, 0], [10, 1, 0, 0])
                cinergiamodbus.electronic_load_activate_config()
                cinergiamodbus.stop_electronic_load()
            return True, False, "Off", "danger"

app.run_server(debug=True, host="0.0.0.0", port="8050")