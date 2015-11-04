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

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os.path

from PyQt4.QtCore import QSettings
from qgis.core import QgsVectorFileWriter

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.ProcessingConfig import ProcessingConfig
from processing.core.ProcessingLog import ProcessingLog
from processing.core.parameters import (
    ParameterVector, ParameterNumber
)
from processing.core.outputs import OutputVector
from processing.tools import dataobjects, vector

import numpy as np
from scipy.stats import gamma, uniform

from anon_utils import DifferentialPrivacyUtils


class DifferentialPrivacyAlgorithm(GeoAlgorithm):
    """This is an example algorithm that takes a vector layer and
    creates a new one just with just those features of the input
    layer that are selected.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the GeoAlgorithm class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT_LAYER = 'OUTPUT_LAYER'
    INPUT_LAYER = 'INPUT_LAYER'
    PROTECTION_DISTANCE = 'PROTECTION_DISTANCE'

    def getIcon(self):
        """Get the icon.
        """
        return DifferentialPrivacyUtils.getIcon()

    def defineCharacteristics(self):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The name that the user will see in the toolbox
        self.name = 'Differential Privacy - independent points'

        # The branch of the toolbox under which the algorithm will appear
        self.group = 'Vector'

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument
        self.addParameter(ParameterVector(self.INPUT_LAYER,
            self.tr('Input layer'), [ParameterVector.VECTOR_TYPE_POINT], False))

        self.addParameter(ParameterNumber(
            self.PROTECTION_DISTANCE,
            self.tr('Protection distance (projected units)'),
            minValue=0.,
            default=500
        ))

        # We add a vector layer as output
        self.addOutput(OutputVector(self.OUTPUT_LAYER,
            self.tr('Anonymized features')))

    def processAlgorithm(self, progress):
        """Here is where the processing itself takes place."""

        # The first thing to do is retrieve the values of the parameters
        # entered by the user
        inputFilename = self.getParameterValue(self.INPUT_LAYER)
        radius = float(self.getParameterValue(
            self.PROTECTION_DISTANCE))

        base_epsilon = float(ProcessingConfig.getSetting(
            DifferentialPrivacyUtils.DIFFERENTIAL_EPSILON))
        epsilon = base_epsilon / radius

        r_generator = gamma(2., scale=1. / epsilon)
        theta_generator = uniform(scale=2 * np.pi)

        output = self.getOutputValue(self.OUTPUT_LAYER)

        # Input layers vales are always a string with its location.
        # That string can be converted into a QGIS object (a
        # QgsVectorLayer in this case) using the
        # processing.getObjectFromUri() method.
        vectorLayer = dataobjects.getObjectFromUri(inputFilename)

        # And now we can process

        # First we create the output layer. The output value entered by
        # the user is a string containing a filename, so we can use it
        # directly
        settings = QSettings()
        systemEncoding = settings.value('/UI/encoding', 'System')
        provider = vectorLayer.dataProvider()
        writer = QgsVectorFileWriter(output, systemEncoding,
                                     provider.fields(),
                                     provider.geometryType(), provider.crs())

        # Now we take the features from input layer and add them to the
        # output. Method features() returns an iterator, considering the
        # selection that might exist in layer and the configuration that
        # indicates should algorithm use only selected features or all
        # of them
        features = vector.features(vectorLayer)
        for f in features:
            r = r_generator.rvs()
            theta = theta_generator.rvs()

            g = f.geometryAndOwnership()
            g.translate(np.cos(theta) * r, np.sin(theta) * r)
            f.setGeometry(g)

            writer.addFeature(f)

        ProcessingLog.addToLog(
            ProcessingLog.LOG_INFO,
            "95% confiedence distance: {}".format(
                np.around(r_generator.ppf(0.95), - int(np.log10(radius)))
            )
        )

        # There is nothing more to do here. We do not have to open the
        # layer that we have created. The framework will take care of
        # that, or will handle it if this algorithm is executed within
        # a complex model


    def help(self):
        """
        Get the help documentation for this algorithm.
        :return: Help text is html from string, the help html
        :rtype: bool, str
        """
        help_data = open(os.path.join(
            os.path.dirname(__file__),
            "doc",
            "independent_points.html"
        )).read()

        return True, help_data
