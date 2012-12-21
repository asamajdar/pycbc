# Copyright (C) 2012  Alex Nitz
#
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


#
# =============================================================================
#
#                                   Preamble
#
# =============================================================================
#
"""This module contains convenience pN functions. This includes calculating conversions
between quantities.
"""
from __future__ import division
import lal
from numpy import log
from scipy.optimize import bisect




def mass1_mass2_to_tau0_tau3(mass1, mass2, f_lower):
    m_total = mass1 + mass2
    mu = mass1 * mass2 / m_total
    eta = mu / m_total
    tau3 = 1.0 / (8.0 * (lal.LAL_PI * lal.LAL_PI * f_lower**5)**(1.0/3.0) * m_total**(2.0/3.0) * eta)
    tau0 = 5.0 / (256.0 * (lal.LAL_PI * f_lower) ** (8.0/3.0) * m_total**(5.0/3.0) * eta)
    return tau0,tau3


def tau0_tau3_to_mtotal_eta(tau0, tau3, f_lower):
    t0q = 5.0 / (256.0 * (lal.LAL_PI * f_lower) ** (8.0/3.0) * tau0)
    t3q = 1.0 / (8.0 * (lal.LAL_PI * lal.LAL_PI * f_lower**5) ** (1.0/3.0 ) * tau3)
    eta = t3q * ( t0q / t3q ) ** (-2.0/3.0) ;
    m_total = t0q / t3q;
    return m_total,eta


def tau0_tau3_to_mass1_mass2(tau0, tau3, f_lower):
    t0q = 5.0 / (256.0 * ( lal.LAL_PI * f_lower)**( 8.0/3.0) * tau0)
    t3q = 1.0 / (8.0 * (lal.LAL_PI * lal.LAL_PI * f_lower **5.0)**(1.0/3.0 ) * tau3)
    eta = t3q * (t0q/t3q)**( -2.0/3.0 )
    m_total = t0q / t3q
    mass1 = 0.5 * m_total * (1.0 + (1.0-4.0*eta)**( 0.5 ))
    mass2 = 0.5 * m_total * (1.0 - (1.0-4.0*eta)**( 0.5 ))
    return mass1,mass2


def mass1_mass2_to_mtotal_eta(mass1, mass2):
    m_total = mass1 + mass2;
    eta = (mass1 * mass2) / (m_total * m_total)
    return m_total,eta


def mtotal_eta_to_mass1_mass2(m_total, eta):
    mass1 = 0.5 * m_total * (1.0 + (1.0 - 4.0 * eta)**0.5)
    mass2 = 0.5 * m_total * (1.0 - (1.0 - 4.0 * eta)**0.5)
    return mass1,mass2


def mchirp_eta_to_mass1_mass2(m_chirp, eta):
    M = m_chirp / (eta ** (3.0/5.0))
    return mtotal_eta_to_mass1_mass2( M, eta )


def mass1_mass2_to_mchirp_eta(mass1, mass2):
    M = mass1 + mass2
    mu = mass1 * mass2 / M
    eta = mu / M
    m_chirp = mu ** (3.0/5.0) * M ** (2.0/5.0)
    return m_chirp, eta

def mass1_mass2_spin1z_spin2z_to_beta_sigma_gamma(mass1, mass2, spin1z, spin2z):
    """ Calculate the slal.LAL_PIn corrections for TaylorF2 
        reference -> <http://arxiv.org/pdf/0810.5336v3.pdf>
    """
    M, v = mass1_mass2_to_mtotal_eta(mass1, mass2)
    d = (mass1 - mass2) / (mass1 + mass2)
    xs = .5 * (spin1z+spin2z)
    xa = .5 * (spin1z-spin2z)

    beta = (113/12.0 - 19/3.0 * v) * xs + 113/12.0 * d * xa
    
    sigma = v * (721/48.0 * ((xs)**2 -(xa)**2)-247.0/48*(xs**2-xa**2))
    sigma += (1-2*v)* (719/96.0 * ((xa)**2+(xs)**2) - 233/96.0 * (xs**2 +xa**2))
    sigma += d * (719/48.0 * xs*xa - 233/48.0 * xs * xa)
    
    gamma = (732985/2268.0 - 24260/81.0 * v - 340/9.0 * v**2 ) * xs
    gamma += (732985/2268.0 +140/9.0 * v) * xa * d
    
    return beta, sigma, gamma    

def solar_mass_to_kg(solar_masses):
    return solar_masses * lal.LAL_MSUN_SI

    
def parsecs_to_meters(distance):
    return distance *lal.LAL_PC_SI

def velocity_to_frequency(v, M):
    return v**(3.0) / (float(M) * lal.LAL_MTSUN_SI * lal.LAL_PI)

def frequncy_to_velocity(f, M):
    return (lal.LAL_PI * float(M) * lal.LAL_MTSUN_SI * float(f))**(1.0/3.0)

def schwarzschild_isco(M):
    return velocity_to_frequency( (1.0/6.0)**(0.5), M)

##############################This code was taken from Andy ###########


