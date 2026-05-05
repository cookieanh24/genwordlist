#!/usr/bin/env python3
import itertools
import argparse
import sys
import datetime
import re

def generate_leetspeak(word):
    """Generates comprehensive leetspeak variations."""
    leets = {
        'a': ['a', '@', '4', '^'],
        'b': ['b', '8'],
        'c': ['c', '(', '{', '['],
        'e': ['e', '3'],
        'g': ['g', '9', '6'],
        'i': ['i', '1', '!', '|'],
        'l': ['l', '1', '|', '7'],
        'o': ['o', '0'],
        's': ['s', '$', '5', 'z'],
        't': ['t', '7', '+'],
        'z': ['z', '2']
    }
    
    variations = ['']
    for char in word.lower():
        if char in leets:
            new_variations = []
            for var in variations:
                for leet_char in leets[char]:
                    new_variations.append(var + leet_char)
            # Cap the number of variations per word to avoid memory issues for long words
            if len(new_variations) > 1000:
                variations = new_variations[:1000]
            else:
                variations = new_variations
        else:
            variations = [var + char for var in variations]
    return variations

def generate_cases(word):
    """Generates capitalization variations."""
    cases = set([
        word.lower(),
        word.capitalize(),
        word.upper(),
        word.title(),
    ])
    # Toggle case (e.g. jOHN)
    cases.add(''.join(c.upper() if c.islower() else c.lower() for c in word.capitalize()))
    return list(cases)

def remove_vowels(word):
    """Returns the word with vowels removed."""
    return re.sub(r'[aeiouAEIOU]', '', word)

def generate_wordlist(info):
    words = set()
    
    # --- 1. Base Words Processing ---
    raw_bases = []
    for key in ['first_name', 'last_name', 'nickname', 'pet_name', 'company', 'partner_name', 'child_name']:
        if info.get(key):
            raw_bases.append(info[key].strip())
            
    base_words = set()
    for w in raw_bases:
        # Standard casing
        for cased in generate_cases(w):
            base_words.add(cased)
            base_words.add(cased[::-1]) # Reverse
            
        # Vowel removed versions
        no_vowels = remove_vowels(w)
        if len(no_vowels) > 0:
            for cased in generate_cases(no_vowels):
                base_words.add(cased)
            
        # Double the word (e.g., johnjohn)
        base_words.add(w.lower() + w.lower())
            
        # Leetspeak (run on lowercase)
        for leet in generate_leetspeak(w.lower()):
            base_words.add(leet)
            base_words.add(leet.capitalize())
            base_words.add(leet.upper())

    base_words = list(base_words)

    # --- 2. Dates & Years ---
    dates = []
    years = []
    if info.get('birthdate'):
        bd = info['birthdate'] # DDMMYYYY
        if len(bd) >= 8:
            dd = bd[:2]
            mm = bd[2:4]
            yyyy = bd[4:8]
            yy = bd[6:8]
            
            dates.extend([
                bd,                 # DDMMYYYY
                dd + mm + yy,       # DDMMYY
                mm + dd + yyyy,     # MMDDYYYY
                mm + dd + yy,       # MMDDYY
                yyyy + mm + dd,     # YYYYMMDD
                yy + mm + dd,       # YYMMDD
                dd + mm,            # DDMM
                mm + dd,            # MMDD
            ])
            years.extend([yyyy, yy])
            
            # Formats with separators
            for sep in ['-', '.', '/']:
                dates.extend([
                    f"{dd}{sep}{mm}{sep}{yyyy}",
                    f"{mm}{sep}{dd}{sep}{yyyy}",
                    f"{yyyy}{sep}{mm}{sep}{dd}",
                ])
        elif len(bd) == 4:
            years.append(bd)
            dates.append(bd)
        else:
            dates.append(bd)

    # Extensive year generation (Common birth years + recent years)
    current_year = datetime.datetime.now().year
    years.extend([str(y) for y in range(current_year - 5, current_year + 3)]) # Recent years
    years.extend([str(y) for y in range(1970, 2010)]) # Common birth years

    years = list(set(years))
    dates = list(set(dates))

    # --- 3. Numbers & Padding ---
    numbers = []
    if info.get('favorite_numbers'):
        numbers.extend([n.strip() for n in info['favorite_numbers'].split(',')])
        
    # Standard common numbers and keyboard walks
    numbers.extend([
        '1', '12', '123', '1234', '12345', '123456', '12345678', '123456789',
        '111', '1111', '000', '0000', '69', '420', '666', '888', '999',
        '01', '02', '03', '07', '10', '99', '100', '1337',
        'qwerty', 'asdf', 'qazwsx', 'zxczxc', '1q2w3e'
    ])
    
    # Generate 0-99 as strings
    paddings = [str(i) for i in range(100)] + [f"{i:02d}" for i in range(100)]
    numbers.extend(paddings)
    numbers = list(set(numbers))

    # --- 4. Symbols ---
    symbols = ['!', '@', '#', '$', '%', '&', '*', '?', '_', '-', '.', '!!', '!!!', '!@#', '!@#$', '@123', '!?']
    separators = ['', '_', '.', '-', '@', '#', '*']

    # --- GENERATION LOGIC ---
    
    important_bases = [w for w in base_words if len(w) >= 2]
    
    # 1. Standalone bases
    for w in base_words:
        words.add(w)

    # 2. Combinations of 2 Bases (Name + Name)
    if len(important_bases) > 1:
        # Limit to combinations of raw inputs to prevent exponential explosion with leet
        raw_cases = []
        for w in raw_bases:
            raw_cases.extend(generate_cases(w))
            
        for r in itertools.permutations(raw_cases, 2):
            for sep in separators:
                words.add(sep.join(r))
                # Add year to these combos
                for y in [str(current_year), str(current_year-1)]: 
                    words.add(sep.join(r) + y)

    # 3. Base + Numbers / Dates / Years
    for base in important_bases:
        for extra in dates + numbers + years:
            for sep in separators:
                words.add(base + sep + extra)
                words.add(extra + sep + base)

    # 4. Base + Symbol + Number/Year (e.g., Name@2023, Name!123)
    # We restrict this to just raw base permutations to save memory
    core_bases = []
    for w in raw_bases:
        core_bases.extend(generate_cases(w))
        
    for base in core_bases:
        for sym in symbols:
            # Suffixes
            words.add(base + sym)
            # Prefixes
            words.add(sym + base)
            
            for extra in years + ['123', '1234', '1', '69', '420'] + dates[:10]:
                words.add(base + sym + extra)
                words.add(base + extra + sym)
                words.add(extra + sym + base)

    # --- CLEANUP ---
    final_words = set()
    for w in words:
        w = str(w).strip()
        # Filter for realistic password lengths (usually 4 to 32 chars)
        if 4 <= len(w) <= 32:
            final_words.add(w)
            
    # Sort by length and then alphabetically for a cleaner wordlist
    return sorted(list(final_words), key=lambda x: (len(x), x))

