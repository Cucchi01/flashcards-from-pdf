# flashcards-from-pdf

The `.txt` files that contains the questions are formatted in this way:  
The first information is the number of completed tests on the flashcards of this file. Then for every completed attempt there is the date in which it was completed and the ratio of the questions completed at the first attempt to the number of questions.  
There is a row that is at 1 if there is an ongoing test and at 0 otherwise.  
Then there is a number that corresponds to the number of questions and finally there are questions. They are ordered by num_page.  
A generic question is a questions that is not connected to a page and the reference page gives only the position of the question. A generic question could have an answer or not. For example a flashcard could only be put there to say something to the reader.  
The questions that are generic to the deck and do not have a corresponding pdf page are stored with a negative num_page.  
The question, that are not generic, are inserted before the card that is currently visualized. So, if there is a flashcard on a specific pdf page on the screen, the reference page of the new flashcard will be the same and it will be inserted immediatly before.  
A question can be specific to a page and have an answer, for example to specify further something.  
The last but one field contains n digits that are the outcome of the previous response sessions. 1 means that the question was known and 0 represents the opposite. For example, 100 means that the first time the response was correct and that the last two times the responses were not remembered.  
Finally there is the result of the ongoing test. If there is no ongoing test this field should be not considered.

num_completed_tests  
datetime1_completed ?^? percentage_correct_first_try ?^?  
datetime2_completed ?^? percentage_correct_first_try ?^?  
....  
first_pass_flag['0'=false|'1'=true]  
num_questions  
num_page ?^? questions ?^? answer['!-!'= no answer] ?^? type['g'=general|'p'=page_specific] ?^? 100 ?^? ongoing_test_result['0'=mistake|'1'=not_done|'2'=correct][optional]?^?

The datetimes are saved in the "yyyy/mm/dd_HH:MM:SS" format.
Only the first pass result is saved as a completed task. So if there are 10 flashcards and in the first trial you complete 6 of those, it is going to be save 0.6. Then the flashcards that were not completed the first time will be visualized again until all of them are responded correctly, but these results will not be saved.
Afterwards there is the possibility to start a new test and the first result will be saved again.

The reference page index is in 1-based format, because in this way a user can read a txt file and make sense if it. Sometimes this software is not available, but it can read the txt file. In the codebase the index of a pdf page is saved and used in 0-based format.  
There is always a +1 in the visualizazion process. So in the txt a generic page has as index -1 and internally it is store -2.

It is possible to export the flashcards to a txt file that it is compatible with Anki. The txt file has to be imported manually in Anki and it is saved in data\Anki. The pdf pages related to a question are converted to jpg and saved in the media directory of Anki. The same relative path of the pdf is copied in the Anki media directory and in data\Anki.

Shortcuts:
Shortcut|Action
---|---
Ctrl++ | Zoom in pdf
Ctrl+- | Zoom out pdf
Ctrl+G | Focus on spinbox
Ctrl+E | Edit current flashcard
Ctrl+A | Focus on question text input(A = Add new flashcard)
Ctrl+S | Add/modify flashcard
Ctrl+Shif+S | Add/modify generic flashcard
Ctrl+D | Remove current flashcard (D = delete)
Ctrl+R | Cancel current flashcard (R = Redo)
Up arrow | Previous page
Down arrow | Next page
Left arrow | Previous card
Right arrow | Next card
Ctrl+Left arrow | Previous flashcard
Ctrl+Right arrow | Next flashcard