def _energy_coeffs(m1, m2, chi1, chi2):
    """ Return the center-of-mass energy coefficients up to 3.0pN (2.5pN spin)
    """ 
    mtot = m1 + m2
    eta = m1*m2 / (mtot*mtot)
    chi = (m1*chi1 + m2*chi2) / mtot
    chisym = (chi1 + chi2) / 2.
    beta = (113.*chi - 76.*eta*chisym)/12.
    sigma12 = 79.*eta*chi1*chi2/8.
    sigmaqm = 81.*m1*m1*chi1*chi1/(16.*mtot*mtot) \
            + 81.*m2*m2*chi2*chi2/(16.*mtot*mtot)

    energy0 = -0.5*eta
    energy2 = -0.75 - eta/12.
    energy3 = 0.
    energy4 = -3.375 + (19*eta)/8. - pow(eta,2)/24.
    energy5 = 0.
    energy6 = -10.546875 - (155*pow(eta,2))/96. - (35*pow(eta,3))/5184. \
                + eta*(59.80034722222222 - (205*pow(lal.LAL_PI,2))/96.)

    energy3 += (32*beta)/113. + (52*chisym*eta)/113.
    energy4 += (-16*sigma12)/79. - (16*sigmaqm)/81.
    energy5 += (96*beta)/113. + ((-124*beta)/339. - (522*chisym)/113.)*eta \
                - (710*chisym*pow(eta,2))/339.

    return (energy0, energy2, energy3, energy4, energy5, energy6)

def meco_velocity(m1, m2, chi1, chi2):
    """ Returns the velocity of the minimum energy cutoff for 3.5pN (2.5pN spin)
    """
    m1 = float(m1)
    m2 = float(m2)
    chi1 = float(chi1)
    chi2 = float(chi2)
    energy0, energy2, energy3, energy4, energy5, energy6 = \
        _energy_coeffs(m1, m2, chi1, chi2)
    def eprime(v):
        return 2. + v * v * (4.*energy2 + v * (5.*energy3 \
                + v * (6.*energy4
                + v * (7.*energy5 + 8.*energy6 * v))))
    return bisect(eprime, 0.05, 1.0)

def meco_frequency(m1, m2, chi1, chi2):
    """Returns the frequency of the minimum energy cutoff for 3.5pN (2.5pN spin)
    """
    return velocity_to_frequency(meco_velocity(m1, m2, chi1, chi2), m1+m2)

def _dtdv_coeffs(m1, m2, chi1, chi2):
    """ Returns the dt/dv coefficients up to 3.5pN (2.5pN spin)
    """
    m1 = float(m1)
    m2 = float(m2)
    chi1 = float(chi1)
    chi2 = float(chi2)
    mtot = m1 + m2
    eta = m1*m2 / (mtot*mtot)
    chi = (m1*chi1 + m2*chi2) / mtot
    chisym = (chi1 + chi2) / 2.
    beta = (113.*chi - 76.*eta*chisym)/12.
    sigma12 = 79.*eta*chi1*chi2/8.
    sigmaqm = 81.*m1*m1*chi1*chi1/(16.*mtot*mtot) \
            + 81.*m2*m2*chi2*chi2/(16.*mtot*mtot)

    energy0 = -0.5*eta
    dtdv0 = 1. # FIXME: Wrong but doesn't matter for now.
    dtdv2 = (1./336.) * (743. + 924.*eta)
    dtdv3 = -4. * lal.LAL_PI + beta
    dtdv4 = (3058673. + 5472432.*eta + 4353552.*eta*eta)/1016064. - sigma12 - sigmaqm 
    dtdv5 = (1./672.) * lal.LAL_PI * (-7729. + 1092.*eta) + (146597.*beta/18984. + 42.*beta*eta/113. - 417307.*chisym*eta/18984. - 1389.*chisym*eta*eta/226.)
    dtdv6 = 22.065 + 165.416*eta - 2.20067*eta*eta + 4.93152*eta*eta*eta
    dtdv6log = 1712./315.
    dtdv7 = (lal.LAL_PI/1016064.) * (-15419335. - 12718104.*eta + 4975824.*eta*eta)

    return (dtdv0, dtdv2, dtdv3, dtdv4, dtdv5, dtdv6, dtdv6log, dtdv7)    

def _dtdv_cutoff_velocity(m1, m2, chi1, chi2):
    dtdv0, dtdv2, dtdv3, dtdv4, dtdv5, dtdv6, dtdv6log, dtdv7 = _dtdv_coeffs(m1, m2, chi1, chi2)

    def dtdv_func(v):
        return 1. + v * v * (dtdv2 + v * (dtdv3 \
                + v * (dtdv4
                + v * (dtdv5
                + v * ((dtdv6 + dtdv6log*3.*log(v))
                + v * dtdv7)))))
    if dtdv_func(1.0) < 0.:
        return bisect(dtdv_func, 0.05, 1.0)
    else:
        return 1.0

def t2_cutoff_velocity(m1, m2, chi1, chi2):
    return min(meco_velocity(m1,m2,chi1,chi2), _dtdv_cutoff_velocity(m1,m2,chi1,chi2))
    
def t2_cutoff_frequency(m1, m2, chi1, chi2):
    return velocity_to_frequency(t2_cutoff_velocity(m1, m2, chi1, chi2), m1 + m2)

t4_cutoff_velocity = meco_velocity
t4_cutoff_freqeuncy = meco_frequency