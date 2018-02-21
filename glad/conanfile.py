from conans import ConanFile, CMake, tools
from conans.tools import download, check_sha256, unzip
import os

class GladConan(ConanFile):
    name = 'glad'
    version = '0.1.16a0'
    license = 'MIT'
    url = 'https://github.com/koeleck/conan-packages/tree/master/glad'
    description = 'GL/GLES/EGL/GLX/WGL Loader-Generator based on the official specs.'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'profile': ['core', 'compatibility'],
               'api': 'ANY',
               'generator': ['c', 'c-debug'],
               'extensions': 'ANY',
               'spec': ['gl', 'egl', 'glx', 'wgl']
              }
    default_options = '''profile=core
api=gl=3.3
generator=c
extensions=
spec=gl'''
    generators = 'cmake'

    def source(self):
        zip_file = 'v{}.zip'.format(self.version)
        download('https://github.com/Dav1dde/glad/archive/{}'.format(zip_file), zip_file)
        check_sha256(zip_file, 'f3a897fff3ecbdf189fbaa1a605686615accda7d28a6ef947b79e3e2003de610')
        unzip(zip_file)
        os.unlink(zip_file)
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file('glad-{}/CMakeLists.txt'.format(self.version), 'project(GLAD)', '''project(GLAD)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        defs = {'GLAD_PROFILE': self.options.profile,
                'GLAD_API': self.options.api,
                'GLAD_GENERATOR': self.options.generator,
                'GLAD_EXTENSIONS': self.options.extensions,
                'GLAD_SPEC': self.options.spec
               }
        cmake = CMake(self)
        cmake.configure(source_folder='glad-{}'.format(self.version), defs=defs)
        cmake.build()

    def package(self):
        self.copy('*.h', dst='include', src='{}/include'.format(self.build_folder))
        self.copy('*.lib', dst='lib', keep_path=False)
        self.copy('*.a', dst='lib', keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['glad']
        if self.settings.os == 'Linux':
            self.cpp_info.libs.append('dl')
