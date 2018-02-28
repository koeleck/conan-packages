#include <glslang/Public/ShaderLang.h>
#include <iostream>

static const char* const shader =
"#version 440 core\n"
"void main() {\n"
"    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);\n"
"}\n";

int main() {
    if (1 != ShInitialize())
        std::terminate();

    int compiler_options = EShMsgRelaxedErrors | EShMsgDebugInfo;
    ShHandle compiler = ShConstructCompiler(EShLangVertex, compiler_options);
    if (!compiler)
        std::terminate();

    TBuiltInResource resources;
    int* const ptr = reinterpret_cast<int*>(&resources);
    for (size_t i = 0; i < sizeof(resources) / sizeof(int); ++i)
        ptr[i] = 3;
    const auto res = ShCompile(compiler,
                               &shader, 1, nullptr,
                               EShOptFull, &resources, 0);
    if (res != 1)
        std::cout << "Error occurred:\n" << ShGetInfoLog(compiler) << '\n';

    ShDestruct(compiler);
    ShFinalize();
}
