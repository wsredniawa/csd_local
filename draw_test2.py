# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 08:27:25 2018

@author: Wladek
"""
import matplotlib.pyplot as plt
from skimage import io,img_as_float
import numpy as np
import pandas as pd
plt.close('all')

def draw_line(im, point_num = 200, ele=False):
    fig, ax = plt.subplots()
    ax.imshow(im, extent = [0,1,0,1])
    ax.set_xlim(0,1)
    ax.set_ylim(0,1)
    ax.set_xlabel('To remove last point: left click and then del')
    x_pts = []
    y_pts = []
    pos = []
    if ele:
        plt.title('choose first electrode contact')
    else:
        plt.title('choose source place or press q to finish', color = 'red')
        
    def onpick(event):    
        this_artist = event.artist #the picked object is available as event.artist
        plt.gca().picked_object = this_artist

    def on_key(event):
        if event.key == u'delete':
            ax = plt.gca()
            if ax.picked_object:
                ax.picked_object.remove()
                ax.picked_object = None
                ax.figure.canvas.draw()
                x_pts.remove(x_pts[-1])
                y_pts.remove(y_pts[-1])

    def onclick(event):
        if event.dblclick:
            pos.append([event.xdata,event.ydata])
            m_x, m_y = event.x, event.y
            x, y = ax.transData.inverted().transform([m_x, m_y])
            x_pts.append(x)
            y_pts.append(y)
            if ele:
                
                plt.title('choose last electrode contact and press q')
                plt.scatter(x, y, s = 80, color = 'black', picker = 5)
                plt.plot(x_pts, y_pts)
            else:
                if len(pos)%2==1:
#                    plt.scatter(x, y, s = 80, color = 'red', picker = 5)
                    plt.scatter(x, y, s = 300, alpha = 0.3, color = 'red', picker = 5)
                    plt.title('choose sink place or press q to finish', color = 'blue')
                else:
#                    plt.scatter(x,y, s= 80, color = 'blue', picker = 5)
                    plt.scatter(x, y, s= 300, alpha = 0.3, color = 'blue', picker = 5)
                    plt.title('choose source place or press q to finish', color = 'red')
        
        fig.canvas.draw()
    
    con = fig.canvas.mpl_connect('button_press_event', onclick)
    fig.canvas.mpl_connect('pick_event', onpick)
    cid = fig.canvas.mpl_connect('key_press_event', on_key)
#    fig.show()
    return x_pts,y_pts



if __name__ == '__main__':
#    os.chdir('/Users/Wladek/Dysk Google/Figures for HFO in olfactory bulb/Ket-Xyl/')
    filename = 'hipo.png'
    logo = img_as_float(io.imread(filename))
    x,y = draw_line(logo) # here you click on the plot[20:1130,155:780]
    points = len(x)
#    pos = np.array([x,y])
#    pos = pos.reshape(points,2)
#    df = pd.DataFrame({'x pos': x, 'y pos': y})
#    df.to_excel('hipo.xlsx', sheet_name='sheet1', index=False)
    df = pd.read_excel(filename[:-4] + '.xlsx', skiprows = 0, index_col = None)
#
    xpos = df['x pos'].values
    ypos = df['y pos'].values
    pos = np.array([xpos,ypos])
    pos = pos.reshape(len(xpos), 2)
    plt.figure()
    cls = ['g', 'r' , 'b']
    plt.xlim(0,1)
    plt.ylim(0,1)
    plt.imshow(logo, extent = [0,1,0,1], alpha = 0.8)
    for sgn, poss in enumerate(pos):
            col = ((-1)**sgn)
            plt.scatter(xpos[sgn], ypos[sgn], color = cls[col])