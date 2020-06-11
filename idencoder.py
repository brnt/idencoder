#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Integer ID Encoder
===================

Python implementation for encoding (usually sequential) integer IDs.

## Algorithm details

A bit-shuffling approach is used to avoid generating consecutive, predictable
values. However, the algorithm is deterministic and will guarantee that no
collisions will occur.

The encoding alphabet is fully customizable and may contain any number of
characters. By default, digits and lower-case letters are used, with
some characters removed to avoid confusion between characters like o, O and 0. The
default alphabet is shuffled and has a prime number of characters to further
improve the results of the algorithm.

The block size specifies how many bits will be shuffled. The lower `BLOCK_SIZE`
bits are reversed. Any bits higher than `BLOCK_SIZE` will remain as is.
`BLOCK_SIZE` of 0 will leave all bits unaffected and the algorithm will simply
be converting your integer to a different base.

## Common usage

The intended use is that incrementing, consecutive integers will be used as
keys to generate the encoded IDs. For example, to create a new short URL (à la
bit.ly), the unique integer ID assigned by a database could be used to generate
the last portion of the URL by using this module. Or a simple counter may be
used. As long as the same integer is not used twice, the same encoded value
will not be generated twice.

The module supports both encoding and decoding of values. The `min_length`
parameter allows you to pad the encoded value if you want it to be a specific
length.

Sample Usage:

```python
>>> import idencoder
>>> x = idencoder.encode(12)
>>> print(x)
LhKA
>>> key = idencoder.decode(x)
>>> print(key)
12
```

Use the functions in the top-level of the module to use the default encoder.
Otherwise, you may create your own `IdEncoder` object and use its `encode()`
and `decode()` methods.

## WARNING ###

If you use this library as part of a production system, **you must generate
your own unique alphabet(s).** One alphabet per encoded entity type is
recommended. Best practice is to configure the alphabet(s) as environment
variables (like you do with credentials, right? ;-)) or to use random alphabets
that are re-randomized each time your application is initialized. The latter
approach will result in different encoded values for the same ID each time your
application is initialized, but this may be acceptable.

For convenience, the library includes a `random_alphabet()` function that you
can use to easily generate these unique alphabets. One easy way is to use the
`-r` flag from the command line:

```sh
$ python idencoder.py -r
Random alphabet: 6nkqyxc4eabmvswfz8d9j5rhp27gt3u
```

And you can, of course, generate random alphabets programmatically:

```python
>>> import idencoder
>>> alpha = idencoder.random_alphabet()
>>> print(alpha)
'c39htkrg5e7mvfn2uwap8sbj6zqdxy4'
```

## Provenance

