from __future__ import print_function, absolute_import, division, unicode_literals

import numpy as np
import copy

from astropy import units as u

from linetools.spectra import plotting as ltsp

def navigate(psdict, event, init=False):
    """ Method to Navigate spectrum

    Updates the dict

    Parameters
    ----------
    init :  (False) Initialize
      Just pass back valid key strokes
    """
    # Initalize
    if init is True:
        return ['l','r','b','t','T','i','I', 'o','O',
                '[',']','W','Z', 'Y', '{', '}', 's']
    #
    if (not isinstance(event.xdata,float)) or (not isinstance(event.ydata,float)):
        print('Navigate: You entered the {:s} key out of bounds'.format(
            event.key))
        return 0

    if event.key == 'l':  # Set left
        psdict['x_minmax'][0] = event.xdata
    elif event.key == 'r':  # Set Right
        psdict['x_minmax'][1] = event.xdata
    elif event.key == 'b':  # Set Bottom
        psdict['y_minmax'][0] = event.ydata
    elif event.key == 't':  # Set Top
        psdict['y_minmax'][1] = event.ydata
    elif event.key == 'T':  # Set Top to 1.1
        psdict['y_minmax'][1] = 1.1
    elif event.key == 's':  # Select window (i.e. zoom-in)
        if psdict['tmp_xy'] is None:
            psdict['tmp_xy'] = [event.xdata,event.ydata]
            print('Press another s to set the zoom-in window')
        else:
            psdict['x_minmax'][0] = np.minimum(event.xdata,psdict['tmp_xy'][0])
            psdict['x_minmax'][1] = np.maximum(event.xdata,psdict['tmp_xy'][0])
            psdict['y_minmax'][0] = np.minimum(event.ydata,psdict['tmp_xy'][1])
            psdict['y_minmax'][1] = np.maximum(event.ydata,psdict['tmp_xy'][1])
            psdict['tmp_xy'] = None
    elif event.key == 'i':  # Zoom in (and center)
        deltx = (psdict['x_minmax'][1]-psdict['x_minmax'][0])/4.
        psdict['x_minmax'] = [event.xdata-deltx, event.xdata+deltx]
    elif event.key == 'I':  # Zoom in (and center)
        deltx = (psdict['x_minmax'][1]-psdict['x_minmax'][0])/16.
        psdict['x_minmax'] = [event.xdata-deltx, event.xdata+deltx]
    elif event.key == 'o':  # Zoom in (and center)
        deltx = psdict['x_minmax'][1]-psdict['x_minmax'][0]
        psdict['x_minmax'] = [event.xdata-deltx, event.xdata+deltx]
    elif event.key == 'O':  # Zoom in (and center)
        deltx = psdict['x_minmax'][1]-psdict['x_minmax'][0]
        psdict['x_minmax'] = [event.xdata-2*deltx, event.xdata+2*deltx]
    elif event.key == 'Y':  # Zoom in (and center)
        delty = psdict['y_minmax'][1]-psdict['y_minmax'][0]
        psdict['y_minmax'] = [event.ydata-delty, event.ydata+delty]
    elif event.key in ['[',']','{','}']:  # Pan
        center = (psdict['x_minmax'][1]+psdict['x_minmax'][0])/2.
        deltx = (psdict['x_minmax'][1]-psdict['x_minmax'][0])/2.
        if event.key == '[':
            new_center = center - deltx
        elif event.key == ']':
            new_center = center + deltx
        elif event.key == '{':
            new_center = center - 4*deltx
        elif event.key == '}':
            new_center = center + 4*deltx
        psdict['x_minmax'] = [new_center-deltx, new_center+deltx]
    elif event.key == 'W': # Reset the Window
        psdict['x_minmax'] = copy.deepcopy(psdict['sv_xy_minmax'][0])
        psdict['y_minmax'] = copy.deepcopy(psdict['sv_xy_minmax'][1])
    elif event.key == 'Z': # Zero
        psdict['y_minmax'][0] = 0.
    else:
        if not (event.key in ['shift']):
            rstr = 'Key {:s} not supported.'.format(event.key)
            print(rstr)
        return 0
    return 1


