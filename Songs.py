class Songs:
    quarter_note = 0.5
    whole_note = quarter_note * 4
    first_16th = (quarter_note / 3) * 2
    second_16th = quarter_note / 3

    starmachine = [
        # Bar 1
        ['f4', first_16th],
        ['g4', second_16th],
        ['a4', first_16th],
        ['c5', second_16th + first_16th],
        ['a4', second_16th],
        ['g4', first_16th],
        # Bar 2
        ['e4', second_16th + first_16th],
        ['c5', second_16th + quarter_note],
        ['a4', quarter_note],
        ['e4', quarter_note],
        # Bar 3 + 4
        ['f4', first_16th],
        ['g4', second_16th],
        ['a4', first_16th],
        ['d5', second_16th + first_16th],
        ['a4', second_16th],
        ['e5', first_16th],
        ['a4', second_16th + whole_note - quarter_note],
        [0, quarter_note],
        # Bar 5
        ['f4', first_16th],
        ['g4', second_16th],
        ['a4', first_16th],
        ['d5', second_16th + first_16th],
        ['a4', second_16th],
        ['e5', first_16th],
        # Bar 6
        ['a4', second_16th + quarter_note],
        ['a#4', quarter_note],
        ['c5', quarter_note],
        ['d5', quarter_note],
        # Bar 7
        ['e5', first_16th],
        ['c5', second_16th],
        ['f5', first_16th],
        ['c5', second_16th],
        ['g5', first_16th],
        ['c5', second_16th],
        ['a5', first_16th],
        # Bar 8
        ['g5', second_16th + quarter_note * 2 + first_16th],
        ['f5', second_16th],
        ['e5', first_16th],
        # Bar 9
        ['f5', second_16th + first_16th],
        ['a4', first_16th],
        [0, second_16th],
        ['a4', second_16th],
        ['d5', first_16th],
        ['a4', second_16th],
        ['c5', first_16th],
        # Bar 10
        ['c5', second_16th + first_16th],
        ['f4', second_16th + quarter_note],
        ['f4', first_16th],
        ['g4', quarter_note],
        
        # Bar 11
        ['a4', second_16th + quarter_note],
        ['c5', quarter_note],
        ['c5', quarter_note],
        ['a4', first_16th],
        
        # Bar 12
        ['g4', second_16th + (quarter_note * 2) + first_16th],
        ['f5', second_16th],
        ['e5', first_16th],
        
        # Bar 13
        ['f5', second_16th + first_16th],
        ['a4', first_16th],
        [0, second_16th],
        ['a4', second_16th],
        ['d5', first_16th],
        ['a4', second_16th],
        ['c5', first_16th],
        
        # Bar 14
        ['c5', second_16th + first_16th],
        ['f4', quarter_note + second_16th],
        ['f4', first_16th],
        ['g4', quarter_note],
        
        # Bar 15
        ['a4', second_16th + first_16th],
        ['f4', second_16th],
        ['a#4', first_16th],
        ['f4', second_16th],
        ['c5', first_16th],
        ['f4', second_16th],
        ['d5', first_16th],
        
        # Bar 16
        ['e5', second_16th + whole_note - quarter_note],
        [0, quarter_note]
        
    ]
