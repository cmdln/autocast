#!/usr/bin/python
import gzip
from BeautifulSoup import BeautifulStoneSoup
import sys



def __main(oo_file):
    g = open(oo_file)
    o = open('output.xml', 'w')
    try:
        soup = BeautifulStoneSoup(g)
        count = 0
        for item in soup.outline.root:
            if item.parent != soup.outline.root:
                continue
            count = count + 1
        print count
    finally:
        g.close()
        o.close()


if __name__ == "__main__":
    __main(sys.argv[1])
