import pandas as pd
from random import shuffle as shuf

def card_ints_to_list(series, shuffle=False):
    ''' Take a pandas Series in which the index is card names and values are integer card
    counts and return a list in which each element is the name of a card (as a string).
    
    e.g., see the example input series below and corresponding example output
    
    Input Series:
        deck_A Little Chat                2
        deck_All-Seeing Arbiter           1
        deck_An Offer You Can't Refuse    0
    Output list:
        ['deck_A Little Chat', 'deck_A Little Chat', 'deck_All-Seeing Arbiter']
    '''
    assert(type(series) == pd.Series)
    
    deck_list = []
    filtered_series = series[series>0]
    idx = filtered_series.index
    for i in range(len(filtered_series)):
        word = [idx[i]]
        words = word * filtered_series[i]
        deck_list += words
    assert(len(deck_list) == sum(series))
    
    if shuffle:
        shuf(deck_list) #random.shuffle does inplace shuffling
        
    return deck_list