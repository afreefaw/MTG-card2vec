import pandas as pd

def card2vec_preprocess(path):
    '''Loads data at specified path which is assumed to be the output of 'draft_game_cleaner'
    and performs preprocessing so it is ready to be passed to a DeckCorpus object.
    '''
    df_raw = pd.read_csv(path)
    
    #Filter out pool and sideboard columns since we don't need those
    keep_cols = df_raw.columns.drop(list(df_raw.filter(regex='pool_|sideboard_')))
    df = df_raw[keep_cols].copy()

    #reset index
    df.reset_index(inplace=True)
    
    #find duplicate decks (look only at deck columns)
    deck_cols = list(df.filter(regex='deck_'))
    duplicates = df.duplicated(keep='first', subset = deck_cols).copy()
    duplicates_idx = duplicates[duplicates==True].index.copy()
    print('Dropping ', len(duplicates_idx), ' duplicate decks')
    df.drop(labels=duplicates_idx, axis=0, inplace=True)
    print(len(df), ' unique decks remain.')
    
    #filter to just 'deck_' columns
    df = df[deck_cols].copy()
    
    #remove 'deck_' prefix
    df.columns = df.columns.str.removeprefix('deck_').copy()
    
    return df