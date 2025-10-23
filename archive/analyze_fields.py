#!/usr/bin/env python3
"""
Script to analyze the Surescripts Provider Directory field structure.
"""

def analyze_fields():
    """Analyze the field structure of the data file."""
    with open('Surescripts_Provider_Directory_202508.txt', 'r') as f:
        first_line = f.readline().strip()
    
    fields = first_line.split('|')
    
    print("Surescripts Provider Directory Field Analysis")
    print("=" * 50)
    print(f"Total fields: {len(fields)}")
    print()
    
    # Print all fields with their positions
    for i, field in enumerate(fields):
        print(f"Field {i+1:2d}: '{field}'")
    
    print()
    print("Key fields identified:")
    print(f"Field 1  (NPI): {fields[0]}")
    print(f"Field 2  (Entity ID): {fields[1]}")
    print(f"Field 7  (Last Name): {fields[6]}")
    print(f"Field 8  (First Name): {fields[7]}")
    print(f"Field 9  (Middle Name): {fields[8]}")
    print(f"Field 10 (Organization): {fields[9]}")
    print(f"Field 11 (Address 1): {fields[10]}")
    print(f"Field 12 (Address 2): {fields[11]}")
    print(f"Field 13 (City): {fields[12]}")
    print(f"Field 14 (State): {fields[13]}")
    print(f"Field 15 (Zip): {fields[14]}")
    print(f"Field 16 (Country): {fields[15]}")
    print(f"Field 17 (Mailing Address 1): {fields[16]}")
    print(f"Field 18 (Mailing Address 2): {fields[17]}")
    print(f"Field 19 (Mailing City): {fields[18]}")
    print(f"Field 20 (Mailing State): {fields[19]}")
    print(f"Field 21 (Mailing Zip): {fields[20]}")
    print(f"Field 22 (Phone): {fields[21]}")
    print(f"Field 23 (Fax): {fields[22]}")
    print(f"Field 25 (Email): {fields[24]}")
    print(f"Field 26 (Effective Date): {fields[25]}")
    print(f"Field 27 (Expiration Date): {fields[26]}")
    print(f"Field 28 (Message Type): {fields[27]}")
    print(f"Field 30 (Last Updated): {fields[29]}")
    print(f"Field 32 (Status): {fields[31]}")
    print(f"Field 33 (Active): {fields[32]}")
    print(f"Field 34 (Version): {fields[33]}")

if __name__ == "__main__":
    analyze_fields()

