#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AquaCrop crop growth model

import os
import shutil
import sys
import math
import gc

import pcraster as pcr

import VirtualOS as vos
import Meteo as meteo
import C02
import Groundwater as groundwater
import CropParameters as cropParams
import SoilAndTopoParameters as soilParams
import InitialConditions as initCond

import logging
logger = logging.getLogger(__name__)

class AquaCrop(object):

    def __init__(self, configuration, currTimeStep, initialState = None):

        self._configuration = configuration
        self._modelTime = currTimeStep

        # clone map, land mask
        pcr.setclone(configuration.cloneMap)
        self.cloneMap = configuration.cloneMap
        self.landmask = vos.readPCRmapClone(configuration.globalOptions['landmask'],
                                            configuration.cloneMap,
                                            configuration.tmpDir,
                                            configuration.globalOptions['inputDir'],
                                            True)
        attr = vos.getMapAttributesALL(self.cloneMap)
        self.nLat = int(attr['rows'])
        self.nLon = int(attr['cols'])
        
        # Prepare sub-models
        self.meteo = meteo.Meteo(
            self._configuration,
            self.landmask,
            initialState)

        self.C02 = CO2.C02(
            self._configuration,
            self.landmask,
            initialState)
        
        self.groundwater = groundwater.Groundwater(
            self._configuration,
            self.landmask,
            initialState)

        self.soilwater = soilwater.SoilWater(
            self._configuration,
            self.landmask,
            initialState)

        self.landcover = landcover.LandCover(
            self._configuration,
            self.landmask,
            initialState)
        
    @property
    def configuration(self):
        return self._configuration

    def dumpState(self, outputDirectory, specific_date_string = None):

        if specific_date_string is None:
            specific_date_string = str(self._modelTime.fulldate)

        state = self.getState()
        groundwater_state = state['groundwater']
        for var in groundwater_state.iterItems():
            fn = self.outNCDir+"/"+str(var)+specific_date_string+".npy"
            np.save(fn, groundwater_state[var])
        
        soil_water_state = state['soil_water']
        for var in soil_water_state.iterItems():
            fn = self.outNCDir+"/"+str(var)+specific_date_string+".npy"
            np.save(fn, soil_water_state[var])
        
        crop_state = state['crop']
        for var in crop_state.iterItems():
            fn = self.outNCDir+"/"+str(var)+specific_date_string+".npy"
            np.save(fn, crop_state[var])
        
    def resume(self):
        pass

    def setState(self):
        logger.error("cannot set state")

    def getState(self):
        result = {}
        result['groundwater'] = self.groundwater.getState()
        result['soilwater'] = self.soilwater.getState()
        result['landcover'] = self.landcover.getState()
        return result

    def getPseudoState(self):
        pass

    def getAllState(self):
        pass

    def read_forcings(self):
        """Function to read model forcing data for current time step
        """
        logger.info("Reading forcings for time %s", self._modelTime)
        self.meteo.read_forcings(self._modelTime)
        self.groundwater.read_forcings(self._modelTime)
        self.C02.read_forcings(self._modelTime)

    def update(self, meteo, currTimeStep):
        """Function to update model state for current time step"""

        # Update forcing data
        self.read_forcings()

        # Update crop parameters for currently grown crops
        self.crop.update()

        




