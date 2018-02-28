from conans import ConanFile, CMake, tools
from conans.tools import download, unzip, check_sha256
import os, shutil, errno

def _create_directory(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

class VulkantoolsConan(ConanFile):
    name = 'VulkanTools'
    version = '1.0.68.0'
    license = 'Apache 2.0'
    url = 'https://github.com/koeleck/conan-packages/tree/master/VulkanTools'
    description = 'LunarG Vulkan SDK'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False]}
    default_options = 'shared=False'
    requires = 'glslang/2651cca@koeleck/testing' # pulls in spirv-tools
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
        self.run('cd VulkanTools/submodules/jsoncpp && python amalgamate.py')

        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file('VulkanTools/CMakeLists.txt', 'project (VULKAN_TOOLS)', '''project (VULKAN_TOOLS)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(NO_OUTPUT_DIRS)''')

    def build(self):
        # fix problem with missing glsl sources:
        self._generate_commit_id_header()

        cmake = CMake(self)
        cmake.definitions['BUILD_TESTS'] = False
        cmake.definitions['BUILD_DEMOS'] = False
        cmake.definitions['BUILD_VIA'] = False
        cmake.definitions['CUSTOM_GLSLANG_BIN_ROOT'] = True
        cmake.definitions['CUSTOM_SPIRV_TOOLS_BIN_ROOT'] = True
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

    # Helper
    def _generate_commit_id_header(self):
        # since we're not using the embedded glslang source, but our own packages:
        # manually generate spirv_tools_commit_id.h and make sure the generator script is not
        # executed
        with open('{}/VulkanTools/submodules/Vulkan-LoaderAndValidationLayers/scripts/external_revision_generator.py'.format(self.source_folder), 'w') as fp:
            pass # truncate
        with open('{}/revision.txt'.format(self.deps_cpp_info['spirv-tools'].rootpath), 'r') as rev_file:
            revision = rev_file.read()
        print('spirv-tools revision: {}'.format(revision))
        commit_id_header = '{}/submodules/Vulkan-LoaderAndValidationLayers/spirv_tools_commit_id.h'.format(self.build_folder)
        _create_directory('{}/submodules/Vulkan-LoaderAndValidationLayers/'.format(self.build_folder))
        with open(commit_id_header, 'w') as out_file:
            out_file.write('#pragma once\n#define SPIRV_TOOLS_COMMIT_ID "{}"'.format(revision))