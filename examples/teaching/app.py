import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import nibabel as nib
import numpy as np
from glob import glob
from collections import OrderedDict
import os.path as op
import json
import sys

sys.path.append('..')  # to enable loading from utils
from utils import (load_data, index_by_slice, standardize,
                   read_design_file, calculate_statistics)

# csrf_protect = False because otherwise gunicorn doesn't
# serve the app properly
app = dash.Dash(csrf_protect=False)
server = app.server

# Load config (with mappings)
with open('teaching/config.json') as config:    
    cfg = json.load(config, object_pairs_hook=OrderedDict)

# Get the first key (random) from mappings, and load contrast/func
global_contrast_name = list(cfg['mappings'].keys())[0]
global_func, global_contrast = load_data(global_contrast_name, load_func=True)
global_design = read_design_file(global_contrast_name)

# Kind of an hack: save on disk which contrast we've loaded
# (to avoid reloading the func-data every callback)
with open("current_contrast.txt", "w") as text_file:
    text_file.write(global_contrast_name)

# timeseries or subjects?
grouplevel = global_func.shape[:3] == (91, 109, 91)

# Use the mean as background
if grouplevel:
    global_bg = nib.load(op.join('..', 'standard.nii.gz')).get_data()
else:
    global_bg = global_func.mean(axis=-1)

if cfg['standardize']:
    global_func = standardize(global_func)
    
colors = {
    'background': '#000000',
    'text': '#D3D3D3'
}

# Start layout of app
app.layout = html.Div(
    
    children=[

        html.Div(className='ten columns offset-by-one', children=[

            html.H1(children='VoxelViz: An interactive viewer for BOLD-fMRI data',
                    style={'textAlign': 'center', 'color': colors['text']},
                    id='title'),

            html.Div(className='row' ,children=[
                
                dcc.Markdown("""Developed for the [TransIP](https://www.transip.nl/) VPS-competition""")
            ], style={'textAlign': 'center', 'color': colors['text'], 'padding-bottom': '20px'})

        ]),

        html.Div(className='five columns', children=[

            html.Div(className='row', children=[

                html.Div(className='five columns', children=[
                    
                    dcc.Dropdown(options=[
                                    {'value': key, 'label': val} for key, val in cfg['mappings'].items()
                                 ],
                                 value=global_contrast_name,
                                 id='contrast')
                ]),
                
                html.Div(className='three columns', children=[
                    
                    dcc.RadioItems(
                        id='direction',
                        options=[
                            {'label': 'X', 'value': 'X'},
                            {'label': 'Y', 'value': 'Y'},
                            {'label': 'Z', 'value': 'Z'}
                        ],
                        labelStyle={'display': 'inline-block'},
                        value='X')
                ], style={'color': colors['text'], 'padding-top': '5px'}),
                
                html.Div(className='four columns', children=[

                    dcc.Slider(
                        min=0,
                        step=1,
                        value=50 if grouplevel else 30,
                        id='slice'),

                ], style={'padding-top': '5px'}),

            ], style={'padding-bottom': '20px'}),

            html.Div(className='row', children=[

                dcc.Graph(id='brainplot', animate=False, config={'displayModeBar': False})

            ]),

            html.Div(className='row', children=[

                html.Div(className='two columns', children=[

                    html.P('Threshold:')
                ], style={'textAlign': 'center', 'color': colors['text']}),

                html.Div(className='ten columns', children=[

                    dcc.Slider(id='threshold',
                               min=0,
                               max=10,
                            step=0.1,
                            value=2.3,
                            marks={i: i for i in np.arange(0, 10.5, 0.5)})
                ], style={'padding-top': '5px'})
            ]),
        ]),

        html.Div(className='six columns', children=[

            html.Div(className='row', children=[

                html.Div(className='twelve columns', children=[
                    dcc.Checklist(
                        options=[
                                {'label': 'Voxel', 'value': 'voxel'},
                                {'label': 'Model', 'value': 'model'}
                                ],
                        values=['voxel'], id='voxel_disp')#, labelStyle={'display': 'inline-block'})
                ], style={'padding-left': '550px'})
                    
            ]),
            
            html.Div(className='row', children=[

                dcc.Graph(id='brainplot_time', animate=False)
            ]),

            html.Div(className='row', children=[

                html.Div(className='ten columns', children=[

                    html.P(id='parameter_value')
                ], style={'textAlign': 'center', 'color': colors['text'], 'padding-top': '5px', 'font-size': '120%'})
            ]),

        ])
    ]
)


@app.callback(
    Output(component_id='parameter_value', component_property='children'),
    [Input(component_id='brainplot_time', component_property='figure'),
     Input(component_id='voxel_disp', component_property='values')])
def update_parameter_statistics(figure, voxel_disp):

    if 'model' in voxel_disp and len(figure['data']) > 1: 
        y = np.array(figure['data'][0]['y'])
        y_hat = np.array(figure['data'][1]['y'])
        stat_txt = calculate_statistics(y, y_hat, grouplevel)
        
    return stat_txt

@app.callback(
    Output(component_id='slice', component_property='max'),
    [Input(component_id='direction', component_property='value')])
def update_slice_slider(direction):

    # To fix!
    srange = {'X': global_contrast.shape[0],
              'Y': global_contrast.shape[1],
              'Z': global_contrast.shape[2]}

    return srange[direction]

