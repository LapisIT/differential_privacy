# -*- coding: utf-8 -*-

"""
/***************************************************************************
 DifferentialPrivacy
                                 A QGIS plugin
 Methods for anonymizing data for public distribution
                              -------------------
        begin                : 2015-11-02
        copyright            : (C) 2015 by Henry Walshaw
        email                : henry.walshaw@spatialvision.com.au
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Henry Walshaw'
__date__ = '2015-11-02'
__copyright__ = '(C) 2015 by Henry Walshaw'

import os.path

from PyQt4.QtGui import QIcon

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'


class DifferentialPrivacyUtils(object):

    DIFFERENTIAL_EPSILON = 'DIFFERENTIAL_EPSILON'


    @staticmethod
    def getIcon():
        return QIcon(os.path.join(
            os.path.dirname(__file__),
            'icons',
            'toucan.png'
        ))
