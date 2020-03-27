import cppyy
import os
import subprocess
import time

class Vudo(object):

  def __init__(self):

    # vulkan SDK
    # TODO: generalize
    if os.name == 'nt':
      self.vulkanSDKDir = "c:/VulkanSDK/1.1.130.0"
      self.glslCompilerPath = self.vulkanSDKDir+"/bin/glslangValidator.exe"
      self.vulkanSharedLibrary = "vulkan-1.dll"
      self.vulkanSDKIncludeDir = self.vulkanSDKDir + "/Include"
      self.vulkanSDKLibDir = self.vulkanSDKDir + "/Lib"
    else:
      # mac
      self.vulkanSDKDir = "/Users/pieper/nac/vulkan/vulkansdk-macos-1.1.126.0/macOS"
      self.glslCompilerPath = self.vulkanSDKDir+"/bin/glslangValidator"
      self.vulkanSharedLibrary = "libvulkan.dylib"
      self.vulkanSDKIncludeDir = self.vulkanSDKDir + "/include"
      self.vulkanSDKLibDir = self.vulkanSDKDir + "/lib"

    cppyy.add_include_path(self.vulkanSDKIncludeDir)
    cppyy.add_library_path(self.vulkanSDKLibDir)
    cppyy.load_library(self.vulkanSharedLibrary)

  def compileGLSL(self, shaderSourcePath, shaderSPIRVPath):
    compileCommand = self.glslCompilerPath + " -V " + shaderSourcePath + " -o " + shaderSPIRVPath
    completedProcess = subprocess.run(compileCommand.split())
    return completedProcess.returncode == 0

  def compileAndImportCPP(self, cppSourcePath):
    cppSource = open(cppSourcePath).read()
    namepaceTag = "cppyy_"+str(time.time()).replace(".", "_")
    cppSource = cppSource.replace("%%_NAMESPACE_TAG_%%", namepaceTag) ;#TODO: better method?
    cppyy.cppdef(cppSource)

    exec("from cppyy.gbl import " + namepaceTag)
    namespace = eval("cppyy.gbl." + namepaceTag)
    return namespace
