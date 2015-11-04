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
from qgis.core import (
    QgsVectorFileWriter, QgsFields, QGis, QgsFeature, QgsGeometry)

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.ProcessingConfig import ProcessingConfig
from processing.core.ProcessingLog import ProcessingLog
from processing.core.parameters import (
    ParameterVector, ParameterNumber, ParameterTableField, ParameterBoolean
)
from processing.core.outputs import OutputVector, OutputNumber
from processing.tools import dataobjects, vector

import numpy as np
from scipy.stats import gamma, uniform

from anon_utils import DifferentialPrivacyUtils


class DifferentialPrivacyAlgorithm(GeoAlgorithm):
    """
    Differential Privacy algorithm implementing the method outlined in:

    Andrés, M.E. et al., 2013. Geo-indistinguishability. In the 2013 ACM SIGSAC
    conference. New York, New York, USA: ACM Press, pp. 901–914.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT_LAYER = 'OUTPUT_LAYER'
    INPUT_LAYER = 'INPUT_LAYER'
    PROTECTION_DISTANCE = 'PROTECTION_DISTANCE'
    NINETY_FIVE_DISTANCE = 'NINETY_FIVE_DISTANCE'
    LIMIT_NINETY_FIVE = 'LIMIT_NINETY_FIVE'

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

        self.addParameter(ParameterBoolean(
            self.LIMIT_NINETY_FIVE,
            "Limit the distance moved to the 95% confidence interval",
            default=False
        ))

        # We add a vector layer as output
        self.addOutput(OutputVector(self.OUTPUT_LAYER,
            self.tr('Anonymized features')))

        self.addOutput(OutputNumber(
            self.NINETY_FIVE_DISTANCE,
            "95% confidence distance for offset"
        ))

    def processAlgorithm(self, progress):
        """Here is where the processing itself takes place."""

        # The first thing to do is retrieve the values of the parameters
        # entered by the user
        inputFilename = self.getParameterValue(self.INPUT_LAYER)
        radius = float(self.getParameterValue(
            self.PROTECTION_DISTANCE))

        base_epsilon = float(ProcessingConfig.getSetting(
            DifferentialPrivacyUtils.DIFFERENTIAL_EPSILON))

        limit_nine_five = self.getParameterValue(self.LIMIT_NINETY_FIVE)

        # scale should be 1 / epsilon where epsilon is some base epsilon constant / chosen radius
        r_generator = gamma(2., scale=radius / base_epsilon)
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

        nine_five_distance = r_generator.ppf(0.95)

        features = vector.features(vectorLayer)
        for f in features:
            r = r_generator.rvs()
            if limit_nine_five and r > nine_five_distance:
                r = nine_five_distance
            theta = theta_generator.rvs()

            g = f.geometryAndOwnership()
            g.translate(np.cos(theta) * r, np.sin(theta) * r)
            f.setGeometry(g)

            writer.addFeature(f)

        ProcessingLog.addToLog(
            ProcessingLog.LOG_INFO,
            "95% confiedence distance: {}".format(nine_five_distance)
        )

        self.setOutputValue(self.NINETY_FIVE_DISTANCE, nine_five_distance)


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


class DisplacementLines(GeoAlgorithm):
    """
    Algorithm for visualising the movement of points displaced.

    Takes two input point layers with ID columns which should match, and builds
    lines between points with matching IDs.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT_LAYER = 'OUTPUT_LAYER'
    BASE_LAYER = 'BASE_LAYER'
    DISPLACED_LAYER = 'DISPLACED_LAYER'
    BASE_ID_FIELD = 'BASE_ID_FIELD'
    DISPLACED_ID_FIELD = 'DISPLACED_ID_FIELD'

    def getIcon(self):
        """Get the icon.
        """
        return DifferentialPrivacyUtils.getIcon()

    def defineCharacteristics(self):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The name that the user will see in the toolbox
        self.name = 'Displacement Lines'

        # The branch of the toolbox under which the algorithm will appear
        self.group = 'Vector'

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument
        self.addParameter(ParameterVector(
            self.BASE_LAYER,
            self.tr('Base layer'),
            [ParameterVector.VECTOR_TYPE_POINT],
            False
        ))

        self.addParameter(ParameterTableField(
            self.BASE_ID_FIELD,
            self.tr('Base layer ID field'),
            self.BASE_LAYER
        ))

        self.addParameter(ParameterVector(
            self.DISPLACED_LAYER,
            self.tr('Displaced layer'),
            [ParameterVector.VECTOR_TYPE_POINT],
            False
        ))

        self.addParameter(ParameterTableField(
            self.DISPLACED_ID_FIELD,
            self.tr('Displaced layer ID field'),
            self.DISPLACED_LAYER
        ))

        # We add a vector layer as output
        self.addOutput(OutputVector(self.OUTPUT_LAYER,
            self.tr('Displacement lines')))

    def processAlgorithm(self, progress):
        """Here is where the processing itself takes place."""

        # The first thing to do is retrieve the values of the parameters
        # entered by the user
        base_filename = self.getParameterValue(self.BASE_LAYER)
        displaced_filename = self.getParameterValue(self.DISPLACED_LAYER)

        output = self.getOutputValue(self.OUTPUT_LAYER)

        # Input layers vales are always a string with its location.
        # That string can be converted into a QGIS object (a
        # QgsVectorLayer in this case) using the
        # processing.getObjectFromUri() method.
        base_layer = dataobjects.getObjectFromUri(base_filename)
        displayed_layer = dataobjects.getObjectFromUri(displaced_filename)

        # And now we can process

        # First, get the ID field index for each layer

        base_id_idx = base_layer.fieldNameIndex(self.getParameterValue(
            self.BASE_ID_FIELD
        ))
        displaced_id_idx = displayed_layer.fieldNameIndex(self.getParameterValue(
            self.DISPLACED_ID_FIELD
        ))

        # Grab the ID field and drop it in a fields object for the output.

        fields = QgsFields()
        fields.append(
            displayed_layer.fields()[displaced_id_idx]
        )

        # Displaced points

        features = vector.features(displayed_layer)
        displaced_points = {
            f[displaced_id_idx]: f.geometry().asPoint()
            for f in features
        }

        # Base points

        features = vector.features(base_layer)
        base_points = {
            f[base_id_idx]: f.geometry().asPoint()
            for f in features
        }

        # Build the output layer
        settings = QSettings()
        systemEncoding = settings.value('/UI/encoding', 'System')
        provider = displayed_layer.dataProvider()
        writer = QgsVectorFileWriter(
            output, systemEncoding, fields, QGis.WKBLineString, provider.crs())

        # Loop over the displayed points and build the line that links them to
        # the base points

        for id, endpoint in displaced_points.iteritems():

            try:
                startpoint = base_points[id]
            except KeyError:
                ProcessingLog.addToLog(
                    ProcessingLog.LOG_WARNING,
                    "Couldn't find input feature with ID {}".format(
                        id
                    )
                )
            else:
                feature = QgsFeature()
                feature.setGeometry(QgsGeometry.fromPolyline(
                    [startpoint, endpoint]))
                feature.setAttributes([id, ])

                writer.addFeature(feature)


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
            "displacement_lines.html"
        )).read()

        return True, help_data
