import pandas as pd
import numpy as np

#custom exception 1
class InvalidScoreError(Exception):
    """Raised when a score is invalid (non-numeric or out of range)."""
    def __init__(self, name, scores, reason):
        self.name = name    
        self.scores = scores
        self.reason = reason
        super().__init__(f"Student '{name}': {reason}")

#custom exception 2
class StudentRecordLockedError(Exception):
    """Raised when attempting to modify a locked student record."""
    def __init__(self, name):
        self.name = name
        super().__init__(f"Cannot add score to locked record for student '{name}'")


class Student:
    def __init__(self, name, scores):
        self.name = name
        self._scores = np.array(scores, dtype=float)
        self._locked = False
        self._validate_scores()
    
    def _validate_scores(self):
        if len(self._scores) == 0:
            raise InvalidScoreError(self.name, self._scores, "No valid scores provided")
        if np.any(self._scores < 0) or np.any(self._scores > 100):
            raise InvalidScoreError(self.name, self._scores, "Score(s) out of range [0, 100]")
    
    def lock(self):
        self._locked = True
    
    def add_score(self, score):
        if self._locked:
            raise StudentRecordLockedError(self.name)
        self._scores = np.append(self._scores, score)
        self._validate_scores()
    
    def average(self):
        return np.mean(self._scores)
    
    def __str__(self):
        return f"{self.name} — {self.average():.2f} avg."
    
    def __repr__(self):
        return f"Student(name='{self.name}', scores={list(self._scores)}, locked={self._locked})"


def clean_and_build(raw_rows):
    df = pd.DataFrame(raw_rows)
    df['name_clean'] = df['name'].str.strip()
    
    df['orig_idx'] = df.index
    df = df.drop_duplicates(subset=['name_clean'], keep='first')
    
    def parse_scores(score_str):
        try:
            return [float(s.strip()) for s in score_str.split(',')]
        except (ValueError, AttributeError):
            return None

    df['parsed_scores'] = df['scores'].apply(parse_scores)
    
    students = []
    failures = []
    

    for _, row in df.iterrows():
        orig_row = raw_rows[row['orig_idx']]
        parsed = row['parsed_scores']
        
        if parsed is None:
            failures.append({
                "row": orig_row, 
                "error": "Failed to parse scores"
            })
            continue
        
        try:
            student = Student(row['name_clean'], parsed)
            students.append(student)
        except InvalidScoreError as e:
            failures.append({
                "row": orig_row, 
                "error": str(e)
            })
            
    return students, failures


def rank_students(students):
    return sorted(students, key=lambda s: s.average(), reverse=True)


if __name__ == "__main__":
    raw_rows = [
        {"name": " Amara ", "scores": "92,85,78"},
        {"name": "Leo", "scores": "88,91,73"},
        {"name": "Priya", "scores": "65,72,150"},         
        {"name": "Sam", "scores": "70,not_a_number,60"},  
        {"name": "Amara", "scores": "95,90,88"},          
        {"name": "Jade", "scores": "81,77,84,90"},
    ]

    # cleaning
    students, failures = clean_and_build(raw_rows)

    # each successfully built student via print(student)
    for student in students:
        print(student)

    # full list of built students in one call
    print(students)

    # one line per failed row
    for failure in failures:
        print(f"Skipped row: {failure['row']} -> reason: {failure['error']}")

    # manual demonstration (Lock & exception check)
    demo_student = Student("Demo", [85.0, 90.0])
    demo_student.lock()
    try:
        demo_student.add_score(95.0)
    except StudentRecordLockedError as e:
        print(e)

    # ranked list with 2 decimal places
    ranked = rank_students(students)
    for i, student in enumerate(ranked, 1):
        print(f"{i}. {student.name} — {student.average():.2f} avg.")