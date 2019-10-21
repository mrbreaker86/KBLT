#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TomoPy example to reconstruct the HZG nano tomography data after data have been realigned.
The script shows an example of how to reconstruct with gridrec and with sirtfbp

"""

from __future__ import print_function
import tomopy
import dxchange
import dxchange.reader as dxreader
import tomopy.misc.corr
import numpy as np
import os
from scipy import signal
import time

#needed for normalization
import tomopy.util.mproc as mproc
import tomopy.util.extern as extern
import tomopy.util.dtype as dtype
import logging
import numexpr as ne

from matplotlib.pyplot import imshow
from PIL import Image
#from skimage.util import img_as_uint, img_as_int

from skimage import data
from skimage.transform import rotate, SimilarityTransform, warp
from skimage.color import rgb2gray

import tifffile as tiff
from tifffile import imsave

def read_rgb_convert(fname, name, save_out):

    fname = os.path.abspath(fname)
    data_name = os.path.join(fname, name + '*.tif')
#    print(data_name)

#    for m, fname in enumerate(data_name):
    data = tiff.imread(data_name)
#    data = data.astype(np.int16)
    data = rgb2gray(data) * 32767
#    data = rgb2gray(data) * 65536
    data = data.astype(np.int16)
    
    #data = np.average(data, axis=3)

    #print('data type: ')
    #print(len(data[0]))
    #print(type(data[0]))
    
    if save_out is True:
        fname_out = os.path.join(fname, '16bit')    
        if not os.path.exists(fname_out):
            os.makedirs(fname_out)
        
        for i in range(len(data)):
            imsave(fname_out + '/' + name + '_' + "%04d" % (i+1,) + '.tif', data[i])
        
        print("Saved down 16bit converted %s!" %name)
            
    return data

def read_kblt(fname, ind_tomo, ind_flat, proj=None, sino=None):
    """
    Read KBLT Larsson standard data format.

    Parameters
    ----------
    fname : str
        Path to data folder.

    ind_tomo : list of int
        Indices of the projection files to read.

    ind_flat : list of int
        Indices of the flat field files to read.

    proj : {sequence, int}, optional
        Specify projections to read. (start, end, step)

    sino : {sequence, int}, optional
        Specify sinograms to read. (start, end, step)

    Returns
    -------
    ndarray
        3D tomographic data.

    ndarray
        3D flat field data.

    """
    fname = os.path.abspath(fname)
    tomo_name = os.path.join(fname, 'tomo_0001.tif')
    flat_name = os.path.join(fname, 'flat_0001.tif')
    if proj is not None:
        ind_tomo = ind_tomo[slice(*proj)]
    tomo = dxreader.read_tiff_stack(
        tomo_name, ind=ind_tomo, slc=(sino, None))
    flat = dxreader.read_tiff_stack(
        flat_name, ind=ind_flat, slc=(sino, None))
    return tomo, flat

def crop(data, name, x1, y1, x2, y2, save_out = False):
    print("Starting cropping of data.")
    t0 = time.time()
    data = data[:, y1:y2, x1:x2]
    print("cropping of %s done!" % name)
    print('Croping took: ' + str(round(time.time()-t0,2)) + ' seconds')

    if save_out is True:
        output = fname_out + crop_name + '/' + name
        print(output)
        dxchange.write_tiff_stack(data[:, :, :], fname=output)
        print("Saved down croped %s" % name)

    return data

def kblt_normalize(arr, flat, cutoff=None, ncore=None, out=None):
    """
    Normalize raw projection data using the flat and dark field projections.

    Parameters
    ----------
    arr : ndarray
        3D stack of projections.
    flat : ndarray
        3D flat field data.
    cutoff : float, optional
        Permitted maximum vaue for the normalized data.
    ncore : int, optional
        Number of cores that will be assigned to jobs.
    out : ndarray, optional
        Output array for result. If same as arr,
        process will be done in-place.

    Returns
    -------
    ndarray
        Normalized 3D tomographic data.
    """
    arr = dtype.as_float32(arr)
    l = np.float32(1e-6)
    flat = np.mean(flat, axis=0, dtype=np.float32)

    with mproc.set_numexpr_threads(ncore):
        denom = ne.evaluate('flat')
        ne.evaluate('where(denom<l,l,denom)', out=denom)
        out = ne.evaluate('arr', out=out)
        ne.evaluate('out/denom', out=out, truediv=True)
        if cutoff is not None:
            cutoff = np.float32(cutoff)
            ne.evaluate('where(out>cutoff,cutoff,out)', out=out)
    return out

def flat_fielding(tomo, flat, save_out = False):
    print("Starting flat-fielding of data.")
    t0 = time.time()
    data = kblt_normalize(tomo, flat)
    data = tomopy.minus_log(data)
    print('Flat-fielding took: ' + str(round(time.time()-t0,2)) + ' seconds')

    if save_out is True:
        output = fname_out + norm_name + '/' + tomo_name
        print(output)
        dxchange.write_tiff_stack(data[:, :, :], fname=output)
        print("Saved down normalized %s" % tomo_name)
    return data

    if save_out is True:
        output = fname_out + norm_name + '/' + tomo_name
        print(output)
        dxchange.write_tiff_stack(data[:, :, :], fname=output)
        print("Saved down normalized %s" % tomo_name)
    return data

def recon_gridrec(data, slice_start, slice_end, theta, rot_center, save_out = True, cr_in_filename = False):
    t0 = time.time()
    rec = tomopy.recon(data[:, slice_start:slice_end, :], theta=theta, center=rot_center, algorithm='gridrec')
    #remove outer circle
    rec = tomopy.circ_mask(rec, axis=0, ratio=0.95)
    if save_out is True:
        if cr_in_filename is True:
            output= fname_out + recon_name + '/' + slice_name + '_cr_' + str(rot_center)
        elif cr_in_filename is False:
            output= fname_out + recon_name + '/' + slice_name
        #print(output)
        dxchange.write_tiff_stack(rec[:, :, :], fname=output)
    print("Reconstructed using GRIDREC done!")
    print('Reconstruction took: ' + str(round(time.time()-t0,2)) + ' seconds')
    return rec

def recon_sirt(data, slice_start, slice_end, theta, rot_center, iter_for_sirt = 100, save_out = True, cr_in_filename = False):
    t0 = time.time()
    num_iter = iter_for_sirt
    nCol = data.shape[2]
    sirtfbp_filter = sirtfilter.getfilter(nCol, theta, num_iter, filter_dir='./')
    tomopy_filter = sirtfilter.convert_to_tomopy_filter(sirtfbp_filter, nCol)
    rec = tomopy.recon(data[:, slice_start:slice_end, :], theta, center=rot_center, algorithm='gridrec', filter_name='custom2d', filter_par=tomopy_filter)
    if save_out is True:
        if cr_in_filename is True:
            output= fname_out + recon_name + '_SIRT/' + slice_name + '_cr_' + str(rot_center)
        elif cr_in_filename is False:
            output = fname_out + recon_name + '_SIRT/' + slice_name
        #print(output)
        dxchange.write_tiff_stack(rec[:, :, :], fname=output)
    print("Reconstructed using SIRT and GRIDREC done!")
    print('Reconstruction took: ' + str(round(time.time()-t0,2)) + ' seconds')
    return rec

def ring_rem(rec, remwidth, varying_width = False, save_out = True):
    t0 = time.time()
    rec = tomopy.misc.corr.remove_ring(rec, center_x=None, center_y=None, thresh=300.0,
                                       thresh_max=300.0, thresh_min=-100.0, theta_min=30, rwidth=remwidth,
                                       int_mode='REFLECT', ncore=None, nchunk=None, out=None)
    if save_out is True:
        if varying_width is True:
            output = fname_out + recon_name + '_ring_rem/' + slice_name + '_' + str(remwidth)
        elif varying_width is False:
            output = fname_out + recon_name + '_ring_rem/' + slice_name
    #print(output)
    dxchange.write_tiff_stack(rec[:, :, :], fname=output)
    print('Ring removal using width %s is done!' % remwidth)
    print('Ring removal took: ' + str(round(time.time()-t0,2)) + ' seconds')
    return rec

def sub_proj_zero_180(im_0, im_180, tilt, trans_x, trans_y):
    im_0 = rotate(im_0, angle=tilt, resize=False, center=None, order=1, mode='constant', cval=0, clip=True, preserve_range=False)
    im_180 = rotate(im_180, angle=tilt, resize=False, center=None, order=1, mode='constant', cval=0, clip=True, preserve_range=False) 

    tform = SimilarityTransform(translation=(trans_x, trans_y))
    im_180 = warp(im_180, tform)

    sub = im_0 - np.fliplr(im_180)
    #convert to 16bit
    #sub = img_as_int(sub)
    #output = fname_out + 'subtracted/' + 'tomo_0001'
    #dxchange.write_tiff_stack(sub, fname=output)
    return sub

def rotate_tomo(proj, tilt, save_out):
    for i in range(len(proj)):
        proj[i] = rotate(proj[i], angle=1.5, resize=False, center=None, order=1, mode='constant', cval=0, clip=True, preserve_range=False)

    if save_out is True:
        output = fname_out + norm_name + '_tilted_' + str(tilt) + '/' + tomo_name
        print(output)
        dxchange.write_tiff_stack(data[:, :, :], fname=output)
        print("Saved down titled projections %s" % tomo_name)
    return data
 
if __name__ == '__main__':

    #Specify the names of the output folders
    global crop_name
    crop_name = '1_PROJ_croped'
    global norm_name
    norm_name = '2_PROJ_normalized'
    global align_name
    align_name = '3_PROJ_aligned'
    global phr_name
    phr_name = '4_PROJ_PhR'
    global recon_name
    recon_name = '5_reconstructed'
    global slice_name
    slice_name = 'slice'
    global tomo_name
    tomo_name = 'tomo'
    global flat_name
    flat_name = 'flat'
    
#    fname = 'C:/Users/emanuella/Desktop/kCT/DATA SETS/lego_man/16bit/'
#    fname_out = 'C:/Users/emanuella/Desktop/kCT/DATA SETS/lego_man/'

#    fname = 'C:/Users/emanuella/Desktop/kCT/DATA SETS/screw_newbase/'
#    fname_out = 'C:/Users/emanuella/Desktop/kCT/DATA SETS/screw_newbase/'

    fname = '/volume1/programming/KBLT/DATA_SETS/20191010_22_44_20/'
    fname_out = fname

    tomo_start = 1
    tomo_end = 200
    flat_start = 1
    flat_end = 6#11

    ind_flat = range(flat_start, flat_end)
    ind_tomo = range(tomo_start, tomo_end)

    tomo = read_rgb_convert(fname, 'tomo', save_out = False)
    flat = read_rgb_convert(fname, 'flat', save_out = False)
#    imshow(hej[99])
#    print(len(hej))

#    tomo, flat = read_kblt(fname, ind_tomo, ind_flat, proj=None, sino=None)
#    print('read in done!')

    #Normalized the projection images
    data = flat_fielding(tomo, flat, save_out = False)

    #rotate data, due to camera tilting
    #data = rotate_tomo(data, tilt = 1.5, save_out = False)

    tilt = 2

#    check correctness of tilting
    sub = sub_proj_zero_180(data[0], data[99], tilt = tilt, trans_x = 0, trans_y = 0)
    #sub = sub_proj_zero_180(data[49], data[149], tilt = tilt, trans_x = -10, trans_y = 0)
    imshow(sub)
    
    #perform tilt correction
    data = rotate_tomo(data, tilt=tilt, save_out = False)

#    sub = sub_proj_zero_180(data[0], data[99], tilt = 1.5)
#    imshow(sub)

#    t0 = time.time()
#    data = tomopy.remove_stripe_fw(data, level=None, wname='db5', sigma=1, pad=True, ncore=None, nchunk=None)
#    print('Sinogram ring-removal took: ' + str(round(time.time() - t0, 2)) + ' seconds')

    #Set data collection angles as equally spaced between 0-180 degrees.
    theta = tomopy.angles(data.shape[0], 0, 360)
    #center of rotation in the middle of the image
    rot_center_m = (data.shape[2]) / 2.0
    print('The central point of the image is: ' + str(rot_center_m))
    rot_center_m = tomopy.find_center_pc(data[0], data[-1], tol=0.5, rotc_guess=rot_center_m)
    print('The automatically detected CoR is: ' + str(rot_center_m))
    #manual rot center
    rot_center_m = 195
    print('The manually set CoR is: ' + str(rot_center_m))

    height = len(data[0])

    #recon_name = '5_reconstructed_cr_test'
    #for i in range(-20, 20, 1):
    #    print(i)
    #    rec = recon_gridrec(data, slice_start = height-31, slice_end = height-30, theta=theta, rot_center=rot_center_m+i, save_out = True, cr_in_filename = True)
    #    imshow(rec[0])

    recon_name = '5_reconstructed_tilt_' + str(tilt) + '_CR_' + str(rot_center_m)
    rec = recon_gridrec(data, slice_start = 0, slice_end = height-1, theta=theta, rot_center=rot_center_m, save_out = True, cr_in_filename = False)
    imshow(rec[height-31])
