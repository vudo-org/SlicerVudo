import importlib
import logging
import numpy
import os
import subprocess
import sys
import time
import timeit
import unittest

import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *


#
# Vudo
#

class Vudo(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Vudo" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Developer Tools"]
    self.parent.dependencies = []
    self.parent.contributors = ["Steve Pieper (Isomics, Inc.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """Tools for using Vulkan in Slicer
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This Steve Pieper, Isomics, Inc. as part of NAC, a Biomedical Technology Resource Center supported by the National Institute of Biomedical Imaging and Bioengineering (NIBIB) (P41 EB015902)
"""
#
# VudoWidget
#

class VudoWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)
    # Layout within the collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = False
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Volume: ", self.inputSelector)

    #
    # output volume selector
    #
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    self.outputSelector.selectNodeUponCreation = True
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    self.outputSelector.noneEnabled = False
    self.outputSelector.showHidden = False
    self.outputSelector.showChildNodeTypes = False
    self.outputSelector.setMRMLScene( slicer.mrmlScene )
    self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    parametersFormLayout.addRow("Output Volume: ", self.outputSelector)

    #
    # threshold value
    #
    self.imageThresholdSliderWidget = ctk.ctkSliderWidget()
    self.imageThresholdSliderWidget.singleStep = 0.1
    self.imageThresholdSliderWidget.minimum = -100
    self.imageThresholdSliderWidget.maximum = 100
    self.imageThresholdSliderWidget.value = 0.5
    self.imageThresholdSliderWidget.setToolTip("Set threshold value for computing the output image. Voxels that have intensities lower than this value will set to zero.")
    parametersFormLayout.addRow("Image threshold", self.imageThresholdSliderWidget)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

  def onApplyButton(self):
    if not self.confirmInstall():
      slicer.util.errorDisplay("Could not install the needed components")
      return
    logic = VudoLogic()
    imageThreshold = self.imageThresholdSliderWidget.value
    logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), imageThreshold)

  def confirmInstall(self):
    try:
      import cppyy
    except ModuleNotFoundError:
      logging.debug("Did not find cppyy, installing")
      try:
        slicer.util.pip_install("cppyy")
      except subprocess.CalledProcessError:
        logging.error("Can't install cppyy")
        return False
    return True

#
# VudoLogic
#

class VudoLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self):
    import VudoLib, VudoLib.Vudo
    self.VudoModule = importlib.reload(VudoLib.Vudo)


  def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
    """
    Run the actual algorithm
    """
    logging.info('Processing started')

    vudo = self.VudoModule.Vudo()
    TODO = """
    vodo.compileGLSL(self, shaderSourcePath, shaderSPIRVPath)

    vodo.compileAndImportCPP(self, cppSource)
    """

    logging.info('Processing completed')

    return True


class VudoTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_VolumeFilter()

  def test_VolumeFilter(self):
    """
    """

    self.delayDisplay("Starting the test", 50)
    #
    # first, get some data
    #
    import SampleData
    volumeNode = SampleData.downloadSample("MRHead")
    self.assertIsNotNone(volumeNode)

    sourceDir = os.path.split(slicer.modules.vudo.path)[0] + "/../Experiments/performance"
    cppSourcePath = sourceDir+"/performance.cpp"
    shaderSourcePath = sourceDir+"/performance.comp.glsl"
    shaderSPIRVPath = sourceDir+"/performance.spv"

    logic = VudoLogic()
    vudoInstance = logic.VudoModule.Vudo()
    self.delayDisplay("Compiling cpp", 50)
    performanceModule = vudoInstance.compileAndImportCPP(cppSourcePath)
    performanceVudo = performanceModule.PerformanceVudo()
    self.delayDisplay("Compiling glsl", 50)
    vudoInstance.compileGLSL(shaderSourcePath, shaderSPIRVPath)
    performanceVudo.shaderSPIRVPath = shaderSPIRVPath
    # TODO: put this in a thread 
    print("run...")
    time = timeit.timeit(performanceVudo.run, number=1)
    print(f"Time for performanceVudo.run is: {time}")

    # get the rendered image as a numpy array
    print("data access...")
    imageView = performanceVudo.renderedImage()
    imageView.reshape((performanceVudo.bufferSize,))

    print("Buffer size is %d" % performanceVudo.bufferSize)
    print(f"pixel size in bytes: {performanceVudo.bufferSize/performanceVudo.WIDTH/performanceVudo.HEIGHT/performanceVudo.DEPTH}")
    imageArray = numpy.frombuffer(imageView, dtype=numpy.float32, count=int(performanceVudo.bufferSize/4))
    imageArray = imageArray.reshape((performanceVudo.WIDTH, performanceVudo.HEIGHT, performanceVudo.DEPTH, 4))
    scalarVolumeArray = numpy.empty((performanceVudo.WIDTH, performanceVudo.HEIGHT, performanceVudo.DEPTH))
    scalarVolumeArray = imageArray[:,:,:,0]

    time = timeit.timeit(lambda : print(scalarVolumeArray.mean()), number=1)
    print(f"Time to compute mean: {time}")

    print("Updating volume...")
    slicer.util.updateVolumeFromArray(volumeNode, scalarVolumeArray)

    print("Cleaning up...")
    imageView = None
    imageArray = None
    performanceVudo.cleanup()
    del performanceVudo

    print("Done")

    self.delayDisplay('Test passed!')
