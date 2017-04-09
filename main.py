#!/usr/bin/env python3

import test

if __name__ == '__main__':
    import os
    if not os.path.exists('output'):
        os.mkdir('output')

    test.RunTest()
