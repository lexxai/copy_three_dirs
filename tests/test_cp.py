import sys

try:
    sys.path.append("./")
    from copy_three_dirs.main import main
except ImportError:
    sys.path.append("../")
    from copy_three_dirs.main import main


if __name__ == "__main__":
    main()
