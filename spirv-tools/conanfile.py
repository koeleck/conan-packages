from conans import ConanFile, CMake, tools
from conans.tools import download, unzip, check_sha256
import os, shutil


class SpirvtoolsConan(ConanFile):
    name = 'spirv-tools'
    _revision = 'c430a41ae32c24bfc0ea87aac1bb19526caafb4e'
    version = '2018.0'
    license = 'Apache 2.0'
    url = 'https://github.com/koeleck/conan-packages/tree/master/spirv-tools'
    description = 'SPIRV-Tools package for conan'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'fPIC': [True, False]}
    default_options = 'fPIC=False'
    generators = 'cmake'

    def config_options(self):
        if self.settings.compiler == 'Visual Studio':
            self.options.remove('fPIC')

    def source(self):
        download('https://github.com/KhronosGroup/SPIRV-Tools/archive/v{}.zip'.format(self.version), 'spirv-tools.zip')
        check_sha256('spirv-tools.zip', '55fd0d446a43839abf5fef4ee01fde938b509fe7574dcae66792e1011fbf1a3a')
        unzip('spirv-tools.zip')
        os.unlink('spirv-tools.zip')
        shutil.move('SPIRV-Tools-{}'.format(self.version), 'spirv-tools')

        # SPIRV headers
        spirv_headers_revision = 'ce309203d7eceaf908bea8862c27f3e0749f7d00'
        download('https://github.com/KhronosGroup/SPIRV-Headers/archive/{}.zip'.format(spirv_headers_revision), 'spirv-headers.zip')
        check_sha256('spirv-headers.zip', '5747e7851b3559bb19e35cc2c9262bb3fb2c279b908737fa24e48e4ab9cc9db5')
        unzip('spirv-headers.zip')
        os.unlink('spirv-headers.zip')
        shutil.move('SPIRV-Headers-{}'.format(spirv_headers_revision), 'spirv-headers')

        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file('spirv-tools/CMakeLists.txt', 'project(spirv-tools)', '''project(spirv-tools)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        cmake.definitions['SPIRV_SKIP_EXECUTABLES'] = True
        cmake.definitions['SPIRV-Headers_SOURCE_DIR'] = '{}/spirv-headers'.format(self.source_folder)
        if not self.settings.compiler == 'Visual Studio':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.configure(source_folder='spirv-tools')
        cmake.build()

    def package(self):
        self.copy('license*', dst='.', src='{}/spirv-tools'.format(self.source_folder), ignore_case=True, keep_path=False)
        self.copy('*', dst='include', src='{}/spirv-tools/include'.format(self.source_folder))
        # glslang needs this header (when optimizer is enabled)
        self.copy('message.h', dst='include/spirv-tools', src='{}/spirv-tools/source'.format(self.source_folder), keep_path=False)
        self.copy('*.lib', dst='lib', keep_path=False)
        self.copy('*.dll', dst='bin', keep_path=False)
        self.copy('*.so', dst='lib', keep_path=False)
        self.copy('*.dylib', dst='lib', keep_path=False)
        self.copy('*.a', dst='lib', keep_path=False)

        with open('{}/revision.txt'.format(self.package_folder), 'w') as rev_file:
            rev_file.write(self._revision)

    def package_info(self):
        self.cpp_info.libs = ['SPIRV-Tools', 'SPIRV-Tools-link', 'SPIRV-Tools-opt']
        self.user_info.revision = self._revision

