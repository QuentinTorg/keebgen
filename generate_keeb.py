#!/usr/bin/env python3

import solid as sl

# TODO: finish end user interface

"""
This file is an example to show how the library can be used, 
at least in a simple case.
"""

def main():
    from keebgen import DactylManuform

    keeb = DactylManuform(rows=4, cols=6)
    sl.scad_render_to_file(keeb.solid(), "example_keyboard.scad")


def build_your_own():
    # TODO: flush out this interface
    from keebgen import DactylManuform, Key, KeyColumn, ThumbCluster

    num_rows = 4
    num_cols = 6
    lightcycle = DactylManuform.unpopulated(rows=num_rows, cols=num_cols)

    key_params = {'switch': 'cherry_mx', 'cap': 'oem'}
    small_key = Key(**key_params)
    big_key = Key(units=1.5, **key_params)

    # Define the right half

    # Columns from left to right
    """
    [x][x][x][x][x][x]
    [x][x][x][x][x][x]
    [x][x][x][x][x][x]
       [x][x][x][x][x]
    """
    cols  = [KeyColumn(keys=[small_key] * (num_rows-1))] # short first column
    cols += [KeyColumn(keys=[small_key] * num_rows) for _ in range(num_cols-1)]
    lightcycle.right_half.add_columns(cols)

    thumb_cluster = ThumbCluster(style='dactyl')
    thumb_cols = [
        KeyColumn(keys=[small_key]*3),
        KeyColumn(keys=[small_key, big_key]),
        KeyColumn(keys=[big_key]),
    ]

    # TODO: Do we need a way to communicate how the thumb columns are aligned?
    """
    [x][x]
    [x]| || | 
    [x]|_||_|
    """
    thumb_cluster.add_columns(thumb_cols)
    lightcycle.right_half.set_thumb_cluster(thumb_cluster)

    lightcycle.left_half = lightcycle.right_half.copy(mirror=True)

    sl.scad_render_to_file(lightcycle.solid(), "lightcycle.scad")


if __name__ == '__main__':
    main()