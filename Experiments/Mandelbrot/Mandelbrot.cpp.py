
"""


# Mac

export PY=/Users/s/python-install/bin/PythonSlicer
export experimentPath="/SlicerVudo/Experiments/Mandelbrot/Mandelbrot.cpp.py"

${PY} /Users/pieper/nac/${experimentPath}

# Windows - start slicer local build, put this in console

experimentPath = "/SlicerVudo/Experiments/Mandelbrot/"
exec(open("c:/pieper"+experimentPath+"Mandelbrot.cpp.py").read())


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
  experimentPath = "/SlicerVudo/Experiments/Mandelbrot/"
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
cppSourcePath = sourceDir+"/Mandelbrot.cpp"
shaderSourcePath = sourceDir+"/Mandelbrot.comp.glsl"
shaderSPIRVPath = sourceDir+"/Mandelbrot.spv"

## shader compilation
print("compiling glsl...")
compileCommand = glslCompilerPath + " -V " + shaderSourcePath + " -o " + shaderSPIRVPath
subprocess.run(compileCommand.split())

# cpp compilation
print("compiling cpp...")
mandelbrotCppSource = open(cppSourcePath).read()
mandelbrotCppSource = mandelbrotCppSource.replace("%%_SPV_FILE_PATH_%%", '"'+shaderSPIRVPath+'"')
namepaceTag = "cppyy_"+str(time.time()).replace(".", "_")
mandelbrotCppSource = mandelbrotCppSource.replace("%%_NAMESPACE_TAG_%%", namepaceTag) 
cppyy.add_include_path(vulkanSDKIncludeDir)
cppyy.add_library_path(vulkanSDKLibDir)
cppyy.load_library(vulkanSharedLibrary)
cppyy.cppdef(mandelbrotCppSource)

# import and use the code
print("running...")
exec("from cppyy.gbl import " + namepaceTag)
namespace = eval("cppyy.gbl." + namepaceTag)
vudo = namespace.MandelbrotVudo()
# TODO: put this in a thread 
time = timeit.timeit(vudo.run, number=1)
print(f"Time for vudo.run is: {time}")

# get the rendered image as a numpy array
print("data access...")
imageView = vudo.renderedImage()
imageView.reshape((vudo.bufferSize,))
imageArray = numpy.frombuffer(imageView, dtype=numpy.float32, count=int(vudo.bufferSize/4))
imageArray = imageArray.reshape((vudo.WIDTH, vudo.HEIGHT, vudo.DEPTH, 4))
scalarVolumeArray = imageArray[:,:,:,0]
print("Buffer size is %d" % vudo.bufferSize)

print(scalarVolumeArray.shape)
print(scalarVolumeArray.min())
print(scalarVolumeArray.mean())
print(scalarVolumeArray.max())

try:
  vudoVolume = slicer.util.getNode("VudoVolume")
  slicer.util.updateVolumeFromArray(vudoVolume, scalarVolumeArray)
except slicer.util.MRMLNodeNotFoundException:
  slicer.util.addVolumeFromArray(scalarVolumeArray, name="VudoVolume")

print("Cleaning up")
imageView = None
imageArray = None
vudo.cleanup()
del vudo

print("Done")
