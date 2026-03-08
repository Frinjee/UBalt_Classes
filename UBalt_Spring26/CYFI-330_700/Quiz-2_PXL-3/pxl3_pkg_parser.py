import re
from collections import defaultdict

def parse_xml(f_path):
    with open(f_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    pkgs = re.findall(r'<(?:package|updated-package)\s+([^>]+?)(?:/>|>)', 
                      content, re.DOTALL)

    count = defaultdict(int)
    pkg_details = defaultdict(list)
    
    for pkg_attr in pkgs:
        _name = re.search(r'name="([^"]+)"', pkg_attr)
        _path = re.search(r'codePath="([^"]+)"', pkg_attr)
        _inst = re.search(r'installer(?:Name)?="([^"]+)', pkg_attr)
        
        if not _name:
            continue
        
        name = _name.group(1)
        path = _path.group(1) if _path else ''
        inst = _inst.group(1) if _inst else ''
        
        is_system = any(path.startswith(p) for p in ['/system', 'product', '/vendor',
                        '/apex', 'system', 'product', 'vendor', 'apex'])
        
        is_data = path.startswith('/data') or path.startswith('data')
        
        if is_system:
            if re.match(r'(com\.android\.|android\.|^android$)', name):
                categ = 'aosp_stock'
            else:
                categ = 'preloaded'
        
        elif is_data:
            is_google_pkg = (
                name.startswith('com.google.') or
                name in ('com.android.chrome', 'com.android.vending') or
                name.startswith('com.google.vr.') or
                name.startswith('com.google.intelligence') or
                name.startswith('com.google.audio') or
                name.startswith('com.google.ar')
                )
            
            if inst =='com.android.vending' and is_google_pkg:
                categ = 'google_play'
                
            elif inst not in ('com.android.vending', '') and not is_google_pkg:
                categ = 'sideloaded'
            else:
                categ = 'third_party'
        else:
            categ = 'aosp_stock'
        
        count[categ] += 1
        pkg_details[categ].append((name, inst))
    
    total = sum(count.values())
    
    
    categ_labels = {
        'aosp_stock': 'Pure Stock (AOSP)',
        'preloaded': 'Preloaded OEM/Google/Carrier ("default app")',
        'google_play': 'User Installed GApps updated via Google Play',
        'third_party': 'User Installed Non-Stock Third Party',
        'sideloaded': 'Sideloaded (Not Play Store)',
    }
    print('=' * 83)
    print('{:^65s}'.format('Breakdown of packages.xml'))
    print('{:^65s}'.format('Output File > ./pkg_report.txt'))
    print('=' * 83)
    
    for key, label in categ_labels.items():
        print(f'{label:<45} {count[key]:>4}')
        
    print('-' * 83)
    print(f'{"Total":<45} {total:>4}')
    print('-' * 83)
    
    print('=' * 83)
    print('{:^65s}'.format('[NON-STOCK THIRD PARTY APPS]'))
    print('=' * 83)
    
    for name, inst in pkg_details['third_party']:
        print(f'{name} (installer: {inst})')
    
    print('-' * 83)
    
    print('=' * 83)
    print('{:^65s}'.format('[SIDELOADED APPS]'))
    print('=' * 83)
    
    for name, inst in pkg_details['sideloaded']:
        print(f'{name} (installer: {inst})')
    
    print('-' * 83)
    
    print('=' * 83)
    print('{:^65s}'.format('[Preloaded - OEM|Carrier|Google]'))
    print('=' * 83)
    
    for name, inst in pkg_details['preloaded']:
        print(name)
    print('-' * 83)
    
    print('=' * 83)
    print('{:^65s}'.format('[User Installed (Updated via GAPP Store)]'))
    print('=' * 83)
    for name, inst in pkg_details['google_play']:
        print(f'{name} (installer: {inst})')
    print('-' * 83)
    
    write_to_txt(pkg_details, count, categ_labels)

def write_to_txt(pkg_details, count, categ_labels, out_path='pkg_report.txt'):
    total = sum(count.values())
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('-' * 83 + '\n')
        f.write('{:^65s}\n'.format('[NON-STOCK THIRD PARTY APPS]'))
        f.write('-' * 83 + '\n')
        for name, inst in pkg_details['third_party']:
            f.write(f'{name} (installer: {inst})\n')

        f.write('-' * 83 + '\n')
        f.write('{:^65s}\n'.format('[SIDELOADED APPS]'))
        f.write('-' * 83 + '\n')
        for name, inst in pkg_details['sideloaded']:
            f.write(f'{name} (installer: {inst})\n')

        f.write('-' * 83 + '\n')
        f.write('{:^65s}\n'.format('[Preloaded - OEM|Carrier|Google]'))
        f.write('-' * 83 + '\n')
        for name, inst in pkg_details['preloaded']:
            f.write(name + '\n')
        f.write('-' * 83 + '\n')

        f.write('{:^65s}\n'.format('[User Installed (Updated via GAPP Store)]'))
        f.write('-' * 83 + '\n')
        for name, inst in pkg_details['google_play']:
            f.write(f'{name} (installer: {inst})\n')
        f.write('-' * 83 + '\n')

        f.write('=' * 83 + '\n')
        f.write('{:^65s}\n'.format('Breakdown of packages.xml'))
        f.write('=' * 83 + '\n')
        for key, label in categ_labels.items():
            f.write(f'{label:<45} {count[key]:>4}\n')
        f.write('-' * 83 + '\n')
        f.write(f'{"Total":<45} {total:>4}\n')
        f.write('-' * 83 + '\n')   
    
if __name__ == '__main__':
    parse_xml('./Transferred_Exports/packages.xml')