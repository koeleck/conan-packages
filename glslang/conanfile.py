from conans import ConanFile, CMake, tools
from conans.tools import download, unzip, check_sha256
import os, shutil

class GlslangConan(ConanFile):
    name = "glslang"
    version = "2651cca"
    license = "3-Clause BSD"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "glslang package for conan "
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    requires = 'spirv-tools/2018.0@koeleck/testing'

    def source(self):
        revision = '2651ccaec8170b3257642b3c438f50dc4f181fdd'
        download('https://github.com/KhronosGroup/glslang/archive/{}.zip'.format(revision), 'glslang.zip')
        check_sha256('glslang.zip', 'ad0950a61247ca66526e5f6fd3684dd6d7502083e9751871a7b4ea40d06400da')
        unzip('glslang.zip')
        os.unlink('glslang.zip')
        shutil.move('glslang-{}'.format(revision), 'glslang')
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly.
        # Also: Define target 'SPIRV-Tools-opt' to enable the optimization passes
        tools.replace_in_file("glslang/CMakeLists.txt", "project(glslang)", '''project(glslang)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
add_library(SPIRV-Tools-opt INTERFACE)
target_link_libraries(SPIRV-Tools-opt INTERFACE CONAN_PKG::spirv_tools)
target_include_directories(SPIRV-Tools-opt INTERFACE "${CONAN_INCLUDE_DIRS_SPIRV-TOOLS}/spirv-tools")''')

    def build(self):
        cmake = CMake(self)
        cmake.definitions['ENABLE_GLSLANG_BINARIES'] = False
        cmake.configure(source_folder="glslang")
        cmake.build()

    def package(self):
        base_dir = '{}/glslang'.format(self.source_folder)
        self.copy("*.h*", dst="include/glslang", src="{}/glslang/".format(base_dir))
        self.copy("*.h*", dst="include/SPIRV", src="{}/SPIRV/".format(base_dir))
        self.copy("*.h*", dst="include/hlsl", src="{}/hlsl/".format(base_dir))
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['glslang',
                              'HLSL',
                              'OGLCompiler',
                              'OSDependent',
                              'SPIRV',
                              'SPVRemapper']
        if not self.settings.os == 'Windows':
            self.cpp_info.libs.append('pthread')
