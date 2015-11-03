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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Henry Walshaw'
__date__ = '2015-11-02'
__copyright__ = '(C) 2015 by Henry Walshaw'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DifferentialPrivacy class from file DifferentialPrivacy.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .anon_methods import DifferentialPrivacyPlugin
    return DifferentialPrivacyPlugin()
