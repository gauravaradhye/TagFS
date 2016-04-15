#!/usr/bin/env python

from __future__ import with_statement

import json
import sys

def main(path):
    with open('config.json', 'r+') as outfile:
        try:
            origin_data = json.load(outfile) 
        except ValueError as e: 
            origin_data = {}
        origin_data["path"] = origin_data.get("path", path)
        outfile.seek(0, 0)
        json.dump(origin_data, outfile) 

if __name__ == '__main__':
    main(sys.argv[1])
