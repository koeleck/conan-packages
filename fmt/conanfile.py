from conans import ConanFile, CMake, tools
from conans.tools import download, check_sha256, unzip
import os

class FmtConan(ConanFile):
    name = 'fmt'
    version = '4.1.0'
    license = 'BSD 2-Clause'
    url = 'https://github.com/koeleck/conan-packages/tree/master/fmt'
    description = 'A modern formatting library'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False],
               'header_only': [True, False]
              }
    default_options = 'shared=False', 'header_only=False'
    generators = 'cmake'

    def source(self):
        zip_file = 'fmt-{}.zip'.format(self.version)
        download('https://github.com/fmtlib/fmt/releases/download/{}/{}'.format(self.version, zip_file), zip_file)
        check_sha256(zip_file, '9d49bf02ceb9d0eec51144b203b63b77e69d3798bb402fb82e7d0bdb06c79eeb')
        unzip(zip_file)
        os.unlink(zip_file)
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file('fmt-{}/CMakeLists.txt'.format(self.version), 'project(FMT)', '''project(FMT)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        defs = {'FMT_DOC': False,
                'BUILD_SHARED_LIBS': self.options.shared,
                'FMT_TEST': False
               }
        cmake = CMake(self)
        cmake.configure(source_folder='fmt-{}'.format(self.version), defs=defs)
        cmake.build()

    def package(self):
        src_folder = '{}/fmt-{}'.format(self.source_folder, self.version)

        self.copy('license*', dst='.', src=src_folder, ignore_case=True, keep_path=False)

        self.copy('*.h', dst='include/fmt', src='{}/fmt'.format(src_folder))
        self.copy('*.lib', dst='lib', keep_path=False)
        self.copy('*.dll', dst='lib', keep_path=False)
        self.copy('*.so', dst='lib', keep_path=False)
        self.copy('*.dylib', dst='lib', keep_path=False)
        self.copy('*.a', dst='lib', keep_path=False)

    def package_info(self):
        if self.options.header_only:
            self.cpp_info.defines = ['FMT_HEADER_ONLY=1']
        else:
            self.cpp_info.libs = ['fmt']