@app.callback(
    Output(component_id='brainplot', component_property='figure'),
    [Input(component_id='threshold', component_property='value'),
     Input(component_id='contrast', component_property='value'),
     Input(component_id='direction', component_property='value'),
     Input(component_id='slice', component_property='value')])
def update_brainplot(threshold, contrast, direction, sslice):
    
    with open("current_contrast.txt", "r") as text_file:
        current_contrast = text_file.readlines()[0]

    if contrast != current_contrast:
        global global_contrast, global_bg, global_func
        if global_contrast.shape == (91, 109, 91):
            global_contrast = load_data(contrast, load_func=False)
        else:
            global_func, global_contrast = load_data(contrast, load_func=True)
            global_bg = global_func.mean(axis=-1)

        with open("current_contrast.txt", "w") as text_file:
            text_file.write(contrast)
    
    bg_slice = index_by_slice(direction, sslice, global_bg)
    img_slice = index_by_slice(direction, sslice, global_contrast)

    bg_map = go.Heatmap(z=bg_slice.T, colorscale='Greys', showscale=False, hoverinfo="none", name='background')
    tmp = np.ma.masked_where(np.abs(img_slice) < threshold, img_slice)
    func_map = go.Heatmap(z=tmp.T, opacity=1, name='Activity map',
                          colorbar={'thickness': 20, 'title': 'Z-val', 'x': -.1})

    layout = go.Layout(autosize=True,
                       margin={'t': 50, 'l': 5, 'r': 5},
                       plot_bgcolor=colors['background'],
                       paper_bgcolor=colors['background'],
                       font={'color': colors['text']},
                       title='Activation pattern: %s' % cfg['mappings'][contrast],
                       xaxis=dict(autorange=True,
                                  showgrid=False,
                                  zeroline=False,
                                  showline=False,
                                  autotick=True,
                                  ticks='',
                                  showticklabels=False),
                       yaxis=dict(autorange=True,
                                  showgrid=False,
                                  zeroline=False,
                                  showline=False,
                                  autotick=True,
                                  ticks='',
                                  showticklabels=False))

    return {'data': [bg_map, func_map], 'layout': layout}

@app.callback(
    Output(component_id='brainplot_time', component_property='figure'),
    [Input(component_id='threshold', component_property='value'),
     Input(component_id='contrast', component_property='value'),
     Input(component_id='direction', component_property='value'),
     Input(component_id='slice', component_property='value'),
     Input(component_id='brainplot', component_property='hoverData'),
     Input(component_id='voxel_disp', component_property='values')])
def update_brainplot_time(threshold, contrast, direction, sslice, hoverData, voxel_disp):

    layout = go.Layout(autosize=True,
                       margin={'t': 50, 'l': 50, 'r': 5},
                       plot_bgcolor=colors['background'],
                       paper_bgcolor=colors['background'],
                       font={'color': colors['text']},
                       xaxis=dict(#autorange=False,
                                  showgrid=True,
                                  zeroline=True,
                                  showline=True,
                                  autotick=True,
                                  #ticks='',
                                  showticklabels=True,
                                  title='Time'),
                       yaxis=dict(autorange=True,
                                  showgrid=True,
                                  zeroline=True,
                                  showline=True,
                                  autotick=True,
                                  #ticks='',
                                  showticklabels=True,
                                  title='Activation (contrast estimate)'))
                                  #range=[-4, 4]))
    
    with open("current_contrast.txt", "r") as text_file:
        current_contrast = text_file.readlines()[0]

    if contrast != current_contrast:
        global global_contrast, global_func, global_design
        global_func, global_contrast = load_data(contrast, load_func=True)
        global_design = read_design_file(contrast)
        if cfg['standardize']:
            global_func = standardize(global_func)

        with open("current_contrast.txt", "w") as text_file:
            text_file.write(contrast)
    
    layout.title = 'Activation across subjects' if grouplevel else 'Activation across time'
    layout.xaxis['title'] = 'Subjects' if grouplevel else 'Time'

    if hoverData is None:
        if grouplevel:
            x, y = 40, 40
        else:
            x, y = 20, 20
    else:
        x = hoverData['points'][0]['x']
        y = hoverData['points'][0]['y']
    
    img = index_by_slice(direction, sslice, global_func)
    signal = img[x, y, :].ravel()
    if np.all(np.isnan(signal)):
        signal = np.zeros(signal.size)
    
    if grouplevel:
        bcolors = ['rgb(225,20,20)' if sig > 0 else 'rgb(35,53,216)' for sig in signal]
        data = go.Bar(x=np.arange(1, global_func.shape[-1] + 1), y=signal, name='Activity',
                      marker=dict(color=bcolors,
                                  line=dict(color='rgb(211,211,211)', width=0.2)))
    else:
        data = go.Scatter(x=np.arange(global_func.shape[-1]), y=signal, name='Activity')
    
    if 'model' in voxel_disp and not np.all(signal == 0):
        betas = np.linalg.lstsq(global_design, signal)[0]
        signal_hat = betas.dot(global_design.T)
        fitted_model = go.Scatter(x=np.arange(1, global_func.shape[-1] + 1), y=signal_hat,
                                  name='Model fit')
        return {'data': [data, fitted_model], 'layout': layout}
    else:
        return {'data': [data], 'layout': layout}
external_css = ["https://codepen.io/lukassnoek/pen/Kvzmzv.css"]

for css in external_css:
    app.css.append_css({"external_url": css})


if __name__ == '__main__':
    app.run_server(ssl_context='adhoc')
