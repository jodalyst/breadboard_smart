from collections import OrderedDict

#from bokeh.sampledata import us_counties, unemployment
from bokeh.plotting import figure, show, output_file, ColumnDataSource
from bokeh.models import HoverTool
import bokeh
import random

import math

import sys
import glob
import serial
import json
import struct
import time

def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in list(range(256))]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            #print("checking port "+port)
            s = serial.Serial(port)
            #print("closing port "+port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
#-------------------

ports = serial_ports() #generate list of currently connected serial ports 
print (ports)

ser = ports[0]

s = serial.Serial(ser)
print(s)

left_nodes = 30
right_nodes = 30
left_bus = 2
right_bus = 2
node_v_spacing = 0.18
bus_h_spacing = 0.18
midline_gap = 0.25
node_to_bus_gap = 0.15



node_length = 1.0
node_height = 0.15
bus_height = node_v_spacing*left_nodes
bb_node = [[0,0,node_length,node_length],[0,node_height,node_height,0]]
bb_bus = [[0,0,node_height,node_height],[0,bus_height,bus_height,0]]

image_height = 0.3+bus_height
image_width = 0.3+midline_gap + 2*node_length+2*node_to_bus_gap+4*node_height

BB_x = []
BB_y = []

orientation='horizontal'

if orientation =='vertical':
    for q in range(left_nodes):
        BB_x.append([t for t in bb_node[0]])
        BB_y.append([t+q*node_v_spacing for t in bb_node[1]])
    for q in range(right_nodes):
        BB_x.append([t+node_length+midline_gap for t in bb_node[0]])
        BB_y.append([t+q*node_v_spacing for t in bb_node[1]])
    
    BB_x.append([t-node_to_bus_gap-node_height - bus_h_spacing for t in bb_bus[0]])
    BB_x.append([t-node_to_bus_gap-node_height for t in bb_bus[0]])
    BB_x.append([t+node_to_bus_gap+2*node_length + midline_gap for t in bb_bus[0]])
    BB_x.append([t+bus_h_spacing+node_to_bus_gap+2*node_length + midline_gap for t in bb_bus[0]])
    for y in range(4):
        BB_y.append(bb_bus[1])
    image_height = 0.3+bus_height
    image_width = 0.3+midline_gap + 2*node_length+2*node_to_bus_gap+4*node_height
    pixel_scaler = 500/6
else:
    for q in range(left_nodes):
        BB_y.append([t for t in bb_node[0]])
        BB_x.append([t+q*node_v_spacing for t in bb_node[1]])
    for q in range(right_nodes):
        BB_y.append([t+node_length+midline_gap for t in bb_node[0]])
        BB_x.append([t+q*node_v_spacing for t in bb_node[1]])
    
    BB_y.append([t-node_to_bus_gap -node_height- bus_h_spacing for t in bb_bus[0]])
    BB_y.append([t-node_to_bus_gap-node_height for t in bb_bus[0]])
    BB_y.append([t+node_to_bus_gap+2*node_length + midline_gap for t in bb_bus[0]])
    BB_y.append([t+bus_h_spacing+node_to_bus_gap+2*node_length + midline_gap for t in bb_bus[0]])
    for y in range(4):
        BB_x.append(bb_bus[1])
    image_width = 0.3+bus_height
    image_height = 0.3+midline_gap + 2*node_length+2*node_to_bus_gap+4*node_height
    pixel_scaler = 500/5

names = list(range(167))


#replace voltage here so that instead of random array we use the data from a pyserial read.
###Have these values come in a correct, ordered way!
string_to_write = "63\r\n"
s.write(bytes(string_to_write,'UTF-8'))
time.sleep(1)
no_more_data = False


##this is a serious cludge:
all_data = ""

while not no_more_data:
    #print("going")
    time.sleep(0.1)
    data_left = s.inWaiting()
    if (data_left >0): 
        all_data += str(s.read(data_left))
    else:
        no_more_data = True

s.close()
print(all_data)
x = all_data.split("'")
x = x[1]
print(x)
x = x.split("&")
x = x[:-1]
bins=[]
for y in x:
    parts = y.split(":")
    print(parts[0])
    print(parts[1])
    bins.append((int(parts[0]),int(parts[1])))
#for random testing:
#voltage = [3.3*random.random() for x in range(len(names))]
voltage  = [3.3*y[1]/1023 for y in bins]
print (voltage)
####--------------------------------------------------------------

#colors = ["#F1EEF6", "#D4B9DA", "#C994C7", "#DF65B0", "#DD1C77", "#980043"]

def color_getter(value,maximum):
    integer = int(math.floor(value*255/maximum))
    print (integer)
    hexval = hex(integer)[2:]
    print (hexval)
    if len(str(hexval))==1:
        return "#" +"0" +hexval+"0000"
    else:
        return "#" +hexval+"0000"

    

colors = [color_getter(v,3.3) for v in voltage]
print (colors)
source = ColumnDataSource(
    data = dict(
        x=BB_x,
        y=BB_y,
        color=colors,
        name=names,
        voltage=voltage,
    )
)


output_file("bb_test_1.html", title="Breadboard Visualizer v1.0")

TOOLS="pan,wheel_zoom,box_zoom,reset,hover,save"

p = figure(title="Breadboard Voltages", tools=TOOLS)
p.toolbar.logo=None
#print(pixel_scaler*image_width)
#print(pixel_scaler*image_height)

p.patches('x', 'y',
    fill_color='color', fill_alpha=0.7,
    line_color="white", line_width=0.0,
    source=source)
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

p.plot_height=int(pixel_scaler*image_height)
p.plot_width=int(pixel_scaler*image_width)

hover = p.select(dict(type=HoverTool))
hover.point_policy = "follow_mouse"
hover.tooltips = OrderedDict([
    ("Name", "@name"),
    ("Voltage)", "@voltage V"),
])

show(p)
