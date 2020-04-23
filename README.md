# Integer ID Encoder

Python implementation for encoding (usually sequential) integer IDs.

A bit-shuffling approach is used to avoid generating consecutive, predictable
values. However, the algorithm is deterministic and will guarantee that no
collisions will occur.

The encoding alphabet is fully customizable and may contain any number of
characters. By default, digits and lower-case letters are used, with
some removed to avoid confusion between characters like o, O and 0. The
default alphabet is shuffled and has a prime number of characters to further
improve the results of the algorithm.

The block size specifies how many bits will be shuffled. The lower `BLOCK_SIZE`
bits are reversed. Any bits higher than `BLOCK_SIZE` will remain as is.
`BLOCK_SIZE` of 0 will leave all bits unaffected and the algorithm will simply
be converting your integer to a different base.

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
your own unique alphabet.** One alphabet per encoded entity type is
recommended. Best practice is to configure the alphabet(s) as environment
variables (like credentials).

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

