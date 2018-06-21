'''
This script is used to test Current Source Density Estimates, 
using the kCSD method Jan et.al (2012)

This script is in alpha phase.

This was written by :
Chaitanya Chintaluri, 
Laboratory of Neuroinformatics,
Nencki Institute of Exprimental Biology, Warsaw.
'''
import os
import scipy.stats as st
import time
import numpy as np
from scipy.integrate import simps 
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.mlab import griddata
from matplotlib import ticker
import csd_profile_model_bar as prof
from kcsd.corelib import KCSD as KCSD
from skimage import io

def do_kcsd(ele_pos, pots, **params):
    """
    Function that calls the KCSD2D module
    """
    if abs(ele_pos[1][1] - ele_pos[0][1])> abs(ele_pos[1][0] - ele_pos[0][0]):
        ele_space = abs(ele_pos[1][1] - ele_pos[0][1])
        ele_dist = abs(ele_pos[-1][1] - ele_pos[0][1])
    else:
        ele_space = abs(ele_pos[1][0] - ele_pos[0][0])
        ele_dist = abs(ele_pos[-1][0] - ele_pos[0][0])
        
    num_ele = len(ele_pos)
    ery = np.linspace(ele_space, ele_dist/2, int(num_ele/2))
#    print(ele_pos, ery)
    pots = pots.reshape(num_ele, 1)
    
    Lamb = [-9, -3]
    lambdas =np.logspace(Lamb[0], Lamb[1], 50, base = 10)
    k = KCSD.KCSD2D(ele_pos, pots, **params)
    k.L_curve(ploting = 0, lambdas = lambdas, Rs = ery)
#    k.cross_validate(Rs=np.array([k.R]), lambdas = np.logspace(Lamb[0], Lamb[1], 50, base = 10))
#    plt.title('kCSD_2d')
    plt.figure()
    lr = plt.subplot(111)
    lr.set_title('Best R: ' +str(k.R))
    plt.imshow(k.curve_surf, extent=[Lamb[0], Lamb[1], ery[-1], ery[0]], interpolation = 'none', aspect = 'auto',
               cmap='PRGn',vmax = np.max(k.curve_surf),vmin = -np.max(k.curve_surf))
    plt.colorbar()
    est_csd = k.values('CSD')
    est_pot = k.values('POT')
    
    return k, est_csd, est_pot

def generate_csd_2D(src_width, name, srcs=np.array([0]),
                    start_x=0., end_x=1., 
                    start_y=0., end_y=1., 
                    res_x=50, res_y=50):
    """
    Gives CSD profile at the requested spatial location, at 'res' resolution
    """
    csd_x, csd_y = np.mgrid[start_x:end_x:np.complex(0,res_x), 
                            start_y:end_y:np.complex(0,res_y)]

    f = prof.gauss_2d_small(csd_x, csd_y, src_width, tpy=name, srcs=srcs)
    
    return csd_x, csd_y, f

def grid(x, y, z, resX=100, resY=100):
    """
    Convert 3 column data to matplotlib grid
    """
    z = z.flatten()
    xi = np.linspace(min(x), max(x), resX)
    yi = np.linspace(min(y), max(y), resY)
    zi = griddata(x, y, z, xi, yi, interp='linear')
    return xi, yi, zi  

def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

def make_plots(title, 
               t_csd_x, t_csd_y, true_csd, 
               ele_x, ele_y, pots, 
               k_csd_x, k_csd_y, est_pot, 
               est_csd, save_as):
    """
    Shows 3 plots
    1_ true CSD generated based on the random seed given
    2_ interpolated LFT (NOT kCSD pot though), generated by simpsons rule integration
    3_ results from the kCSD 2D for the default values
    """
    #True CSD
    fig = plt.figure(figsize=(16, 12), dpi=120)
    
    tick_locator = ticker.MaxNLocator(nbins=7)
    
    ax1 = plt.subplot(221)
    logo = io.imread(title[-1])#ob
    
    t_max = np.max(np.abs(true_csd))
    levels = np.linspace(-1*t_max, t_max, 32)
    im = ax1.contourf(t_csd_x, t_csd_y, true_csd, levels=levels, cmap=cm.bwr, alpha = 0.5)
    plt.scatter(ele_x, ele_y, 8, color = 'yellow')
    
    plt.imshow(logo, extent = [0,1,0,1]) #[20:1130,155:780]
    
    ax1.set_title('TrueCSD')
    cb = plt.colorbar(im)
    cb.locator = tick_locator
    cb.update_ticks()

