#!/usr/bin/env python3
# Script to extract local environments from a list of phonetic transcriptions

import argparse
from itertools import zip_longest
import unicodedata
import csv

# Define characters that should be merged with a sound.
merge_chars = [':']

def main():
    parser = argparse.ArgumentParser(description='Extract phonetic local environments.')
    parser.add_argument('input',help='Input file that contains phonetci transcriptions. Must be one word per line.')
    parser.add_argument('output',help='Output file for environemnts. Will be CSV file, each column a phoneme.')
    parser.add_argument('phonemes', nargs='+',help='Each phoneme to investigate.')
    parser.add_argument('--allow_double', action='store_true', help='Count repeat characters as phonemes of the single character.')
    parser.add_argument('--reverse_sort', action='store_true', help='Sort from the end during output.')

    args = parser.parse_args()

    # Load the words into memory right away.
    words = []
    with open(args.input, 'r') as input_file:
        words = [line.strip() for line in input_file]

    # Dictionary of phonemes. Each one gets a list.
    table = {}
    for phoneme in args.phonemes:
        table[phoneme] = []

    # Loop through each word and phoneme.
    for word in words:
        for p in args.phonemes:
            # Loop through each phoneme in word.
            next_loc = word.find(p)
            loc = 0
            while next_loc != -1:
                loc = next_loc
                next_loc = word.find(p, loc+1)

                # TODO support multiple occurances.

                finish = loc + len(p)

                print(f"{word}: prev: {loc}, next: {finish}")

                # Need character before phoneme, underscore, then the character after.
                # Phonemes may be multiple characters, so need length.
                # TODO need to identify what makes up a phoneme. Dipthongs(?), dicritics(x), long, affricates(x) doubled(x).

                if loc == 0:
                    prev = '#'
                else:
                    # If the previous character is double combining, abort. this is not the phoneme searched for.
                    comb_class = unicodedata.combining(word[loc-1]);
                    if (comb_class == 233 or comb_class == 234):
                        print("ABORT")
                        continue # Exits phoneme loop

                    # If the previous character is the same as the last character in p, this is different. Long consonant.
                    if (not args.allow_double):
                        if word[loc] == word[loc-1]:
                            print("ABORT")
                            continue

                    # Make sure to include all combining characters.
                    prev = word[loc-1]
                    cnt = 1

                    # Include diacritics and any of the merge characters
                    while unicodedata.combining(prev[0]) or (prev[0] in merge_chars):
                        cnt += 1
                        prev = word[loc-cnt:loc]

                if finish == len(word):
                    next = '#'
                else:
                    f_len = 1;

                    # Not the phoneme we are looking for, has diacritics.
                    if unicodedata.combining(word[finish]):
                        print("ABORT")
                        continue # Exits phoneme loop

                    # If the next character is the same as the last character in p, this is different. Long consonant.
                    if (not args.allow_double):
                        if word[finish-1] == word[finish]:
                            print("ABORT")
                            continue

                    while True:
                        if (finish + f_len) >= len(word):
                            break

                        comb_class = unicodedata.combining(word[finish+f_len])
                        if (comb_class == 0) and (word[finish+f_len] not in merge_chars):
                            break

                        # Add the next two characters for double combining, get next character.
                        if (comb_class == 233 or comb_class == 234):
                            f_len += 2
                        else:
                            f_len += 1

                    next = word[finish:finish+f_len]

                    # TODO merge following combining characters.

                environment = prev + '_' + next

                print(f"  {environment}")

                # Don't add if it's already in the table.
                if environment in table[p]:
                    continue

                table[p].append(environment)

    # Sort to make it easier to identify patterns.
    for p in table.keys():
        if args.reverse_sort:
            table[p].sort(key=lambda x: ord(x[-1]))
        else:
            table[p].sort()


    # Output as a csv
    with open(args.output, 'w') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(table.keys())
        writer.writerows(zip_longest(*table.values(), fillvalue=""))



if __name__ == '__main__':
    main()

