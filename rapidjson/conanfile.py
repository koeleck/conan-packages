from conans import ConanFile, CMake, tools
from conans.tools import download, check_sha256, unzip
import os

class RapidJSONConan(ConanFile):
    name = 'rapidjson'
    version = '1.1.0'
    license = 'MIT, BSD'
    url = 'https://github.com/koeleck/conan-packages/tree/master/rapidjson'
    description = 'A fast JSON parser/generator for C++ with both SAX/DOM style API'

    def source(self):
        zip_file = 'v{}.zip'.format(self.version)
        download('https://github.com/Tencent/rapidjson/archive/{}'.format(zip_file), zip_file)
        check_sha256(zip_file, '8e00c38829d6785a2dfb951bb87c6974fa07dfe488aa5b25deec4b8bc0f6a3ab')
        unzip(zip_file)
        os.unlink(zip_file)

    def package(self):
        src_folder = '{}/rapidjson-{}'.format(self.source_folder, self.version)
        self.copy('license*', dst='.', src=src_folder, ignore_case=True, keep_path=False)
        self.copy('*', dst='include', src='{}/include'.format(src_folder))

