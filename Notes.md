## Notes Summary

TBA

---

## Notes

## September 29, 2020

Dataset used: https://www.kaggle.com/bman93/dataset
  


Better dataset: https://www.kaggle.com/madhab/jobposts  
Out of: https://www.kaggle.com/datasets?search=job

---
Checked NER with spacy pretrained corpus ("en_core_web_sm").
eg: 
   Proficient in Word GPE , Excel PRODUCT and Outlook PRODUCT
-> corpus needs to be retrained, if required skills are to be extracted from job descriptions

---

Built association dictionary based on 2-word job titles slice of the dataset.
Since this dataset has a high count of a small number of distinct job titles, the resulting dictionary is small:

+ Order matters -> "A B" is split as [A,B] and then saved in association dict (linear time) as `{ 'A': 'B' }`
```python
{
    'Administrative': ['Assistant'],
    'Sales': ['Representative'],
    'Java': ['Developer'],
    'Financial': ['Analyst'],
    'Project': ['Manager'],
    'Executive': ['Assistant'],
    'Maintenance': ['Technician'],
    'Physical': ['Therapist'],
    'Store': ['Manager'],
    'Staff': ['Accountant'],
    'Account': ['Executive', 'Representative'],
    'Senior': ['Accountant'],
    'Business': ['Analyst'],
    'Restaurant': ['Manager'],
    'Benefits': ['Consultant']
}
```

+ Order does not matter -> "A B" is split as [A,B] and then saved in association dict (linear time) as `{ 'A': 'B', 'B': 'A' }`
```python
{
    'Administrative': ['Assistant'],
    'Assistant': ['Administrative', 'Executive'],
    'Sales': ['Representative'],
    'Representative': ['Sales', 'Account'],
    'Java': ['Developer'],
    'Developer': ['Java'],
    'Financial': ['Analyst'],
    'Analyst': ['Financial', 'Business'],
    'Project': ['Manager'],
    'Manager': ['Project', 'Store', 'Restaurant'],
    'Executive': ['Assistant', 'Account'],
    'Maintenance': ['Technician'],
    'Technician': ['Maintenance'],
    'Physical': ['Therapist'],
    'Therapist': ['Physical'],
    'Store': ['Manager'],
    'Staff': ['Accountant'],
    'Accountant': ['Senior', 'Staff'],
    'Account': ['Executive', 'Representative'],
    'Senior': ['Accountant'],
    'Business': ['Analyst'],
    'Restaurant': ['Manager'],
    'Benefits': ['Consultant'],
    'Consultant': ['Benefits']
}
```

**`ISSUE`**: Job titles can get mucky.
+ Case in point, job title word count can be significant, reaching up to 12 "words" (not preprocessed for actual words)
```
2     36443
3     13537
4      9091
1      3292
6      3275
12     2419
8      2412
9      1823
Name: Query_word_len, dtype: int64
```
+ A 12-token example:
  + `Sales / Customer Service – Part or Full time – Summer Work`
  + This should ideally be saved as:
```python
{
    'Sales': [ 'Customer Service', 'Service' ],
    'Customer': [ 'Sales Service', 'Service' ],
    'Service' ?
}
```

---

# September 30, 2020


