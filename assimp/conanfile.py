from conans import ConanFile, CMake, tools
from conans.tools import download, unzip, check_sha256
import os


class AssimpConan(ConanFile):
    name = 'assimp'
    version = '4.1.0'
    license = 'BSD 3-Clause'
    url = '<Package recipe repository url here, for issues about the package>'
    description = 'Conan package for assimp library'
    requires = 'zlib/1.2.11@conan/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False]}
    default_options = 'shared=False'
    generators = 'cmake'

    def source(self):
        zip_file = 'v{}.zip'.format(self.version)
        download('https://github.com/assimp/assimp/archive/{}'.format(zip_file), zip_file)
        check_sha256(zip_file, '407be74f44f488fcf1aac3492d962452ddde89561906e917a208c75e1192bcdc')
        unzip(zip_file)
        os.unlink(zip_file)
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file('assimp-{}/CMakeLists.txt'.format(self.version), 'PROJECT( Assimp )', '''PROJECT( Assimp )
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        defs = {
            'BUILD_SHARED_LIBS': self.options.shared,
            'ASSIMP_BUILD_ASSIMP_TOOLS': False,
            'ASSIMP_BUILD_SAMPLES': False,
            'ASSIMP_BUILD_TESTS': False
        }
        cmake.configure(source_folder='assimp-{}'.format(self.version), defs=defs)
        cmake.build()

    def package(self):
        self.copy('LICENSE', dst='.', src='{}/assimp-{}'.format(self.source_folder, self.version), keep_path=False, ignore_case=True)
        self.copy('*.h', dst='include', src='{}/include'.format(self.build_folder))
        self.copy('*.h', dst='include', src='{}/assimp-{}/include'.format(self.source_folder, self.version))
        self.copy('*.inl', dst='include', src='{}/assimp-{}/include'.format(self.source_folder, self.version))
        self.copy('*.lib', dst='lib', src=self.build_folder, keep_path=False)
        self.copy('*.dll', dst='lib', src=self.build_folder, keep_path=False)
        self.copy('*.so', dst='lib', src=self.build_folder, keep_path=False)
        self.copy('*.dylib', dst='lib', src=self.build_folder, keep_path=False)
        self.copy('*.a', dst='lib', src=self.build_folder, keep_path=False)

    def package_info(self):
        if self.settings.compiler == 'Visual Studio':
            if self.settings.compiler.version == '15':
                msvc_version = 140
            else:
                msvc_version = int(str(self.settings.compiler.version)) * 10
            self.cpp_info.libs = ['assimp-vc{}-mt'.format(msvc_version)]
        else:
            self.cpp_info.libs = ['assimp']
        if not self.options.shared:
            self.cpp_info.libs.append('IrrXML')
