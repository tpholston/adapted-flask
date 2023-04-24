from enum import Enum
import re

from sqlalchemy.orm import validates

from project import db


class GradeType(Enum):
    def __str__(self):
        return str(self.value)
    
    TEST = 'Test'
    ASSIGNMENT = 'Assignment'
    QUIZ = 'Quiz'

class SubjectType(Enum):
    def __str__(self):
        return str(self.value)
    
    READING_AND_WRITING = 'Reading & Writing'
    MATH = 'Math'

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    classes = db.relationship('Class', backref='teacher', lazy=True)
    
    def __repr__(self):
        return f'<Teacher {self.first_name} {self.last_name}>'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    ieps = db.relationship('IEP', cascade='delete')
    grades = db.relationship('Grade', cascade='delete')
    accommodations = db.relationship('Accommodation', cascade='delete')

    def __repr__(self):
        return f'<Student {self.first_name} {self.last_name}>'

class IEP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'))
    description = db.Column(db.String(120))
    disability = db.Column(db.String(120))
    start_date = db.Column(db.Date)

    def __repr__(self):
        return f'<IEP for student ID: {self.student_id} with {self.disability}>'

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column('student_id', db.Integer, db.ForeignKey('student.id'))
    class_id = db.Column('class_id', db.Integer, db.ForeignKey('class.id'))

    def __repr__(self):
        return f'<Enrollment for student ID: {self.student_id} in class ID: {self.class_id}>'

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    name = db.Column(db.String(50))
    school_year = db.Column(db.String(9)) # YYYY-YYYY
    lesson_plans = db.relationship('LessonPlan', cascade='delete')

    # Use regex to validate the school_year field
    @validates('school_year')
    def validate_school_year(self, key, value):
        if not re.match(r'^\d{4}-\d{4}$', value):
            raise ValueError('Invalid school year format. Please use the format: YYYY-YYYY')
        start_year, end_year = value.split('-')
        if int(start_year) < 1900 or int(end_year) > 2100:
            raise ValueError('Invalid school year. Please enter a year between 1900 and 2100.')
        if int(end_year) - int(start_year) != 1:
            raise ValueError('Invalid school year. Please enter consecutive years.')
        return value

    def __repr__(self):
        return f'<Class {self.name} {self.school_year}>'

class LessonPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    name = db.Column(db.String(50))
    date = db.Column(db.Date)
    overview = db.Column(db.Text)
    objective = db.Column(db.Text)
    subject = db.Column(db.Enum(SubjectType))
    accommodations = db.relationship('Accommodation', cascade='delete')

    def __repr__(self):
        return f'<Lesson Plan {self.name} {self.date}>'

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    grade_type = db.Column(db.Enum(GradeType))
    grade_value = db.Column(db.Float)
    date = db.Column(db.Date)
    subject = db.Column(db.Enum(SubjectType))

    def __repr__(self):
        return f'<Grade {self.id} {self.date}>'

class Accommodation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    lesson_plan_id = db.Column(db.Integer, db.ForeignKey('lesson_plan.id'))
    text = db.Column(db.Text)

    def __repr__(self):
        return f'<Accommodation for student ID: {self.student_id}>'