import pandas as pd
from random import shuffle as shuf

class DeckCorpus():
    ''' Iterator object that serves as a corpus and can pass decks to gensim Word2Vec 1 at a time.
    (generates processed decks which are lists of strings)

    data:
        pandas Dataframe in which each row represents 1 deck, and integer counts in each column
        represent the count of a specific card in the deck.
    '''

    def __init__(self, data=None, shuffle=True):
        self.data = data.copy()
        self.shuffle = shuffle
 
    def __iter__(self):
        for i, deck in self.data.iterrows():
            yield _card_ints_to_list(deck, shuffle = self.shuffle)
    
    def __len__(self):
        return len(self.data)

def _card_ints_to_list(series, shuffle=False):
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