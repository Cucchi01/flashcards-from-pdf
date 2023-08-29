# flashcards-from-pdf

The `.txt` files that contains the questions are formatted in this way:\\
The first information is the number of completed tests on the flashcards of this file. Then for every completed attempt there is the date in which it was completed and the ratio of the questions completed at the first attempt to the number of questions.\\
There is a row that is at 1 if there is an ongoing test and at 0 otherwise.\\
Then there is a number that corresponds to the number of questions and finally there are questions. They are ordered by num_page.\\
A generic question is a questions that is not connected to a page and the reference page gives only the position of the question. A generic question could have an answer or not. For example a flashcard could only be put there to say something to the reader.\\
The questions that are generic to the deck and do not have a corresponding pdf page are stored with a negative num_page.\\
A question can be specific to a page and have an answer, for example to specify further something.\\
The last but one field contains n digits that are the outcome of the previous response sessions. 1 means that the question was known and 0 represents the opposite. For example, 100 means that the first time the response was correct and that the last two times the responses were not remembered.\\
Finally there is the result of the ongoing test. If there is no ongoing test this field should be not considered.\\

num_completed_tests\\
date1_completed ?^? percentage_correct_first_try ?^?\\
date2_completed ?^? percentage_correct_first_try ?^?\\
....\\
ongoing_test_flag['0'=no|'1'=yes]\\
num_questions\\
num_page ?^? questions ?^? answer['!-!'= no answer] ?^? type['g'=general|'p'=page_specific] ?^? 100 ?^? ongoing_test_result['0'=mistake|'1'=not_done|'2'=correct][optional]?^?\\
