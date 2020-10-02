# Project 1

**`Documentation`**: **project requirements** and **data source** listed below, **notes** listed under [Notes.md](Notes.md)  
**`Notebooks`**: initial Jupyter notebooks for exploratory work  
**`Modules`**: modules productized from Jupyter notebooks  


---

## Requirements

Based on a job descriptions dataset, build a taxonomy of:
+ job titles
+ job-specific skills

Taxonomy model:
+ taxonomy of job titles and skills, eg:
  + job titles: 
  ```python
  [ "Data Scientist", "Data Analyst", "Business Analyst" ]
  # => 
  {
        "Data": [ "Scientist", "Analyst" ],
        "Business": [ "Analyst" ],
        "Scientist": [ "Data" ],
        "Analyst": [ "Data", "Business" ]
  }
  ```
  + taxonomy of job-specific skills, eg:
  ```python
  [ "We are looking for a Java developer [...] Akka [...] Spring" ]
  # =>
  {
        "Java": [ "Akka", "Spring" ],
        "Akka": [ "Java", "Spring" ],
        "Spring": [ "Java", "Akka" ]
  }
  ```

**Eventually**, the taxonomy model should incorporate for every end tag ("leaf tag", if modeled as a tree) at least a metric - for starters at least a "relevancy" metric, such as:
+ percent found in same job description,
+ co-occurence etc.

