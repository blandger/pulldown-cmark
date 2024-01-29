# Copyright 2015 Google Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# curl -O https://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt
# Usage: python tools/mk_puncttable.py UnicodeData.txt > src/puncttable.rs

import sys

def get_bits(high, punct):
    b = 0
    for i in range(16):
        if high * 16 + i in punct:
            b |= 1 << i
    return b

def main(args):
    ascii_punct = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    ascii_set = set((ord(c) for c in ascii_punct))

    punct = set()
    for line in open(args[1]):
        spl = line.split(';')
        if spl[2] in ('Pc', 'Pd', 'Pe', 'Pf', 'Pi', 'Po', 'Ps', 'Sm', 'Sc', 'Sk', 'So'):
            punct.add(int(spl[0], 16))
    pshift = list(set((cp // 16 for cp in punct if cp >= 128)))
    pshift.sort()
    bits = [get_bits(high, punct) for high in pshift]
    print("""// Copyright 2015 Google Inc. All rights reserved.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

//! CommonMark punctuation set based on spec and Unicode properties.

// Autogenerated by mk_puncttable.py

const PUNCT_MASKS_ASCII: [u16; 8] = [""")
    for x in range(8):
        y = get_bits(x, ascii_set)
        print('    0x%04x, // U+%04X...U+%04X' % (y, x * 16, x * 16 + 15))
    print("""];

const PUNCT_TAB: [u16; %i] = [""" % len(pshift))
    for x in pshift:
        print('    %-5s // U+%04X...U+%04X' % (str(x)+",", x * 16, x * 16 + 15))
    print("""];

const PUNCT_MASKS: [u16; %i] = [""" % len(pshift))
    for i, y in enumerate(bits):
        x = pshift[i]
        print('    0x%04x, // U+%04X...U+%04X' % (y, x * 16, x * 16 + 15))
    print("""];

pub(crate) fn is_ascii_punctuation(c: u8) -> bool {
    c < 128 && (PUNCT_MASKS_ASCII[(c / 16) as usize] & (1 << (c & 15))) != 0
}

pub(crate) fn is_punctuation(c: char) -> bool {
    let cp = c as u32;
    if cp < 128 {
        return is_ascii_punctuation(cp as u8);
    }
    if cp > 0x%04X {
        return false;
    }
    let high = (cp / 16) as u16;
    match PUNCT_TAB.binary_search(&high) {
        Ok(index) => (PUNCT_MASKS[index] & (1 << (cp & 15))) != 0,
        _ => false,
    }
}

#[cfg(test)]
mod tests {
    use super::{is_ascii_punctuation, is_punctuation};

    #[test]
    fn test_ascii() {
        assert!(is_ascii_punctuation(b'!'));
        assert!(is_ascii_punctuation(b'@'));
        assert!(is_ascii_punctuation(b'~'));
        assert!(!is_ascii_punctuation(b' '));
        assert!(!is_ascii_punctuation(b'0'));
        assert!(!is_ascii_punctuation(b'A'));
        assert!(!is_ascii_punctuation(0xA1));
    }

    #[test]
    fn test_unicode() {
        assert!(is_punctuation('~'));
        assert!(!is_punctuation(' '));

        assert!(is_punctuation('\\u{00A1}'));
        assert!(is_punctuation('\\u{060C}'));
        assert!(is_punctuation('\\u{FF65}'));
        assert!(is_punctuation('\\u{1BC9F}'));
        assert!(!is_punctuation('\\u{1BCA0}'));
    }
}""" % max(punct))

main(sys.argv)
