"""
Helper script to find Vivado installation and provide setup instructions.
"""

import os
import platform
import subprocess
from pathlib import Path

def find_vivado_windows():
    """Search common Vivado installation locations on Windows."""
    search_paths = [
        Path("C:/Xilinx"),
        Path("D:/Xilinx"),
        Path("E:/Xilinx"),
        Path(os.environ.get("XILINX", "")),
    ]

    vivado_paths = []

    for base in search_paths:
        if not base.exists():
            continue

        # Look for Vivado installations
        for version_dir in base.glob("Vivado/*/"):
            vivado_bat = version_dir / "bin" / "vivado.bat"
            if vivado_bat.exists():
                vivado_paths.append(vivado_bat)

    return vivado_paths

def find_vivado_linux():
    """Search common Vivado installation locations on Linux."""
    search_paths = [
        Path("/tools/Xilinx"),
        Path("/opt/Xilinx"),
        Path.home() / "Xilinx",
    ]

    vivado_paths = []

    for base in search_paths:
        if not base.exists():
            continue

        for version_dir in base.glob("Vivado/*/"):
            vivado_sh = version_dir / "bin" / "vivado"
            if vivado_sh.exists():
                vivado_paths.append(vivado_sh)

    return vivado_paths

def check_vivado_in_path():
    """Check if vivado is already in PATH."""
    try:
        result = subprocess.run(["vivado", "-version"],
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True
    except:
        pass
    return False

def main():
    print("="*80)
    print("Vivado Installation Checker")
    print("="*80)

    # Check if already in PATH
    if check_vivado_in_path():
        print("\n[OK] Vivado is already in your PATH!")
        try:
            result = subprocess.run(["vivado", "-version"],
                                    capture_output=True, text=True)
            print(result.stdout)
        except:
            pass
        return

    print("\n[NOT FOUND] Vivado not found in PATH")
    print("\nSearching for Vivado installations...")

    # Find Vivado
    if platform.system() == "Windows":
        vivado_paths = find_vivado_windows()
    else:
        vivado_paths = find_vivado_linux()

    if vivado_paths:
        print(f"\nFound {len(vivado_paths)} Vivado installation(s):")
        for i, path in enumerate(vivado_paths, 1):
            print(f"  {i}. {path}")

        print("\nTo use Vivado, you need to:")
        if platform.system() == "Windows":
            print("\nOption 1: Add to PATH (PowerShell):")
            for path in vivado_paths[:1]:  # Show first one as example
                print(f'  $env:PATH += ";{path.parent}"')

            print("\nOption 2: Run Vivado settings script before running tests:")
            for path in vivado_paths[:1]:
                settings_path = path.parent.parent / "settings64.bat"
                if settings_path.exists():
                    print(f'  call "{settings_path}"')
        else:
            print("\nOption 1: Source settings script:")
            for path in vivado_paths[:1]:
                settings_path = path.parent.parent / "settings64.sh"
                if settings_path.exists():
                    print(f'  source "{settings_path}"')

    else:
        print("\n[NOT FOUND] No Vivado installations found in common locations.")
        print("\nPlease ensure Vivado is installed and accessible.")
        print("\nCommon installation locations:")
        if platform.system() == "Windows":
            print("  - C:/Xilinx/Vivado/")
            print("  - D:/Xilinx/Vivado/")
        else:
            print("  - /tools/Xilinx/Vivado/")
            print("  - /opt/Xilinx/Vivado/")
            print("  - ~/Xilinx/Vivado/")

    print("\n" + "="*80)

if __name__ == '__main__':
    main()
