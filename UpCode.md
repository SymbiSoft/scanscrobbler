## Upcode ##

Upcode is a 2d and 1d barcode reader.

It is marketed primarily for reading 2d QR/ datamatrix codes. These are capable of holding a large amount of information in a small space, and are commonly used to distribute urls and contact information in a fun and potentially easy to use way (saves typing a long url on a tricky input for example).

UpCode is currently used by ScanScrobbler to read barcodes from a CD. the barcode reading algorithm in UpCode is very robust, and I've yet to find a more suitable alternative that will enable me to do away with the slightly clunky interfacing of ScanScrobbler with UpCode.

Ideally, ScanScrobbler would read a barcode without the use of a 3rd party application, but I've yet to find a decent 1D barcode reading library for pyS60 that works.