#    ax3 = plt.subplot(132, aspect='equal')
#    
#    ax3.set_title('Measured potential: interpolated LFP')#+ 'I position and width = ' + str(b_width[argbrl]))
#    ax3.set_xlabel('y')
#    ax3.set_ylabel('x')
#    
#    t_max = np.max(np.abs(est_pot))
#    levels = np.linspace(-1*t_max, t_max, 32)
#    im3 = ax3.contourf(k_csd_x, k_csd_y, est_pot[:,:,0], levels=levels, cmap='PRGn')
#    plt.scatter(ele_x, ele_y, 8, color = 'yellow')
#    cb3 = plt.colorbar(im3, orientation='horizontal')
#    cb3.locator = tick_locator
#    cb3.update_ticks()
#    plt.legend()
    
    ax3 = plt.subplot(212)
    ax3.set_title('Measured potential: interpolated LFP')#+ 'I position and width = ' + str(b_width[argbrl]))

    
    ind = np.arange(len(pots))+1
    if abs(ele_x[1]-ele_x[0]) > abs(ele_y[1]- ele_y[0]):
        ax3.plot(ind, pots*1000, 'b',marker = 'o', linewidth=0.1)
        ax3.set_xlabel('electrode contact number', fontsize=20)
        ax3.set_ylabel('Potential [mV]', fontsize=20)
        plt.xticks(ind, ind)
    else:
        ax3.plot(pots*1000, ind, 'b',marker = 'o', linewidth=0.1)
        ax3.set_ylabel('electrode contact number', fontsize=20)
        ax3.set_xlabel('Potential [mV]', fontsize=20)
        plt.yticks(ind, ind)
        
        
    plt.legend()
    plt.grid()
    
    ax4 = plt.subplot(222, aspect='equal')

    ax4.set_title('2D kCSD reconstruction')#: '+ 'source+sink = '+ str(normstat)+'| brl_height = '+ str(argbrl))
    levels_kcsd = np.linspace(-1*np.max(abs(est_csd[:,:,0])), np.max(abs(est_csd[:,:,0])), 32)
    im4 = ax4.contourf(k_csd_x, k_csd_y, est_csd[:,:,0], levels=levels_kcsd, cmap=cm.bwr, alpha = 0.5)
    
    plt.scatter(ele_x, ele_y, 8, color = 'yellow')
    ax4.imshow(logo, extent = [0,1,0,1])
    
    cb4 = plt.colorbar(im4)
    cb4.locator = tick_locator
    cb4.update_ticks()
    
    fig.suptitle("Lambda =" + title[0] + " I R = " + title[1] + 
                 " I Noise_lvl =" + title[2])
    
    return np.linalg.norm(true_csd - est_csd)

def integrate_2D(x, y, xlim, ylim, csd, h, xlin, ylin, X, Y):
    """
    X,Y - parts of meshgrid - Mihav's implementation
    """
    Ny = ylin.shape[0]
    m = np.sqrt((x - X)**2 + (y - Y)**2)     # construct 2-D integrand
    m[m < 0.0000001] = 0.0000001             # I increased acuracy
    y = np.arcsinh(2*h / m) * csd            # corrected
    I = np.zeros(Ny)                         # do a 1-D integral over every row
    for i in range(Ny):
        I[i] = simps(y[:, i], ylin)          # I changed the integral
    F = simps(I, xlin)                       # then an integral over the result 
    return F 

def calculate_potential_2D(true_csd, ele_xx, ele_yy, csd_x, csd_y):
    """
    For Mihav's implementation to compute the LFP generated
    """
    xlin = csd_x[:,0]
    ylin = csd_y[0,:]
    xlims = [xlin[0], xlin[-1]]
    ylims = [ylin[0], ylin[-1]]
    sigma = 0.3
    h = 50.
    pots = np.zeros(len(ele_xx))
    for ii in range(len(ele_xx)):
        pots[ii] = integrate_2D(ele_xx[ii], ele_yy[ii], 
                                xlims, ylims, true_csd, h, 
                                xlin, ylin, csd_x, csd_y)
    pots /= 2*np.pi*sigma
    return pots

def transformAndNormalizeLongGrid(D):
    #D is a dictionary
    locations = np.zeros((len(D),2))
    for i in range(len(D)):
        locations[i,0] = D[i]['x']
        locations[i,1] = D[i]['y']

    return locations

def generate_electrodes(inpos, lpos, b):
    loc = {}
    cordx = -(inpos[0] - lpos[0])/b
    cordy = -(inpos[1] - lpos[1])/b
    def _addLocToDict(D,chnum, x, y):
        d = {}
        d['x'] = x
        d['y'] = y
        D[chnum] = d
    #first add locations just as they suppose to be
    for i in range(b):
        _addLocToDict(loc, i, inpos[0] + cordx*i, inpos[1] + cordy*i)
    loc_mtrx = transformAndNormalizeLongGrid(loc)
    loc_mtrx = loc_mtrx.T 
    return loc_mtrx[0],loc_mtrx[1]
