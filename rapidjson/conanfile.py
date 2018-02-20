from conans import ConanFile, CMake, tools
from conans.tools import download, check_sha256, unzip
import os

class JsonConan(ConanFile):
    name = 'json'
    version = '1.1.0'
    license = 'MIT, BSD'
    url = '<Package recipe repository url here, for issues about the package>'
    description = '<Description of Json here>'

    def source(self):
        zip_file = 'v{}.zip'.format(self.version)
        download('https://github.com/Tencent/rapidjson/archive/{}'.format(zip_file), zip_file)
        check_sha256(zip_file, '8e00c38829d6785a2dfb951bb87c6974fa07dfe488aa5b25deec4b8bc0f6a3ab')
        unzip(zip_file)
        os.unlink(zip_file)

    def package(self):
        self.copy('*', dst='include', src='{}/rapidjson-{}/include'.format(self.source_folder, self.version))

