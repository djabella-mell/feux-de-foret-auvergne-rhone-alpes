"""Indice forêt météo (IFM, en anglais FWI) : méthode canadienne de Van Wagner (1987), version quotidienne.

Entrées quotidiennes : température et humidité relative « de midi », vent (km/h), pluie sur 24 h (mm).
Les données quotidiennes françaises ne donnent pas la valeur de midi : on prend la température maximale et
une humidité de midi estimée (voir humidite_midi). C'est l'approximation usuelle avec des données quotidiennes.
"""
from __future__ import annotations

import math

import numpy as np

# longueur du jour effective (DMC) et facteur de longueur du jour (DC), latitudes tempérées nord
LE = [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0]
LF = [-1.6, -1.6, -1.6, 0.9, 3.8, 5.8, 6.4, 5.0, 2.4, 0.4, -1.6, -1.6]


def pression_saturante(t):
    """Pression de vapeur saturante (hPa), formule de Magnus."""
    return 6.112 * np.exp(17.62 * t / (243.12 + t))


def humidite_midi(hu_moyenne, t_moyenne, t_max):
    """Humidité relative estimée à l'heure la plus chaude, en supposant la vapeur d'eau constante dans la journée."""
    hu = hu_moyenne * pression_saturante(t_moyenne) / pression_saturante(t_max)
    return np.clip(hu, 5, 100)


def _ffmc(t, h, w, r, ffmc0):
    mo = 147.2 * (101 - ffmc0) / (59.5 + ffmc0)
    if r > 0.5:
        rf = r - 0.5
        if mo > 150:
            mo = mo + 42.5 * rf * math.exp(-100 / (251 - mo)) * (1 - math.exp(-6.93 / rf)) \
                 + 0.0015 * (mo - 150) ** 2 * math.sqrt(rf)
        else:
            mo = mo + 42.5 * rf * math.exp(-100 / (251 - mo)) * (1 - math.exp(-6.93 / rf))
        mo = min(mo, 250)
    ed = 0.942 * h ** 0.679 + 11 * math.exp((h - 100) / 10) + 0.18 * (21.1 - t) * (1 - math.exp(-0.115 * h))
    if mo > ed:
        ko = 0.424 * (1 - (h / 100) ** 1.7) + 0.0694 * math.sqrt(w) * (1 - (h / 100) ** 8)
        kd = ko * 0.581 * math.exp(0.0365 * t)
        m = ed + (mo - ed) * 10 ** (-kd)
    else:
        ew = 0.618 * h ** 0.753 + 10 * math.exp((h - 100) / 10) + 0.18 * (21.1 - t) * (1 - math.exp(-0.115 * h))
        if mo < ew:
            k1 = 0.424 * (1 - ((100 - h) / 100) ** 1.7) + 0.0694 * math.sqrt(w) * (1 - ((100 - h) / 100) ** 8)
            kw = k1 * 0.581 * math.exp(0.0365 * t)
            m = ew - (ew - mo) * 10 ** (-kw)
        else:
            m = mo
    return max(0.0, min(101.0, 59.5 * (250 - m) / (147.2 + m)))


def _dmc(t, h, r, dmc0, mois):
    t = max(t, -1.1)
    rk = 1.894 * (t + 1.1) * (100 - h) * LE[mois - 1] * 1e-6
    if r > 1.5:
        re = 0.92 * r - 1.27
        mo = 20 + math.exp(5.6348 - dmc0 / 43.43)
        if dmc0 <= 33:
            b = 100 / (0.5 + 0.3 * dmc0)
        elif dmc0 <= 65:
            b = 14 - 1.3 * math.log(dmc0)
        else:
            b = 6.2 * math.log(dmc0) - 17.2
        mr = mo + 1000 * re / (48.77 + b * re)
        pr = max(244.72 - 43.43 * math.log(mr - 20), 0.0)
    else:
        pr = dmc0
    return max(pr + 100 * rk, 0.0)


def _dc(t, r, dc0, mois):
    t = max(t, -2.8)
    pe = max((0.36 * (t + 2.8) + LF[mois - 1]) / 2, 0.0)
    if r > 2.8:
        rd = 0.83 * r - 1.27
        qo = 800 * math.exp(-dc0 / 400)
        qr = qo + 3.937 * rd
        dr = max(400 * math.log(800 / qr), 0.0)
    else:
        dr = dc0
    return max(dr + pe, 0.0)


def _isi(w, ffmc):
    fm = 147.2 * (101 - ffmc) / (59.5 + ffmc)
    sf = 91.9 * math.exp(-0.1386 * fm) * (1 + fm ** 5.31 / 4.93e7)
    return sf * math.exp(0.05039 * w) * 0.208


def _bui(dmc, dc):
    if dmc <= 0.4 * dc:
        u = 0.8 * dmc * dc / (dmc + 0.4 * dc) if (dmc + 0.4 * dc) > 0 else 0.0
    else:
        u = dmc - (1 - 0.8 * dc / (dmc + 0.4 * dc)) * (0.92 + (0.0114 * dmc) ** 1.7)
    return max(u, 0.0)


def _fwi(isi, bui):
    bb = 0.1 * isi * (0.626 * bui ** 0.809 + 2) if bui <= 80 else 0.1 * isi * (1000 / (25 + 108.64 * math.exp(-0.023 * bui)))
    return math.exp(2.72 * (0.434 * math.log(bb)) ** 0.647) if bb > 1 else bb


def serie_ifm(t, h, w_kmh, r, mois, ffmc0=85.0, dmc0=6.0, dc0=15.0):
    """Calcule jour après jour FFMC, DMC, DC, ISI, BUI et IFM. Les tableaux doivent être triés par date, sans trou."""
    n = len(t)
    sortie = np.full((n, 6), np.nan)
    ffmc, dmc, dc = ffmc0, dmc0, dc0
    for i in range(n):
        if any(np.isnan(v) for v in (t[i], h[i], w_kmh[i], r[i])):
            continue  # on garde les codes de la veille
        ffmc = _ffmc(t[i], h[i], w_kmh[i], r[i], ffmc)
        dmc = _dmc(t[i], h[i], r[i], dmc, mois[i])
        dc = _dc(t[i], r[i], dc, mois[i])
        isi = _isi(w_kmh[i], ffmc)
        bui = _bui(dmc, dc)
        sortie[i] = (ffmc, dmc, dc, isi, bui, _fwi(isi, bui))
    return sortie
