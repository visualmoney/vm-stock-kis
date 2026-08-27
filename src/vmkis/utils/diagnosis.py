import importlib.metadata as metadata
import platform

import vmkis


def check():
    uname = platform.uname()

    print(f"Version: VmKis/{vmkis.__version__}")
    print(f"Python: {platform.python_implementation()} {platform.python_version()}")
    print(f"System: {uname.system} {uname.version} [{uname.machine}]")
    print()
    print("Installed Packages:", end=" ")

    try:
        requires = metadata.distribution(vmkis.__package_name__).requires

        if not requires:
            print("No Dependencies")
        else:
            print()

            for package in requires:
                package, version = package.rsplit("=", 1)
                package, operator = package[:-1], package[-1]
                left = (30 - len(package)) // 2
                right = 30 - len(package) - left

                print(
                    f"{'=' * left} {package} {'=' * right}\nRequired: {version}{operator}=\nInstalled: ",
                    end="",
                )

                try:
                    print(metadata.version(package))
                except metadata.PackageNotFoundError:
                    print("Not Found")

    except metadata.PackageNotFoundError:
        print("Package Not Found")
        return

    print("=" * 32)

    print()


if __name__ == "__main__":
    check()
