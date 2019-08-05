# Eml vCard Export Tool

RFC 2425 defines a way to transport a vcard inside an email. This tool 
loads eml (email) files and extracts the vcard. 

Embedded images (binary data) stored as email attachment (multi part email) are 
embedded into the exported vcard. The linking between vcard and attachment is 
described in RFC 2425 and the embedding of image data into vcards in RFC 2426.

Care is taken, to limit the impact on non-standard vcard extensions not understood
by the underlying library.

This tool can also export vcards to a csv table. A vcard is a multi dimensional 
data structure, while a table has only two dimensions, thus the CSV representation
is limited in usability and correctness.
