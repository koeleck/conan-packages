from conans import ConanFile, CMake, tools
from conans.tools import download, check_sha256, unzip
import os

class JsoncppConan(ConanFile):
    name = 'jsoncpp'
    version = '1.8.4'
    license = 'MIT'
    url = 'https://github.com/koeleck/conan-packages/tree/master/jsoncpp'
    description = 'A C++ library for interacting with JSON.'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False]}
    default_options = 'shared=False'
    generators = 'cmake'

    def source(self):
        zip_file = '{}.zip'.format(self.version)
        download('https://github.com/open-source-parsers/jsoncpp/archive/{}'.format(zip_file), zip_file)
        check_sha256(zip_file, '2979436dbd4c48a3284dca9fa8f212298425ba3920ed6bacdda8905a94b111a8')
        unzip(zip_file)
        os.unlink(zip_file)
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file('jsoncpp-{}/CMakeLists.txt'.format(self.version), 'PROJECT(jsoncpp)', '''PROJECT(jsoncpp)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        defs = {'JSONCPP_WITH_PKGCONFIG_SUPPORT': False,
                'BUILD_SHARED_LIBS': self.options.shared,
                'BUILD_STATIC_LIBS': not self.options.shared
               }
        cmake = CMake(self)
        cmake.configure(source_folder='jsoncpp-{}'.format(self.version), defs=defs)
        cmake.build()

    def package(self):
        src_folder = '{}/jsoncpp-{}'.format(self.source_folder, self.version)
        lib_folder = '{}/lib'.format(self.build_folder)

        self.copy('license*', dst='.', src=src_folder, ignore_case=True, keep_path=False)
        self.copy('*.h', dst='include', src=src_folder)
        self.copy('*.lib', dst='lib', src=lib_folder, keep_path=False)
        self.copy('*.dll', dst='lib', src=lib_folder, keep_path=False)
        self.copy('*.so', dst='lib', src=lib_folder, keep_path=False)
        self.copy('*.dylib', dst='lib', src=lib_folder, keep_path=False)
        self.copy('*.a', dst='lib', src=lib_folder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['jsoncpp']
