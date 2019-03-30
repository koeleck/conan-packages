from conans import ConanFile, CMake, tools
import os

class MeshoptimizerConan(ConanFile):
    name = "meshoptimizer"
    version = "0.11"
    license = "MIT"
    author = "koeleck"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "Optimized triangle meshes for GPU rendering"
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True
    source_subfolder = 'meshoptimizer'
    options = {"fPIC": [True, False]}
    default_options = "fPIC=True"
    generators = "cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        url = "https://github.com/zeux/meshoptimizer/archive/v{}.tar.gz".format(self.version)
        tools.get(url)
        os.rename('meshoptimizer-{}'.format(self.version), self.source_subfolder)

        tools.replace_in_file(os.path.join(self.source_subfolder, "CMakeLists.txt"), "project(meshoptimizer)",
                              '''project(meshoptimizer)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self.source_subfolder)
        cmake.build()

    def package(self):
        self.copy("*.h", dst="include", src=os.path.join(self.source_subfolder, "src"), keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        libs = tools.collect_libs(self)

