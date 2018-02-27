from conans import ConanFile, CMake, tools
from conans.tools import download, unzip, check_sha256
import os, shutil

class VulkantoolsConan(ConanFile):
    name = 'VulkanTools'
    version = '1.0.68.0'
    license = 'Apache 2.0'
    url = 'https://github.com/koeleck/conan-packages/tree/master/VulkanTools'
    description = 'LunarG Vulkan SDK'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False]}
    default_options = 'shared=False'
    generators = 'cmake'

    def source(self):
        revision = '2fbb616a7fe0230b3255cd0c5307fcd8551f3b1d'
        #download('https://github.com/LunarG/VulkanTools/archive/sdk-{}.zip'.format(self.version), 'sdk.zip')
        #check_sha256('sdk.zip', '4bb35ed5334a443e43bf3abfc06701724218cbe1b0fa80d87cc3fdd76d4c746f')
        #unzip('sdk.zip')
        #os.unlink('sdk.zip')
        #unzip('D:\\Downloads\\tmp\\VulkanTools-sdk-1.0.68.0.zip')
        #shutil.move('VulkanTools-sdk-{}'.format(self.version), 'sdk')
        self.run('git clone https://github.com/LunarG/VulkanTools.git')
        self.run('cd VulkanTools && git reset --hard {} && git submodule init && git submodule update'.format(revision))

        self.run('cd VulkanTools && .{}update_external_sources.{} --no-build'.format(os.path.sep,
                 'bat' if self.settings.os == 'Windows' else 'sh'))
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file('VulkanTools/CMakeLists.txt', 'project (VULKAN_TOOLS)', '''project (VULKAN_TOOLS)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        update_cmd = 'cd {}/VulkanTools && .{}update_external_sources.{} --no-sync --glslang'.format(self.source_folder,
                os.path.sep, 'bat' if self.settings.os == 'Windows' else 'sh')
        if self.settings.os == 'Windows':
            if self.settings.compiler == 'Visual Studio':
                vcvars = tools.vcvars_command(self.settings)
                update_cmd = '{} && {}'.format(vcvars, update_cmd)
            update_cmd += ' --32' if self.settings.arch == 'x86' else ' --64'
            update_cmd += ' --debug' if self.settings.build_type == 'Debug' else ' --release'
        self.run(update_cmd)
        cmake = CMake(self)
        cmake.configure(source_folder='VulkanTools')
        cmake.build()

    def package(self):
        self.copy('*.h', dst='include', src='hello')
        self.copy('*hello.lib', dst='lib', keep_path=False)
        self.copy('*.dll', dst='bin', keep_path=False)
        self.copy('*.so', dst='lib', keep_path=False)
        self.copy('*.dylib', dst='lib', keep_path=False)
        self.copy('*.a', dst='lib', keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['hello']
