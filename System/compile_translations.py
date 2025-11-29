"""
Simple script to compile .po files to .mo files using polib
"""
import polib
from pathlib import Path


def main():
    base_dir = Path(__file__).parent
    locale_dir = base_dir / 'locale'
    
    for lang_dir in locale_dir.iterdir():
        if lang_dir.is_dir():
            lc_messages = lang_dir / 'LC_MESSAGES'
            if lc_messages.exists():
                po_file = lc_messages / 'django.po'
                mo_file = lc_messages / 'django.mo'
                
                if po_file.exists():
                    try:
                        po = polib.pofile(str(po_file))
                        po.save_as_mofile(str(mo_file))
                        print(f"Compiled: {po_file} -> {mo_file}")
                    except Exception as e:
                        print(f"Error compiling {po_file}: {e}")


if __name__ == '__main__':
    main()
