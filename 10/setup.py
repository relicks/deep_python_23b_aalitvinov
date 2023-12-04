from setuptools import Extension, setup

module = Extension(
    name="cjson",
    sources=["./src/cjson/cjsonmodule.cpp"],
    include_dirs=["./include"],
    language="c++",
)


def main():
    setup(
        name="cjson",
        version="0.1.0",
        author="Alexander Litvinov",
        ext_modules=[module],
    )


if __name__ == "__main__":
    main()
