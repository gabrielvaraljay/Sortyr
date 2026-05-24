from setuptools import setup

APP = ['app.py']
DATA_FILES = ['config.json']
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.icns',  # Create if missing
    'plist': {
        'CFBundleName': 'Sortyr',
        'CFBundleDisplayName': 'Sortyr',
        'CFBundleIdentifier': 'com.gabrielvaraljay.sortyr',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '12.0',
    },
    'packages': ['PIL', 'tkinter'],
    'includes': ['objc', 'Vision', 'Quartz', 'Foundation'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)