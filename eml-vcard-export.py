#!/usr/bin/env python3

from eml_vcard_export import app

if __name__ == "__main__":
    a = app.CliApp()
    a.parse_args()
    a.main()