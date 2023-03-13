import os
import requests
import gzip
import polars as pl

def download_game_data(set_abbr):
    '''Download traditional + premier draft game files for a set.
    Specify using 3 letter set abbreviation.'''
    
    # Target format:
    # "https://17lands-public.s3.amazonaws.com/analysis_data/game_data/game_data_public.ONE.PremierDraft.csv.gz"
    url_p1 = 'https://17lands-public.s3.amazonaws.com/analysis_data/game_data/game_data_public.'
    url_p2 = 'Draft.csv.gz'
    urls = [url_p1 + set_abbr.upper() + '.Premier' + url_p2,
            url_p1 + set_abbr.upper() + '.Trad' + url_p2]

    data_dir = os.getcwd() + '/data/' + set_abbr

    # Create the local directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    if any(file.endswith('.gz') for file in os.listdir(data_dir)):
        print(f'.gz files found in {data_dir}, skipping download.')
        return
        
    # Download the files and save them to the local directory
    for url in urls:
        # Extract the filename from the URL
        filename = url.split("/")[-1]

        # Make the request and get the response
        response = requests.get(url)
        # Save the file to the local directory
        with open(os.path.join(data_dir, filename), "wb") as f:
            f.write(response.content)


def _extract_urls(response_json, name_to_card_details) -> dict:
    '''Extracts the URLs for card images from the JSON response and maps them to their
     corresponding card names, adding them in-place to the passed name_to_card_details.'''

    for value in response_json["data"]:
        if value["name"][:2] == "A-":
            name_to_use = value["name"][2:]
            name_to_card_details[name_to_use] = {}
        else:
            name_to_use = value["name"]
            name_to_card_details[name_to_use] = {}
        name_to_card_details[name_to_use]["url"] = value["image_uris"]["large"]

    return name_to_card_details

def _extract_rarity(response_json, name_to_card_details) -> dict:
    '''Extracts the rarity of each card from the JSON response and maps it to its
     corresponding card name, adding them in-place to the passed name_to_card_details..'''
    for value in response_json["data"]:
        name_to_use = ""
        if value["name"][:2] == "A-":
            name_to_use = value["name"][2:]
        else:
            name_to_use = value["name"]
        name_to_card_details[name_to_use]["rarity"] = value["rarity"]
        
    return name_to_card_details
        
def scryfall_card_details(set_abbreviation) -> dict:
    '''Calls the Scryfall API to get information on all cards in a specified set and
    returns a dictionary mapping card names to their corresponding image URLs and rarity.'''
    
    response = requests.get("https://api.scryfall.com/cards/search/?q=e=" + set_abbreviation)
    response_json = response.json()

    try:
        next_page_url = response_json["next_page"] #does it have a next page?
        # Note, this will break if there are multiple next pages.
        # we might want to make this a while loop or something in the future.
        # All standard sets currently 2 pages.
        
        response_p2 = requests.get(next_page_url) #if yes, save it
        
        #now we have two JSON objects containing around half the set each.
        response_p2_json = response_p2.json() 
        
    except KeyError:
        raise("No next page in response")
    
    #looping through the responses and saving the card image uris
    name_to_card_details = {}
    
    name_to_card_details = _extract_urls(response_json, name_to_card_details)
    name_to_card_details = _extract_urls(response_p2_json, name_to_card_details)
    name_to_card_details = _extract_rarity(response_json, name_to_card_details)
    name_to_card_details = _extract_rarity(response_p2_json, name_to_card_details)
    
    return name_to_card_details

def extract_gzip(filepath):
    '''Extract contents of .gz file to the same directory where it is located'''
    directory = os.path.dirname(filepath)
    filename = os.path.splitext(os.path.basename(filepath))[0]

    # specify the path of the extracted CSV file
    extracted_filepath = os.path.join(directory, filename)

    # open the compressed CSV file using gzip and read it as binary
    with gzip.open(filepath, "rb") as f_in, open(extracted_filepath, "wb") as f_out:
        # copy the compressed CSV file to the extracted CSV file
        f_out.write(f_in.read())
        
def set_data_folder(set_abbreviation):
    '''Return the path where data is stored a given set'''
    return os.getcwd() + '/data/' + set_abbreviation +'/'

def _game_dtypes(data_sample: pl.DataFrame):
        '''Returns a dict mapping column names in data_sample to polars datatypes.
        Assumes data_sample is an unmodified pl.DataFrame version of 17lands draft .gz file
        '''
        
        game_dtypes = {
            'expansion':pl.Categorical,
            'event_type':pl.Categorical,
            'rank':pl.Categorical,
            'opp_rank':pl.Categorical,
            'main_colors':pl.Categorical,
            'splash_colors':pl.Categorical,
            'opp_colors':pl.Categorical,
            'draft_id':pl.Utf8,
            'draft_time':pl.Datetime,
            'game_number':pl.UInt8,
            'num_mulligans':pl.UInt8,
            'opp_num_mulligans':pl.UInt8,
            'on_play':pl.Boolean,
            'won':pl.Boolean,
            'num_turns':pl.UInt16,
            'user_n_games_bucket':pl.Int16,
            'user_game_win_rate_bucket':pl.Float32,
        }
        
        assert (type(data_sample) == pl.DataFrame), 'data_sample must be a polars DataFrame.'
        dtypes = {}
        for col in data_sample.columns:
            try:
                dtypes[col] = game_dtypes[col]
            except KeyError:
                dtypes[col] = pl.UInt8
        return dtypes
    
def parquet_path(set_abbreviation):
    '''Return path of parquet data for a given set'''
    out = set_data_folder(set_abbreviation) + set_abbreviation + '.parquet'
    assert (os.path.exists(out)) , 'Could not find parquet file for ' + set_abbreviation + '. Have you run gz_to_parquet()?'
    return out

def gz_to_parquet(set_abbreviation):
    '''Convert raw 17lands .gz files in data/<setabreviation> into parquet files with memory efficient datatypes'''
    
    data_folder = set_data_folder(set_abbreviation)
    
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    # get file paths for all .gz files in the data/set folder
    draft_files = []
    for file in os.listdir(data_folder):
        if file.endswith('.gz'):
            draft_files.append(file)
    file_paths = [data_folder + file for file in draft_files]
    assert len(draft_files) > 0, 'Could not find any .gz files in ' + data_folder
    
    #determine datatypes to reduce memory usage ~85%
    dtypes = _game_dtypes(data_sample = pl.read_csv(file_paths[0],
                                            n_rows=100))
    
    with pl.StringCache(): # use the same stringcache for categorical vars btwn files
        dfs = [pl.read_csv(file, dtypes=dtypes) for file in file_paths]
        #may temporarily double memory usage by concat before write
        pl.concat(dfs).write_parquet(data_folder + set_abbreviation + '.parquet', compression = 'snappy')
        
        
def card2vec_preprocess(path):
    '''Read parquet file, preprocess to match DeckCorpus object requirement, return polars df
    '''
    df = pl.read_parquet(path).sort(by=['draft_id','match_number','game_number'])
    rows = len(df)
    df = df.unique(subset=['draft_id'], keep='last') # use only deck in final game of every draft
    left = len(df)
    removed = rows - left
    print(f'removed {removed} rows for decks in the same draft. {left} decks remain.')
    df = df.select(pl.col('^deck_.*$')).to_pandas()
    
    df.columns = df.columns.str.removeprefix('deck_').copy() #get rid of "deck_" in col names
    return df