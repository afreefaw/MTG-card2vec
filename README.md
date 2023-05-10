# card2vec
## Check out a ***rough tech-demo*** of this concept [here](https://card2vec.herokuapp.com/).

Vector embeddings of Magic the Gathering cards using [17Lands data](https://www.17lands.com/public_datasets) and [gensim](https://github.com/RaRe-Technologies/gensim).

**word**2vec creates vector embeddings of words such that semantically similar words are located close together in vector space.

**card**2vec uses word2vec to create embeddings of Magic the Gathering cards such that similar cards are close together.

Embeddings allow for some cool card math:

![math_visual_transparent](https://user-images.githubusercontent.com/55111775/222978940-322bc991-fcb7-4bf4-aaa1-5a94f4cf4fe1.png)

For more details on what this image is showing, see [examples](#examples).

## About Embeddings
Card embeddings are rich representations of cards, learned entirely from decklists. card2vec does not receive any information about the cards (such as colour, converted mana cost, power/toughness, abilities) other than their name, and what decks they are in.

An embedding is a vector in which each value can be thought of as a numerical representation of a feature of the card. For example, if the embedding for a card was:

```python
Array([0.06, 0.01, 22.43])
```
The card would be strongly expressing the feature in the 3rd position (which might indicate e.g., whether it is a sorcery), but the other two features are low (so for example, that might indicate it is NOT a red card, and NOT a creature).

In practice, embeddings are much longer vectors (currently length 100), and the features are much harder to interpret than in this simplified example.

## Examples

In the [word2vec paper](https://arxiv.org/abs/1301.3781), the authors highlight a magical result:
> *Using a word offset technique where simple algebraic operations are performed on the word vectors, it was shown for example that vector(”King”) - vector(”Man”) + vector(”Woman”) results in a vector that is closest to the vector representation of the word Queen*

The same type of operations can be performed on card vectors. For example, starting from the vector for [Call in a Professional](https://scryfall.com/card/snc/103/call-in-a-professional) (a red removal spell), we subtract mountain and add swamp. The resulting vector is closest in vector space to black removal options (excluding Swamp, since we just added it):

<p align="left">
  <img width="500" src="https://user-images.githubusercontent.com/55111775/222977789-22ea2f98-f27a-4628-bc92-47f96d0fe509.png">
</p>

[Murder](https://scryfall.com/card/snc/88/murder) <br>
[Whack](https://scryfall.com/card/snc/99/whack) <br>
[Deal Gone Bad](https://scryfall.com/card/snc/74/deal-gone-bad) <br>

Using dimensionality reduction techniques such as [T-SNE](https://towardsdatascience.com/an-introduction-to-t-sne-with-python-example-5a3a293108d1), the vectors can be reduced to just 2 dimensions for plotting while preserving some of the information about distances between the embeddings in vector space.

Much of the richness of the embeddings is lost through this process, however it allows us to visualize high-level card similarities (mostly colour).

### Examples for the set *Streets of New Capenna:*

**Artifacts are at the intersection of the different colour clusters**
<p align="left">
  <img width="500" src="https://user-images.githubusercontent.com/55111775/222976920-373aa547-5bcb-4ede-8d0d-c2bad5ac35e7.gif">
</p>


**Multi-colour cards are tightly clustered**

<p align="left">
  <img width="500" src="https://user-images.githubusercontent.com/55111775/222976936-c0f1c33a-76c7-4f07-a29e-fc8a60e8e4a9.gif">
</p>
