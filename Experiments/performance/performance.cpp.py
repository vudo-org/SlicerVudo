
"""


# Mac

export PY=/Users/s/python-install/bin/PythonSlicer
export experimentPath="/SlicerVudo/Experiments/performance/performance.cpp.py"

${PY} /Users/pieper/nac/${experimentPath}

# Windows - start slicer local build, put this in console

experimentPath = "/SlicerVudo/Experiments/performance/"
exec(open("c:/pieper"+experimentPath+"performance.cpp.py").read())


"""


print("Starting...")
# standard imports
import numpy
import os
import subprocess
import time
import timeit

# project specific imports
import cppyy

print("setting up...")
# vulkan SDK
if os.name == 'nt':
  vulkanSDKDir = "c:/VulkanSDK/1.1.130.0"
  experimentPath = "/SlicerVudo/Experiments/performance/"
  sourceDir = "c:/pieper"+experimentPath
  glslCompilerPath = vulkanSDKDir+"/bin/glslangValidator.exe"
  vulkanSharedLibrary = "vulkan-1.dll"
  vulkanSDKIncludeDir = vulkanSDKDir + "/Include"
  vulkanSDKLibDir = vulkanSDKDir + "/Lib"
else:
  # mac
  vulkanSDKDir = "/Users/pieper/nac/vulkan/vulkansdk-macos-1.1.126.0/macOS"
  sourceDir = "/Users/pieper"+experimentPath
  glslCompilerPath = vulkanSDKDir+"/bin/glslangValidator"
  vulkanSharedLibrary = "libvulkan.dylib"
  vulkanSDKIncludeDir = vulkanSDKDir + "/include"
  vulkanSDKLibDir = vulkanSDKDir + "/lib"


# project paths
cppSourcePath = sourceDir+"/performance.cpp"
shaderSourcePath = sourceDir+"/performance.comp.glsl"
shaderSPIRVPath = sourceDir+"/performance.spv"

## shader compilation
print("compiling glsl...")
compileCommand = glslCompilerPath + " -V " + shaderSourcePath + " -o " + shaderSPIRVPath
subprocess.run(compileCommand.split())

# cpp compilation
print("compiling cpp...")
performanceCppSource = open(cppSourcePath).read()
namepaceTag = "cppyy_"+str(time.time()).replace(".", "_")
performanceCppSource = performanceCppSource.replace("%%_NAMESPACE_TAG_%%", namepaceTag) 
cppyy.add_include_path(vulkanSDKIncludeDir)
cppyy.add_library_path(vulkanSDKLibDir)
cppyy.load_library(vulkanSharedLibrary)
cppyy.cppdef(performanceCppSource)

# import and use the code
print("running...")
print("import...")
exec("from cppyy.gbl import " + namepaceTag)
namespace = eval("cppyy.gbl." + namepaceTag)
print("instance...")
vudo = namespace.performanceVudo()
vudo.shaderSPIRVPath = shaderSPIRVPath
# TODO: put this in a thread 
print("run...")
time = timeit.timeit(vudo.run, number=1)
print(f"Time for vudo.run is: {time}")

# get the rendered image as a numpy array
print("data access...")
imageView = vudo.renderedImage()
imageView.reshape((vudo.bufferSize,))
print("Buffer size is %d" % vudo.bufferSize)
print(f"pixel size in bytes: {vudo.bufferSize/vudo.WIDTH/vudo.HEIGHT/vudo.DEPTH}")
imageArray = numpy.frombuffer(imageView, dtype=numpy.float32, count=int(vudo.bufferSize/4))
imageArray = imageArray.reshape((vudo.WIDTH, vudo.HEIGHT, vudo.DEPTH, 4))
scalarVolumeArray = numpy.empty((vudo.WIDTH, vudo.HEIGHT, vudo.DEPTH))
scalarVolumeArray = imageArray[:,:,:,0]

time = timeit.timeit(lambda : print(scalarVolumeArray.mean()), number=1)
print(f"Time to compute mean: {time}")

print("Updating volume...")
try:
  vudoVolume = slicer.util.getNode("VudoVolume")
  slicer.util.updateVolumeFromArray(vudoVolume, scalarVolumeArray)
except slicer.util.MRMLNodeNotFoundException:
  volumeNode = slicer.util.addVolumeFromArray(scalarVolumeArray, name="VudoVolume")
  slicer.util.setSliceViewerLayers(background=volumeNode)

print("Cleaning up...")
imageView = None
imageArray = None
vudo.cleanup()
del vudo

print("Done")
