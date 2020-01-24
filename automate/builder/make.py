from .builder import BaseBuilder


class MakefileBuilder(BaseBuilder):
    def configure(self, c):
        self._mkbuilddir()
        c.run(f"rsync --delete {self.srcdir} {self.builddir}")

    def build(self, c):
        with c.cd(str(self.builddir)):
            c.run(
                f"make CC={cc} CXX={cxx} CFLAGS={cflags} CXXFLAGS={cxxflags} LDFLAGS={ldflags}"
            )

    def install(self, c):
        """Do nothing"""

    def deploy(self, c):
        with c.cd(str(self.builddir)):
            c.run("make")
