# Control text source

`uss_maine_1898.txt` — front-page article, *New York Journal and Advertiser*,
February 17, 1898 ("DESTRUCTION OF THE WAR SHIP MAINE WAS THE WORK OF AN
ENEMY"). William Randolph Hearst's coverage of the USS Maine explosion is
the textbook case study of sensationalized/propagandistic journalism
("yellow journalism") in American media history — reporting a mine/enemy
attack as established fact well before any investigation had concluded
(the actual cause was never conclusively determined). Public domain
(1898). Transcribed excerpt sourced via Historical Thinking Matters
(historicalthinkingmatters.org), an educational history project — "Document
A" in their Spanish-American War document set
(https://historicalthinkingmatters.org/pdf/SpAm-docset.pdf).

Used here as a control text for the semantic-axis pipeline: a known,
historically-documented example of non-credible/propagandistic news
writing, to test whether the credibility axis registers it differently
from the production 11-article corpus (all mainstream, professionally-
edited outlets) — see `outputs/control-text-comparison.md`.

Not part of the 11-article production corpus. Chosen over 20th-century
totalitarian propaganda (initially considered) because most well-documented,
readily available examples of that era (Nazi radio broadcasts, Der
Stürmer) are also antisemitic hate propaganda targeting real named
individuals — not an appropriate or necessary source for what this check
actually needs (a text known to be journalistically non-credible, not a
text that is also hateful).

Length: ~300 words — shorter than any of the 11 production articles
(shortest: A9 at 401 words). Below the pipeline's normal 3-real-paragraph
minimum in spirit (the "paragraphs" here include Hearst's characteristic
multi-deck sub-headlines, not uniform prose paragraphs), so this is run as
a single whole-document score, not split into headline+lead/body/end
zones like the production corpus.
