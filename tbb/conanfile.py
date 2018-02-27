from conans import ConanFile, tools
from conans.tools import download, unzip, check_sha256
import os, shutil


class TBBConan(ConanFile):
    name = 'TBB'
    version = '2018_U2'
    license = 'Apache 2.0'
    homepage = 'https://www.threadingbuildingblocks.org'
    description = '''Intel Threading Building Blocks (Intel TBB) lets you easily write parallel C++ programs 
    that take full advantage of multicore performance, that are portable and composable, and that have future-proof scalability
    '''
    url = 'https://github.com/conan-community/conan-tbb'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False]}
    # TBB by default is a special case, it strongly recommends SHARED
    default_options = 'shared=True'

    def configure(self):
        if not self.options.shared:
            if self.settings.os == 'Windows':
                raise Exception('Intel-TBB does not support static linking in Windows')
            else:
                self.output.warn('Intel-TBB strongly discourage usage of static linkage')

    def source(self):
        download('https://github.com/01org/tbb/archive/{}.zip'.format(self.version), 'tbb.zip')
        check_sha256('tbb.zip', '37f77ed2099e63304c2190a288943356b65de01dbdb39bea8ceb7d47cca36486')
        unzip('tbb.zip')
        os.unlink('tbb.zip')
        shutil.move('tbb-{}'.format(self.version), 'tbb')

    def build(self):
        extra='' if self.options.shared else 'extra_inc=big_iron.inc'
        arch='ia32' if self.settings.arch=='x86' else 'intel64'
        if self.settings.compiler == 'Visual Studio':
            vcvars = tools.vcvars_command(self.settings)
            if tools.which('mingw32-make'):
                self.run('{} && cd {}\\tbb && mingw32-make arch={} {}'.format(vcvars, self.source_folder, arch, extra))
            else:
                raise Exception('This package needs mingw32-make in the path to build')
        else:
            self.run('cd {}/tbb && make arch={} {}'.format(self.source_folder, arch, extra))

    def package(self):
        self.copy('*.h', 'include/tbb', 'tbb/include/tbb')
        build_folder = 'tbb/build/'
        build_type = 'debug' if self.settings.build_type == 'Debug' else 'release'
        self.copy('*{}*.lib'.format(build_type), 'lib', build_folder, keep_path=False)
        self.copy('*{}*.a'.format(build_type), 'lib', build_folder, keep_path=False) 
        self.copy('*{}*.dll'.format(build_type), 'bin', build_folder, keep_path=False)
        self.copy('*{}*.dylib'.format(build_type), 'lib', build_folder, keep_path=False)

        if self.settings.os == 'Linux':
            # leaving the below line in case MacOSX build also produces the same bad libs
            extension = 'dylib' if self.settings.os == 'Macos' else 'so'
            if self.options.shared:
                self.copy('*{}*.{}.*'.format(build_type, extension), 'lib', build_folder, keep_path=False)
                outputlibdir = os.path.join(self.package_folder, 'lib')
                os.chdir(outputlibdir)
                for fpath in os.listdir(outputlibdir):
                    self.run('ln -s \'{}\' \'{}\''.format(fpath, fpath[0:fpath.rfind('.' + extension)+len(extension)+1]))

    def package_info(self):
        if self.settings.build_type == 'Debug':
            self.cpp_info.libs.extend(['tbb_debug', 'tbbmalloc_debug'])
            if self.options.shared:
                self.cpp_info.libs.extend(['tbbmalloc_proxy_debug'])
        else:
            self.cpp_info.libs.extend(['tbb', 'tbbmalloc'])
            if self.options.shared:
                self.cpp_info.libs.extend(['tbbmalloc_proxy'])

        if not self.options.shared and self.settings.os != 'Windows':
            self.cpp_info.libs.extend(['pthread'])
