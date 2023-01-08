# Iterator object that serves as a corpus and can pass decks to gensim Word2Vec 1 at a time.

class DeckCorpus():
    def __init__(self, data=None):
            self.data = data
            self.position = 0

    def __next__():
        #TODO make this return the next deck, including parsing it
        self.position += 1
        return