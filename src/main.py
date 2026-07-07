"""main module"""
import os
import platform
import requests

from tqdm import tqdm

def load_dll_files():
    """Loads necessary DLL files."""
    base_url = ("https://raw.githubusercontent.com/tschoonj/"
                "GTK-for-Windows-Runtime-Environment-Installer/master/gtk-nsis-pack/bin")
    dll_files = [
        'libbrotlicommon.dll', 'libbrotlidec.dll', 'libbz2-1.dll', 'libcairo-2.dll',
        'libcairo-gobject-2.dll', 'libcairo-script-interpreter-2.dll', 'libcairomm-1.0-1.dll',
        'libexpat-1.dll', 'libfontconfig-1.dll', 'libfreetype-6.dll', 'libgcc_s_seh-1.dll',
        'libglib-2.0-0.dll', 'libglibmm-2.4-1.dll', 'libgraphite2.dll', 'libgthread-2.0-0.dll',
        'libharfbuzz-0.dll', 'libiconv-2.dll', 'libintl-8.dll', 'libpcre-1.dll',
        'libpixman-1-0.dll', 'libpng16-16.dll', 'libstdc++-6.dll', 'libwinpthread-1.dll',
        'zlib1.dll'
    ]

    os.makedirs('dlls', exist_ok=True)
    missing_dlls = [dll for dll in dll_files if not os.path.exists(os.path.join('dlls', dll))]

    if missing_dlls:
        print("Downloading missing DLL files...")
        for dll in tqdm(missing_dlls):
            dll_path = os.path.join('dlls', dll)
            url = f"{base_url}/{dll}"
            response = requests.get(url, timeout=5)
            with open(dll_path, 'wb') as file:
                file.write(response.content)

    os.environ['PATH'] = os.path.abspath('dlls') + ';' + os.environ['PATH']

def main():
    """Main function."""
    if platform.system() == "Windows":
        load_dll_files()

    from handlers.command_handler import CommandHandler
    CommandHandler().main()

if __name__ == "__main__":
    main()
