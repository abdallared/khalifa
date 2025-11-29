"""
WhatsApp Provider Switcher
Easily switch between WPPConnect and Elmujib Cloud API
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace') if hasattr(sys.stdout, 'reconfigure') else None


def read_settings_file():
    """Read settings.py file"""
    settings_path = os.path.join(os.path.dirname(__file__), 'khalifa_pharmacy', 'settings.py')
    with open(settings_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_settings_file(content):
    """Write settings.py file"""
    settings_path = os.path.join(os.path.dirname(__file__), 'khalifa_pharmacy', 'settings.py')
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)


def get_current_driver():
    """Get current WHATSAPP_DRIVER value"""
    content = read_settings_file()
    for line in content.split('\n'):
        if line.strip().startswith('WHATSAPP_DRIVER'):
            if 'wppconnect' in line.lower():
                return 'wppconnect'
            elif 'elmujib' in line.lower():
                return 'elmujib_cloud'
            elif 'cloud_api' in line.lower():
                return 'cloud_api'
    return 'unknown'


def switch_driver(new_driver):
    """Switch to new driver"""
    content = read_settings_file()
    lines = content.split('\n')
    
    new_lines = []
    for line in lines:
        if line.strip().startswith('WHATSAPP_DRIVER'):
            # Replace the driver value
            new_lines.append(f"WHATSAPP_DRIVER = '{new_driver}'")
        else:
            new_lines.append(line)
    
    new_content = '\n'.join(new_lines)
    write_settings_file(new_content)


def main():
    print("="*70)
    print("  WhatsApp Provider Switcher")
    print("  Khalifa Pharmacy System")
    print("="*70)
    
    current = get_current_driver()
    print(f"\nCurrent Provider: {current}")
    
    print("\nAvailable Providers:")
    print("  1. wppconnect    - Self-hosted WPPConnect (Local server)")
    print("  2. elmujib_cloud - Elmujib Cloud Business API (Recommended)")
    print("  3. cloud_api     - Meta WhatsApp Business API")
    print("  4. Cancel")
    
    choice = input("\nSelect provider (1-4): ").strip()
    
    driver_map = {
        '1': 'wppconnect',
        '2': 'elmujib_cloud',
        '3': 'cloud_api'
    }
    
    if choice == '4':
        print("\nCancelled.")
        return
    
    if choice not in driver_map:
        print("\nInvalid choice.")
        return
    
    new_driver = driver_map[choice]
    
    if new_driver == current:
        print(f"\nAlready using {new_driver}. No change needed.")
        return
    
    print(f"\nSwitching from '{current}' to '{new_driver}'...")
    
    # Confirm
    confirm = input(f"Confirm switch to {new_driver}? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        try:
            switch_driver(new_driver)
            print(f"\n✓ Successfully switched to {new_driver}")
            print(f"\nIMPORTANT: Restart your Django server for changes to take effect:")
            print(f"  1. Stop the current server (Ctrl+C)")
            print(f"  2. Run: python manage.py runserver")
        except Exception as e:
            print(f"\n✗ Error switching provider: {str(e)}")
    else:
        print("\nCancelled.")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    main()
