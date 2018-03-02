from conans import ConanFile, CMake, tools
import os, errno, glob, re

def _create_directory(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
def _make_empty_file(path):
    parent_dir = os.path.dirname(path)
    _create_directory(parent_dir)
    with open(path, 'w') as _:
        pass

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
        cmake.definitions['BUILD_VLF'] = False
        cmake.definitions['BUILD_VKTRACE'] = False
        cmake.definitions['BUILD_VKTRACE_REPLAY'] = False
        cmake.definitions['CUSTOM_GLSLANG_BIN_ROOT'] = True
        cmake.definitions['CUSTOM_SPIRV_TOOLS_BIN_ROOT'] = True
        cmake.configure(source_folder='VulkanTools')
        cmake.build()

    def package(self):
        self.copy('*.h*', dst='include', src='{}/VulkanTools/submodules/Vulkan-LoaderAndValidationLayers/include'.format(self.source_folder))
        self.copy('vk_dispatch_table_helper.h', dst='include/vulkan', src='{}/submodules/Vulkan-LoaderAndValidationLayers'.format(self.build_folder), keep_path=False)
        self.copy('vk_layer_dispatch_table.h', dst='include/vulkan', src='{}/submodules/Vulkan-LoaderAndValidationLayers'.format(self.build_folder), keep_path=False)

        extra_path = '/{}'.format(self.settings.build_type) if self.settings.os == 'Windows' else ''
        layer_input_paths = ['layersvt', 'submodules/Vulkan-LoaderAndValidationLayers/layers']
        library_input_paths = layer_input_paths + ['submodules/Vulkan-LoaderAndValidationLayers/loader']
        for p in library_input_paths:
            src = '{}/{}{}'.format(self.build_folder, p, extra_path)
            self.copy('*.lib', dst='lib', src=src, keep_path=False, excludes='VKstatic.*')
            self.copy('*.dll', dst='bin', src=src, keep_path=False)
            self.copy('*.so', dst='lib', src=src, keep_path=False)
            self.copy('*.dylib', dst='lib', src=src, keep_path=False)
            self.copy('*.a', dst='lib', src=src, keep_path=False)

        json_dst = '{}/layers.d'.format(self.package_folder)
        _create_directory(json_dst)
        for p in layer_input_paths:
            pattern = '{}/{}{}/*.json'.format(self.build_folder, p, extra_path)
            for json in glob.glob(pattern):
                self._copy_layer_json(dst='{}/{}'.format(json_dst, os.path.basename(json)),
                                      src=json)

        src = '{}/submodules/Vulkan-LoaderAndValidationLayers{}'.format(self.build_folder, extra_path)
        self.copy('*VkLayer_utils.lib', dst='lib', src=src, keep_path=False)
        self.copy('*VkLayer_utils.dll', dst='bin', src=src, keep_path=False)
        self.copy('*VkLayer_utils.so', dst='lib', src=src, keep_path=False)
        self.copy('*VkLayer_utils.dylib', dst='lib', src=src, keep_path=False)
        self.copy('*VkLayer_utils.a', dst='lib', src=src, keep_path=False)


    def package_info(self):
        vulkan_lib = 'vulkan-1' if self.settings.os == 'Windows' else 'vulkan'
        self.cpp_info.libs = [vulkan_lib]
        self.cpp_info.defines = ['VULKAN_TOOLS_VK_LAYER_PATH={}{}layers.d'.format(
                self.cpp_info.rootpath, os.path.sep)]

    # Helper
    def _generate_commit_id_header(self):
        # since we're not using the embedded glslang source, but our own packages:
        # manually generate spirv_tools_commit_id.h and make sure the generator script is not
        # executed
        lvl_dir = '{}/VulkanTools/submodules/Vulkan-LoaderAndValidationLayers'.format(self.source_folder)
        _make_empty_file('{}/scripts/external_revision_generator.py'.format(lvl_dir))
        _make_empty_file('{}/external/glslang/External/spirv-tools/.git/HEAD'.format(lvl_dir))
        _make_empty_file('{}/external/glslang/External/spirv-tools/.git/index'.format(lvl_dir))

        with open('{}/revision.txt'.format(self.deps_cpp_info['spirv-tools'].rootpath), 'r') as rev_file:
            revision = rev_file.readline().strip()
        commit_id_header = '{}/submodules/Vulkan-LoaderAndValidationLayers/spirv_tools_commit_id.h'.format(self.build_folder)
        _create_directory('{}/submodules/Vulkan-LoaderAndValidationLayers/'.format(self.build_folder))
        with open(commit_id_header, 'w') as out_file:
            out_file.write('#pragma once\n#define SPIRV_TOOLS_COMMIT_ID "{}"'.format(revision))

    def _adjust_json_line(self, line):
        match = re.fullmatch(r'^(.*)"library_path":[ \t]*".*?((?:lib|)VkLayer[^"]*)"(.*\n?)$', line)
        if match:
            return '{}"library_path": "..{sep}{}{sep}{}"{}'.format(
                    match.group(1),
                    'bin' if self.settings.os == 'Windows' else 'lib',
                    match.group(2),
                    match.group(3),
                    sep=os.path.sep)
        return line

    def _copy_layer_json(self, *, dst, src):
        with open(dst, 'w') as out_file:
            with open(src, 'r') as in_file:
                for line in in_file:
                    out_file.write(self._adjust_json_line(line))

