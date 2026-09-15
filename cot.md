#Quiz Cleaner 

This turns messy weekly quiz-score exports from the LMS into clean, usable student records, then ranks students by performance. 



This operates in a two-stage workflow of raw data in via pandas before instantiating domain models in Python

1.
   Raw input dictionaries are converted into a DataFrame. Names are stripped of whitespace. Deduplication is performed using df.drop_duplicates as an intentionally non-failing cleaning operation. Next, the raw CSV is outputted

2. 
   Cleaned rows with successfully parsed scores are passed to the `Student`, where validation is enforced 


How can i manage failures?

If any record containing malformed or bad data that prevents the creation of a valid `Student` instance, whereas valid deduplication filters are excluded.

**Parsing Failure:** 
If a score string is not a number, raises a `ValueError`. This is caught then records a "Failed to parse scores" error along with the original dictionary.

**Validation Failure:** 
If score parsing succeeds but values violate it like if empty score list or scores outside $[0, 100]$
the `Student` constructor raises the custom `InvalidScoreError`. Every iteration is caught, then it goes back to the original raw row.

**Deduplication** 
Duplicate student records (second occurrence of Amara) are dropped in Pandas by default. 