def main():
    parser = argparse.ArgumentParser(description="Ultimate Custom Wordlist Generator (CUPP Alternative).")
    parser.add_argument('-f', '--first-name', help="Target's first name")
    parser.add_argument('-l', '--last-name', help="Target's last name")
    parser.add_argument('-n', '--nickname', help="Target's nickname")
    parser.add_argument('-b', '--birthdate', help="Target's birthdate (Format: DDMMYYYY)")
    parser.add_argument('-p', '--pet-name', help="Target's pet name")
    parser.add_argument('-c', '--company', help="Target's company name")
    parser.add_argument('--partner-name', help="Target's partner's name")
    parser.add_argument('--child-name', help="Target's child's name")
    parser.add_argument('-num', '--favorite-numbers', help="Comma-separated numbers (e.g., 7,42,69)")
    parser.add_argument('-o', '--output', help="Output file to save the wordlist")
    
    args = parser.parse_args()
    
    info = {
        'first_name': args.first_name,
        'last_name': args.last_name,
        'nickname': args.nickname,
        'birthdate': args.birthdate,
        'pet_name': args.pet_name,
        'company': args.company,
        'partner_name': args.partner_name,
        'child_name': args.child_name,
        'favorite_numbers': args.favorite_numbers
    }
    
    if not any(info.values()):
        print("[-] Error: Please provide at least one piece of information.")
        parser.print_help()
        sys.exit(1)
        
    print("[*] Initializing generation of massive wordlist permutations...")
    wordlist = generate_wordlist(info)
    
    if args.output:
        try:
            with open(args.output, 'w') as f:
                for word in wordlist:
                    f.write(word + '\n')
            print(f"[+] SUCCESS! Wordlist generated and saved to {args.output}")
            print(f"[+] Total unique passwords generated: {len(wordlist):,}")
        except Exception as e:
            print(f"[-] Error writing to file: {e}")
    else:
        for word in wordlist:
            print(word)

if __name__ == '__main__':
    main()
