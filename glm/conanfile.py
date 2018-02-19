from conans import ConanFile, tools
from conans.tools import download, unzip, check_sha256
import os


class GlmConan(ConanFile):
    name = 'glm'
    version = '0.9.8.5'
    license = 'MIT'
    url = 'https://github.com/koeleck/conan-packages/tree/master/glm'
    description = 'GLM package for conan'

    def source(self):
        zip_file = 'glm-{}.zip'.format(self.version)
        download('https://github.com/g-truc/glm/releases/download/{}/{}'.format(self.version, zip_file), zip_file)
        check_sha256(zip_file, '9f9f520ec7fb8c20c69d6b398ed928a2448c6a3245cbedb8631a56a987c38660')
        unzip(zip_file)
        os.unlink(zip_file)

        # Fix for newer gcc versions
        tools.replace_in_file('{}/glm/glm/simd/platform.h'.format(self.source_folder), '(__GNUC__ == 7) && (__GNUC_MINOR__ == 2)',
                '(__GNUC__ == 7) && (__GNUC_MINOR__ >= 2)')


    def package(self):
        glm_dir = '{}/glm'.format(self.source_folder)
        self.copy('copying*', dst='.', src=glm_dir, ignore_case=True, keep_path=False)
        self.copy('*', dst='include/glm', src='{}/glm'.format(glm_dir))

