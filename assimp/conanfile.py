from conans import ConanFile, CMake, tools
from conans.tools import download, unzip, check_sha256
import os


class AssimpConan(ConanFile):
    name = 'assimp'
    version = '4.1.0'
    license = 'BSD 3-Clause'
    url = 'https://github.com/assimp/assimp/issues'
    description = 'Conan package for assimp library'
    requires = 'zlib/1.2.11@conan/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    source_subfolder = 'assimp'
    no_copy_source = True
    options = {
        'shared': [True, False],
        'fPIC': [True, False]
    }
    default_options = 'shared=False', 'fPIC=True'
    generators = 'cmake'

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        url = 'https://github.com/assimp/assimp/archive/v{}.zip'.format(self.version)
        tools.get(url, sha256='407be74f44f488fcf1aac3492d962452ddde89561906e917a208c75e1192bcdc')
        os.rename('assimp-{}'.format(self.version), self.source_subfolder)

        tools.replace_in_file(os.path.join(self.source_subfolder, 'CMakeLists.txt'), 'PROJECT( Assimp )', '''PROJECT( Assimp )
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        cmake.definitions['ASSIMP_NO_EXPORT'] = True
        cmake.definitions['ASSIMP_BUILD_ASSIMP_TOOLS'] = False
        cmake.definitions['ASSIMP_BUILD_SAMPLES'] = False
        cmake.definitions['ASSIMP_BUILD_TESTS'] = False
        cmake.definitions['ASSIMP_BUILD_TESTS'] = False
        cmake.definitions['ASSIMP_INSTALL_PDB'] = False
        cmake.configure(source_folder=self.source_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy('license*', src=self.source_subfolder, ignore_case=True, keep_path=False)

    def package_info(self):
        libs = tools.collect_libs(self)
        # Ensure linking order
        libs = [l for l in libs if 'assimp' in l.lower()] + [l for l in libs if 'assimp' not in l.lower()]
        self.cpp_info.libs = libs

