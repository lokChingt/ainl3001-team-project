# ainl3001-team-project

# Intelligent Course Recommendation System

## Overview
A rule-based system that recommends a course to a a student.The student enters their credits, passed subjects, favourite subject and career goal. The systems
1. Recommends eligible courses and ranks them based on student facts [forward chaining]
2. Explains what student needs to meet fir a specific course [backward chaining]

Rules live in data/courses.json separate from code so courses and scoring can change without editing Python.

## Install
Requires Python 3.10+

cd ainl3001-team-project

pip install -r requirements.txt

## How to run
python src/main.py

pytin -m pytest -v

In program choose:
1. Recommed Course: enter facts to get ranked courses with explaination.
2. Chcek Course: enter facts and course to see what you still need to meet.

## Architecture
ainl3001-team-project

|-- data/

|   |-- course.json [course data: hard & soft requirements]

|   |-- rules.json [rule definitions]

|   |-- students.json [sample students for tests]

|-- src/

|   |-- knowledge_base.py [loads and validaets data into knowledge base]

|   |-- reasoning_engine.py [forward chaining, scoring and ranking]

|   |-- backward_chaining.py [goal-driven check one course and outputs unment requirements]

|   |-- main.py [menus, input validation and output]

|-- tests/

|   |-- loader_test.py [unit tests for load_courses function]

|-- proposal/

|   |-- proposal.md

|   |-- image.png

|-- docs/

|-- presentation/

|-- assets/

|-- requirements/

|-- README.md

## Pipeline
student input -> input validation -> knowledge_base.py (course & rules load from data folder) -> reasoning_engine.py [forward chaining] / backward_chaining.py [goal-driven] -> eligible course(ranking, explaintion, output) / unmet conditions & actions (output)


## Contributions
**Lok Ching Tam:** forward-chaining, scoring and ranking, engine tests

**Amy Webb:** course.json + loader, KB tests, README sections, AIMA formulation, backward-chaing

**Karla Satrapová:** input validation, explanation, output layer, sample students data, end-to-end tests