#def generate_electrodes(inpos, lpos, b):
#    loc = {}
##    cordx = -(inpos[0] - lpos[0])/b
##    cordy = -(inpos[1] - lpos[1])/b
#    def _addLocToDict(D,chnum, x, y):
#        d = {}
#        d['x'] = x
#        d['y'] = y
#        D[chnum] = d
#    #first add locations just as they suppose to be
#    for i in range(4):
#        for j in range(int(b/4)):
#            _addLocToDict(loc, i*int(b/4) + j, inpos[0] + lpos[0]*i, inpos[1] + lpos[1]*j)
#        
#    loc_mtrx = transformAndNormalizeLongGrid(loc)
#    loc_mtrx = loc_mtrx.T 
#    return loc_mtrx[0],loc_mtrx[1]

def electrode_config(ele_res, true_csd, csd_x, csd_y, inpos, lpos):
    """
    What is the configuration of electrode positions, between what and what positions
    """
    ele_x, ele_y = generate_electrodes(inpos, lpos, ele_res)
    pots = calculate_potential_2D(true_csd, ele_x, ele_y, csd_x, csd_y)
    ele_pos = np.vstack((ele_x, ele_y)).T     #Electrode configs
    return ele_pos, pots

def main_loop(src_width, total_ele, inpos, lpos, nm, noise=0, srcs=np.array([0])):
    """
    Loop that decides the random number seed for the CSD profile, 
    electrode configurations and etc.
    """
    #TrueCSD
    t_csd_x, t_csd_y, true_csd = generate_csd_2D(src_width, nm, srcs=srcs,
                                                 start_x=0, end_x=1., 
                                                 start_y=0, end_y=1, 
                                                 res_x=100, res_y=100)

#    percent = 0.1
#    true_csd += percent*(np.random.rand(100,100)*np.max(true_csd)-np.max(true_csd)/2)

    n_spec = [noise]
   
    RMS_wek = np.zeros(len(n_spec))
    LandR = np.zeros((2,len(n_spec)))
    
    for i, noise in enumerate(n_spec):
        noise = np.round(noise,5)
        print('numer rekonstrukcji: ', i, 'noise level: ' , noise)
        #Electrodes
        ele_pos, pots = electrode_config(total_ele, true_csd, t_csd_x, t_csd_y, inpos, lpos)
#        print (ele_pos)
        ele_x = ele_pos[:, 0]
        ele_y = ele_pos[:, 1]
        gdX = 0.01
        gdY = 0.01 #resolution of CSD space
        x_lims = [0, 1] #CSD estimation place
        y_lims = [0, 1]
        
#        np.random.seed(0)
        pots += (np.random.rand(total_ele)*np.max(abs(pots))-np.max(abs(pots))/2)*noise/100
        k, est_csd, est_pot = do_kcsd(ele_pos, pots, h=1., gdx=gdX, gdy=gdY, 
                             xmin=x_lims[0], xmax=x_lims[1], 
                             ymin=y_lims[0], ymax=y_lims[1])
      
        save_as = nm + '_noise' + str(noise)
        
        title = [str(k.lambd), str(k.R), str(noise), nm]
        RMS_wek[i] = make_plots(title, 
                           t_csd_x, t_csd_y, true_csd, 
                           ele_x, ele_y, pots,
                           k.estm_x, k.estm_y, est_pot,
                           est_csd, save_as)
    return RMS_wek, LandR

def randsample(x,ile):
	ind = st.randint.rvs(0,len(x),size = ile)
	y = x[ind]
	return y

if __name__=='__main__':
    saveDir = "/Users/Wladek/Dysk Google/kCSD_lcurve/quadr_source/"
    plt.close('all')
    total_ele = 32
    name =  'ob.png' # quadr, two_sink, dip, ob, hipo
    src_width = 0.05
    noise_lvl = 1e-3
    inpos = [0.5, 0.1]#od dolu
    lpos = [0.5, 0.8] 
        
    RMS_wek, LandR = main_loop(src_width, total_ele, inpos, lpos,
                               name, noise=noise_lvl)
    
    from pandas import DataFrame
    df = DataFrame({'RMS': RMS_wek.tolist(), 'Lambda': LandR[0].tolist(), 'R' : LandR[1].tolist()})
    df.to_excel(name + 'cv.xlsx', sheet_name='sheet1', index=False)