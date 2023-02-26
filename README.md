# flashcards-from-pdf

The `.txt` files that contains the questions are formatted in this way:
The file is ordered by num_page. The questions that are generic to the deck and do not have a corresponding pdf page are stored with a negative num_page. The last field contains n digits that are the outcome of the previous response session. 1 means that the question was known and 0 represents the opposite. For example, 100 means that the first time the response was correct and that the last two times the responses were not remembered.

num_domande
num_page ?^? questions ?^? answer[optional] ?^? type[g=general|p=page_specific] ?^? 100 ?^?
