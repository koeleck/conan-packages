from conans import ConanFile, CMake, tools
import os

STATIC_LIBS = ["nvtt", "squish", "rg_etc1", "nvimage", "bc6h", "posh",
               "bc7", "nvmath", "nvthread", "nvcore"]
SHARED_LIBS = ["nvtt", "nvimage", "nvthread", "nvmath", "nvcore"]

class NvidiatexturetoolsConan(ConanFile):
    name = "nvidia-texture-tools"
    version = "662d223626185f7c6c7e0d822a4796a691acc05a"
    license = "MIT"
    author = "koeleck"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "The NVIDIA Texture Tools is a collection of image processing and texture manipulation tools, designed to be integrated in game tools and asset processing pipelines."
    settings = "os", "compiler", "build_type", "arch"
    source_subfolder = "nvtt"
    no_copy_source = True
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "use_OpenMP": [True, False]
    }
    default_options = "shared=False", "fPIC=True", "use_OpenMP=True"
    generators = "cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        url = "https://github.com/castano/nvidia-texture-tools/archive/{}.zip".format(self.version)
        tools.get(url)
        os.rename('nvidia-texture-tools-{}'.format(self.version), self.source_subfolder)
        tools.replace_in_file(os.path.join(self.source_subfolder, "CMakeLists.txt"), "PROJECT(NV)",
                              '''PROJECT(NV)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        cmake.definitions["HAVE_CUDA"] = False
        cmake.definitions["HAVE_OPENMP"] = self.options.use_OpenMP
        cmake.configure(source_folder=self.source_subfolder)
        cmake.build()

    def package(self):
        self.copy("license*", src=self.source_subfolder, ignore_case=True, keep_path=False)
        self.copy("nvtt.h", dst="include/nvtt", src=os.path.join(self.source_subfolder, "src", "nvtt"), keep_path=False)
        self.copy("nvtt_wrapper.h", dst="include/nvtt", src=os.path.join(self.source_subfolder, "src", "nvtt"), keep_path=False)
        if self.options.shared:
            for libname in SHARED_LIBS:
                self.copy("*{}*.dll".format(libname), dst="bin", src=os.path.join(self.build_folder, "bin"), keep_path=False)
                self.copy("*{}*.lib".format(libname), dst="lib", src=os.path.join(self.build_folder, "lib"), keep_path=False)
                self.copy("*{}*.so*".format(libname), dst="lib", src=os.path.join(self.build_folder, "lib"), keep_path=False)
        else:
            for libname in STATIC_LIBS:
                self.copy("*{}*.a".format(libname), dst="lib", src=os.path.join(self.build_folder, "lib"), keep_path=False)
                self.copy("*{}*.lib".format(libname), dst="lib", src=os.path.join(self.build_folder, "lib"), keep_path=False)

    def package_info(self):
        all_libs = tools.collect_libs(self)
        if self.options.shared:
            libs = all_libs
        else:
            libs = []
            for libname in STATIC_LIBS:
                libs += [lib for lib in all_libs if libname in lib]
        self.cpp_info.libs = libs
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["dl", "pthread"])

        if self.options.shared:
            self.cpp_info.defines = ["NVTT_SHARED=1"]
