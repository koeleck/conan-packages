from conans import ConanFile, CMake, tools
from conans.tools import download, check_sha256, unzip
import os
from shutil import copyfile

class ImguiConan(ConanFile):
    name = 'imgui'
    version = '1.53'
    license = 'MIT'
    url = '<Package recipe repository url here, for issues about the package>'
    description = '<Description of Imgui here>'
    settings = 'os', 'compiler', 'build_type', 'arch'
    exports = 'CMakeLists.txt'
    generators = 'cmake'

    def source(self):
        zip_file = 'v{}.zip'.format(self.version)
        download('https://github.com/ocornut/imgui/archive/{}'.format(zip_file), zip_file)
        check_sha256(zip_file, '49285711401c4a1c3fdbf5cf1edaf28b11af1a3964bbeb6ecae2f9d4e9ecaab7')
        unzip(zip_file)
        os.unlink(zip_file)
        copyfile('{}/CMakeLists.txt'.format(self.source_folder),
                 'imgui-{}/CMakeLists.txt'.format(self.version))
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file('imgui-{}/CMakeLists.txt'.format(self.version), 'project(imgui)', '''project(imgui)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder='imgui-{}'.format(self.version))
        cmake.build()

    def package(self):
        imgui_dir = '{}/imgui-{}'.format(self.source_folder, self.version)
        self.copy('imgui.h', dst='include/imgui', src=imgui_dir)
        self.copy('imconfig.h', dst='include/imgui', src=imgui_dir)
        self.copy('*.lib', dst='lib', src='{}/lib'.format(self.build_folder), keep_path=False)
        self.copy('*.a', dst='lib', src='{}/lib'.format(self.build_folder), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['imgui']