Original Author: [Michael Fogleman](http://code.activestate.com/recipes/576918/)  
License: [MIT](https://opensource.org/licenses/MIT)  
URL: https://github.com/brnt/idencoder

### Changelog:

2014-05-09 Eric Wald ([@eswald](https://github.com/eswald))
- condensed duplicate bit-scrambling logic
- switched to a native padding function
- removed recursion and extra division
- removed exponentiation and enumeration
- removed excess convenience functions

2014-01-13 Brent Thomson ([@brnt](https://github.com/brnt))
- added `random_alphabet()` function
- replaced `main()` method with a useful one

2013-10-11 Brent Thomson ([@brnt](https://github.com/brnt))
- minor bug fixes
- minor code cleanup
- renamed some functions to better reflect functionality
- updated documentation to reflect function name changes and to better reflect
  the true nature of the module (it encodes serial integers, not URLs)


"""

"""
Each install should use its own alphabet. At the very least, you should
scramble the order of the characters below.
"""
DEFAULT_ALPHABET = "ygw96j2cetxuk3fq4rv5z7hsdamn8bp"
DEFAULT_BLOCK_SIZE = 24
DEFAULT_CHECKSUM = 29
MIN_LENGTH = 5


class IdEncoder(object):
    def __init__(
        self,
        alphabet=DEFAULT_ALPHABET,
        block_size=DEFAULT_BLOCK_SIZE,
        checksum=DEFAULT_CHECKSUM,
    ):
        assert 0 < checksum < len(alphabet)
        self.alphabet = alphabet
        self.block_size = block_size
        self.modulus = checksum

    def encode(self, n, min_length=MIN_LENGTH):
        return self.checksum(n) + self.enbase(self.encode_value(n), min_length)

    def decode(self, n):
        value = self.decode_value(self.debase(n[1:]))
        if self.checksum(value) != n[:1]:
            raise ValueError("Incorrect checksum")
        return value

    def checksum(self, n):
        return self.alphabet[n % self.modulus]

    def _scramble(self, n):
        block_size = self.block_size
        mask = (1 << block_size) - 1
        result = n & ~mask
        for bit in range(block_size):
            if n & (1 << bit):
                result |= 1 << (block_size - bit - 1)
        return result

    encode_value = _scramble
    decode_value = _scramble

    def enbase(self, x, min_length=MIN_LENGTH):
        x = int(x)
        n = len(self.alphabet)
        chars = []
        while x:
            x, c = divmod(x, n)
            chars.insert(0, self.alphabet[c])
        result = str.join("", chars)
        return result.rjust(min_length, self.alphabet[0])

    def debase(self, x):
        n = len(self.alphabet)
        result = 0
        for c in x:
            result *= n
            result += self.alphabet.index(c)
        return result


DEFAULT_ENCODER = IdEncoder()


def encode(n, min_length=MIN_LENGTH):
    return DEFAULT_ENCODER.encode(n, min_length)


def decode(n):
    return DEFAULT_ENCODER.decode(n)


def random_alphabet():
    import random

    l = list(DEFAULT_ALPHABET)
    random.shuffle(l)
    return "".join(l)


if __name__ == "__main__":
    import argparse

    alpha = DEFAULT_ALPHABET
    length = MIN_LENGTH

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-q",
        "--quiet",
        help="suppress formatting and instructional output",
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--length",
        help="set min encoded output length to NUM",
        metavar="NUM",
        type=int,
    )

    encode_group = parser.add_mutually_exclusive_group()
    encode_group.add_argument(
        "-e", "--encode", help="encode NUM", metavar="NUM", type=int
    )
    encode_group.add_argument(
        "-d", "--decode", help="decode STR", metavar="STR", type=str
    )
    encode_group.add_argument(
        "-b",
        "--benchmark",
        help="run a series of NUM encode/decode cycles",
        metavar="NUM",
    )

    alpha_group = parser.add_mutually_exclusive_group()
    alpha_group.add_argument(
        "-a", "--alphabet", help="use ALPHA as the alphabet", metavar="ALPHA"
    )
    alpha_group.add_argument(
        "-r", "--random", help="generate a random alphabet", action="store_true"
    )

    args = parser.parse_args()

    if args.alphabet:
        alpha = args.alphabet

    if args.length:
        length = args.length

    if args.random:
        alpha = random_alphabet()
        if (
            args.quiet
        ):  # no decoration text is nice for supplying alphabet to another program
            print(alpha)
        else:
            print("Random alphabet: %s" % alpha)

    if args.benchmark:
        encoder = IdEncoder(alpha)
        for a in range(0, int(args.benchmark)):
            b = encoder.encode_value(a)
            c = encoder.enbase(b)
            d = encoder.debase(c)
            e = encoder.decode_value(d)
            c = (" " * (7 - len(c))) + c
            if (
                not args.quiet
            ):  # benchmark without output can be useful for measuring speed
                print("%6d %12d %s %12d %6d" % (a, b, c, d, e))

            assert a == e
            assert b == d
    elif args.encode:
        encoder = IdEncoder(alpha, checksum=len(alpha) - 1)
        print(encoder.encode(args.encode, length))
    elif args.decode:
        encoder = IdEncoder(alpha, checksum=len(alpha) - 1)
        print(encoder.decode(args.decode))
