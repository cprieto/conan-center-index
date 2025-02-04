from os import path
from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.files import get, apply_conandata_patches, export_conandata_patches, rmdir, copy, collect_libs
from conan.tools.layout import basic_layout
from conan.tools.gnu import PkgConfigDeps


class CriterionConan(ConanFile):
    name = "criterion"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Snaipe/Criterion"
    topics = ("testing")
    description = "A cross-platform C and C++ unit testing framework for the 21st century"

    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    requires = ("libgit2/1.5.0", "libffi/3.4.3")

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):        
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.compiler.rm_safe("libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        pc = PkgConfigDeps(self)
        pc.generate()

        tc = MesonToolchain(self)
        tc.project_options['force_fallback_for'] = ['boxfort', 'debugbreak', 'klib']
        tc.project_options['default_library'] = 'shared' if self.options['shared'] else 'static'
        
        # We don't need tests or samples
        tc.project_options['tests'] = False
        tc.project_options['samples'] = False
        tc.project_options['localedir'] = 'res/locale'
        
        tc.generate()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        meson = Meson(self)
        meson.install()

        copy(self, "LICENSE", src=self.source_folder, dst=path.join(self.package_folder, 'licenses'))
        rmdir(self, path.join(self.package_folder, "lib", "pkgconfig"))

        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.resdirs = ["res"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ['anl']

    def build_requirements(self):
        self.tool_requires("pkgconf/1.9.3")
        self.tool_requires("meson/1.0.0")
