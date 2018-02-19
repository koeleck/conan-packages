from conans import ConanFile, CMake, tools
from conans.tools import download, unzip, check_sha256
import os


class GlfwConan(ConanFile):
    name = 'glfw'
    version = '3.2.1'
    license = 'zlib/libpng'
    url = 'https://github.com/koeleck/conan-packages/glfw'
    description = 'GLFW package for conan'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False]}
    default_options = 'shared=False'
    generators = 'cmake'

    def source(self):
        zip_file = 'glfw-{}.zip'.format(self.version)
        download('https://github.com/glfw/glfw/releases/download/{}/{}'.format(self.version, zip_file), zip_file)
        check_sha256(zip_file, 'b7d55e13e07095119e7d5f6792586dd0849c9fcdd867d49a4a5ac31f982f7326')
        unzip(zip_file)
        os.unlink(zip_file)
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file('glfw-{}/CMakeLists.txt'.format(self.version), 'project(GLFW C)', '''project(GLFW C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        defs = {
                'BUILD_SHARED_LIBS': self.options.shared,
                'GLFW_BUILD_DOCS': False,
                'GLFW_BUILD_EXAMPLES': False,
                'GLFW_BUILD_TESTS': False
        }
        if self.settings.compiler == 'Visual Studio':
            defs['USE_MSVC_RUNTIME_LIBRARY_DLL'] = str(self.settings.compiler.runtime).startswith('MD')

        cmake = CMake(self)
        cmake.configure(source_folder='glfw-{}'.format(self.version), defs=defs)
        cmake.build()

    def package(self):
        glfw_dir = '{}/glfw-{}'.format(self.source_folder, self.version)
        self.copy('copying*', dst='.', src=glfw_dir, ignore_case=True, keep_path=False)
        self.copy('*.h', dst='include', src='{}/include'.format(glfw_dir))
        self.copy('*.lib', dst='lib', keep_path=False)
        self.copy('*.dll', dst='lib', keep_path=False)
        self.copy('*.so', dst='lib', keep_path=False)
        self.copy('*.dylib', dst='lib', keep_path=False)
        self.copy('*.a', dst='lib', keep_path=False)

    def package_info(self):
        if self.options.shared:
            self.cpp_info.defines.append('GLFW_DLL')
        if self.settings.os == 'Windows':
            if self.options.shared:
                self.cpp_info.libs = ['glfwdll']
            else:
                self.cpp_info.libs = ['glfw3']
        else:
            if self.options.shared:
                self.cpp_info.libs = ['glfw']
            else:
                self.cpp_info.libs = ['glfw3']
                if self.settings.os == 'Linux':
                    self.cpp_info.libs.extend(['dl', 'rt', 'm',
                        'X11', 'pthread', 'Xrandr', 'Xinerama',
                        'Xxf86vm', 'Xcursor'])
