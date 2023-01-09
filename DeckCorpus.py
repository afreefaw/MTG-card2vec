from card_ints_to_list import card_ints_to_list

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
            yield card_ints_to_list(deck, shuffle = self.shuffle)
    
    def __len__(self):
        return len(self.data)    
    
#     def __init__(self, data=None, shuffle=True):

#         self.data = data.copy()
#         self.position = 0
#         self.shuffle = shuffle

#     def __next__(self):
#         if self.position < len(self):
#             return_val = card_ints_to_list(
#                 self.data.iloc[self.position,:],
#                 shuffle = self.shuffle
#             )
#             self.position += 1
#         else:
#             raise StopIteration
#         return return_val
    
#     def __iter__(self):
#         return self
    
#     def __len__(self):
#         return len(self.data)