def set_doublet(iself, event):
    """ Set z and plot doublet
    """
    wv_dict = {'C': (1548.195, 1550.770, 'CIV'),
               'M': (2796.352, 2803.531, 'MgII'),
               '4': (1393.755, 1402.770, 'SiIV'),
               'X': (1031.9261, 1037.6167, 'OVI'),
               '8': (770.409, 780.324, 'NeVIII'),
               'B': (1025.4433, 1215.6701, 'Lyba')}
    wrest = wv_dict[event.key]

    # Set z
    iself.zabs = event.xdata/wrest[0] - 1.
    try:
        iself.statusBar().showMessage('z = {:g} for {:s}'.format(
                iself.zabs, wrest[2]))
    except AttributeError:
        print('z = {:g} for {:s}'.format(iself.zabs, wrest[2]))

    return np.array(wrest[0:2])*(1.+iself.zabs)


def set_llist(llist, in_dict=None, sort=True):
    """ Method to set a line list dict for the Widgets

    Parameters
    ----------
    sort : bool, optional
      Sort lines by rest wavelength
    """
    from linetools.lists.linelist import LineList
    from astropy.units.quantity import Quantity

    if in_dict is None:
        in_dict = dict(Lists=[])

    if isinstance(llist,basestring): # Set line list from a file
        in_dict['List'] = llist
        in_dict['Lists'].append(llist)
        if llist == 'None':
            in_dict['Plot'] = False
        else:
            in_dict['Plot'] = True
            # Load?
            if not (llist in in_dict):
                # Homebrew
                if llist == 'OVI':
                    gdlines = u.AA*[629.730, 702.332, 770.409, 780.324, 787.711, 832.927, 972.5367, 977.0201,
                        1025.7222, 1031.9261, 1037.6167, 1206.5, 1215.6700, 1260.4221]
                    llist_cls = LineList('Strong', subset=gdlines)
                    in_dict[llist] = llist_cls
                else:
                    llist_cls = LineList(llist)
                    # Sort
                    llist_cls._data.sort('wrest')
                    # Load
                    in_dict[llist] = llist_cls
    elif isinstance(llist, (Quantity, list)): # Set from a list of wrest
        in_dict['List'] = 'input.lst'
        in_dict['Lists'].append('input.lst')
        in_dict['Plot'] = True
        # Fill
        if sort:
            llist.sort()
        llist_cls = LineList('ISM', subset=llist)
        in_dict['input.lst'] = llist_cls
    else:
        raise IOError('Not ready for this type of input')

    # Return
    return in_dict


# Read spectrum, pass back it and spec_file name
def read_spec(ispec, exten=None):
    """Parse spectrum out of the input

    If 2 spectra are given, the 2nd is scaled to the first

    Parameters
    ----------
    ispec : Spectrum1D, str, list of files (ordered blue to red),
       or tuple of arrays
    exten : int, optional
      FITS extension

    Returns
    -------
    spec : XSpectrum1D
    spec_file : str
    """
    from specutils.spectrum1d import Spectrum1D
    from linetools.spectra import xspectrum1d as lsx
    #
    if isinstance(ispec,basestring):
        spec_fil = ispec
        spec = lsx.XSpectrum1D.from_file(spec_fil, exten=exten)
    elif isinstance(ispec,Spectrum1D):
        spec = ispec
        spec_fil = spec.filename # Grab from Spectrum1D
    elif isinstance(ispec,tuple):
        spec = lsx.XSpectrum1D.from_tuple(ispec)
        spec_fil = 'none'
    elif isinstance(ispec,list): # Multiple file names
        # Loop on the files
        for kk,ispecf in enumerate(ispec):
            jspec = lsx.XSpectrum1D.from_file(ispecf, exten=exten)
            if kk == 0:
                spec = jspec
                _, xper1 = ltsp.get_flux_plotrange(spec.flux, perc=0.9)
            else:
                # Scale flux for convenience of plotting (sig is not scaled)
                _, xper2 = ltsp.get_flux_plotrange(jspec.flux, perc=0.9)
                scl = xper1[1]/xper2[1]
                # Splice
                spec = spec.splice(jspec, scale=scl)
            # Filename
            spec_fil = ispec[0]
            spec.filename=spec_fil
    else:
        raise ValueError('Bad input to read_spec: {:s}'.format(type(ispec)))

    # Return
    return spec, spec_fil
