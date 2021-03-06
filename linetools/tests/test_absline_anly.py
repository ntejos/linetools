# Module to run tests on AbsLine analysis

# TEST_UNICODE_LITERALS
from __future__ import print_function, absolute_import, division, unicode_literals

import numpy as np
import os, pdb
import pytest
from astropy import units as u

from linetools.spectralline import AbsLine
from linetools.spectra import io as lsio

def data_path(filename):
    data_dir = os.path.join(os.path.dirname(__file__), '../spectra/tests/files')
    return os.path.join(data_dir, filename)

def test_aodm_absline():
    # Init CIV 1548
    abslin = AbsLine(1548.195*u.AA)

    # Set spectrum
    abslin.analy['spec'] = lsio.readspec(data_path('UM184_nF.fits')) # Fumagalli+13 MagE spectrum
    abslin.analy['wvlim'] = [6080.78, 6087.82]*u.AA
    #
    abslin.measure_aodm()
    N, sig_N, flgN = [abslin.attrib[key] for key in ['N','sig_N','flag_N']]

    np.testing.assert_allclose(N.value, 300010067404184.0)
    assert N.unit == 1/u.cm**2
    assert flgN == 1
    # Now velocity limits

    abslin.analy['wvlim'] = np.zeros(2)*u.AA
    abslin.analy['vlim'] = (-150., 150.)*u.km/u.s
    abslin.attrib['z'] = 2.92929
    #
    abslin.measure_aodm()
    N, sig_N, flgN = [abslin.attrib[key] for key in ['N','sig_N','flag_N']]
    np.testing.assert_allclose(N.value, 80369217498895.17)
    return

def test_boxew_absline():
    # Text boxcar EW evaluation
        # Init CIV 1548
    abslin = AbsLine(1548.195*u.AA)

    # Set spectrum
    abslin.analy['spec'] = lsio.readspec(data_path('UM184_nF.fits')) # Fumagalli+13 MagE spectrum
    abslin.analy['wvlim'] = [6080.78, 6087.82]*u.AA
    # Measure EW (not rest-frame)
    abslin.measure_ew()
    ew = abslin.attrib['EW']

    np.testing.assert_allclose(ew.value, 0.9935021012055584)
    assert ew.unit == u.AA

    abslin.measure_restew()
    #import pdb
    #pdb.set_trace()
    np.testing.assert_allclose(ew.value, 0.9935021012055584/(1+abslin.attrib['z']))

def test_gaussew_absline():
    # Text Gaussian EW evaluation
    # Init CIV 1548
    abslin = AbsLine(1548.195*u.AA)

    # Set spectrum
    abslin.analy['spec'] = lsio.readspec(data_path('UM184_nF.fits')) # Fumagalli+13 MagE spectrum
    abslin.analy['wvlim'] = [6080.78, 6087.82]*u.AA
    # Measure EW (not rest-frame)
    abslin.measure_ew(flg=2)
    ew = abslin.attrib['EW']

    np.testing.assert_allclose(ew.value, 1.02,atol=0.01)
    assert ew.unit == u.AA

    abslin.measure_ew(flg=2,initial_guesses=(0.5,6081,1))
    np.testing.assert_allclose(ew.value, 1.02,atol=0.01)

    abslin.measure_restew()
    np.testing.assert_allclose(ew.value, 1.02/(1+abslin.attrib['z']),atol=0.01)


def test_ismatch():
    # Init CIV 1548
    abslin = AbsLine(1548.195*u.AA)
    abslin.attrib['z'] = 1.2322

    abslin2 = AbsLine(1548.195*u.AA)
    abslin2.attrib['z'] = 1.2322

    assert abslin.ismatch(abslin2)
    # tuples
    assert abslin.ismatch((1.2322,1548.195*u.AA))
    assert abslin.ismatch((1.2322,1548.195*u.AA),Zion=(6,4))
