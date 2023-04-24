from datetime import datetime
from random import randrange

from project.models import Teacher, Grade, LessonPlan, Class, Student, GradeType, SubjectType, IEP, Accommodation, Enrollment

# Only called to initialize/reset the db. Remove later
def init_db(db, app):
    with app.app_context():
        db.drop_all()
        db.create_all()

        # create 2 teachers
        teacher1 = Teacher(first_name='John', last_name='Doe',
                        email='johndoe@example.com', password='password')
        teacher2 = Teacher(first_name='Jane', last_name='Doe',
                        email='janedoe@example.com', password='password')
        db.session.add_all([teacher1, teacher2])
        db.session.commit()

        # create 10 students
        student1 = Student(first_name='Alice', last_name='Johnson')
        student2 = Student(first_name='Bob', last_name='Smith')
        student3 = Student(first_name='Charlie', last_name='Brown')
        student4 = Student(first_name='Diana', last_name='Parker')
        student5 = Student(first_name='Emily', last_name='Lee')
        student6 = Student(first_name='Frank', last_name='Rodriguez')
        student7 = Student(first_name='Grace', last_name='Lin')
        student8 = Student(first_name='Henry', last_name='Chen')
        student9 = Student(first_name='Isabella', last_name='Davis')
        student10 = Student(first_name='Jack', last_name='Wang')
        db.session.add_all([student1, student2, student3, student4,
                        student5, student6, student7, student8, student9, student10])
        db.session.commit()

        # create 2 classes and enroll 5 students in each class
        class1 = Class(name='English 101',
                    school_year='2022-2023', teacher=teacher1)
        class2 = Class(name='Math 101', school_year='2022-2023', teacher=teacher2)
        db.session.add_all([class1, class2])
        db.session.commit()

        enroll1 = Enrollment(student_id=student1.id, class_id=class1.id)
        enroll2 = Enrollment(student_id=student2.id, class_id=class1.id)
        enroll3 = Enrollment(student_id=student3.id, class_id=class1.id)
        enroll4 = Enrollment(student_id=student4.id, class_id=class1.id)
        enroll5 = Enrollment(student_id=student5.id, class_id=class1.id)
        enroll6 = Enrollment(student_id=student6.id, class_id=class2.id)
        enroll7 = Enrollment(student_id=student7.id, class_id=class2.id)
        enroll8 = Enrollment(student_id=student8.id, class_id=class2.id)
        enroll9 = Enrollment(student_id=student9.id, class_id=class2.id)
        enroll10 = Enrollment(student_id=student10.id, class_id=class2.id)
        db.session.add_all([enroll1, enroll2, enroll3, enroll4,
                        enroll5, enroll6, enroll7, enroll8, enroll9, enroll10])
        db.session.commit()

        # create 3 lesson plans for each class
        lesson1 = LessonPlan(name='Lesson 1', date=datetime.strptime('2022-09-01', '%Y-%m-%d'), overview='Overview of lesson 1',
                            objective='Objective of lesson 1', subject=SubjectType.READING_AND_WRITING, class_id=class1.id)
        lesson2 = LessonPlan(name='Lesson 2', date=datetime.strptime('2022-09-08', '%Y-%m-%d'), overview='Overview of lesson 2',
                            objective='Objective of lesson 2', subject=SubjectType.READING_AND_WRITING, class_id=class1.id)
        lesson3 = LessonPlan(name='Lesson 3', date=datetime.strptime('2022-09-15', '%Y-%m-%d'), overview='Overview of lesson 3',
                            objective='Objective of lesson 3', subject=SubjectType.READING_AND_WRITING, class_id=class1.id)
        db.session.add_all([lesson1, lesson2, lesson3])
        class1.lesson_plans.extend([lesson1, lesson2, lesson3])

        lesson4 = LessonPlan(name='Lesson 1', date=datetime.strptime('2022-09-01', '%Y-%m-%d'),
                            overview='Overview of lesson 1', objective='Objective of lesson 1', subject=SubjectType.MATH, class_id=class2.id)
        lesson5 = LessonPlan(name='Lesson 2', date=datetime.strptime('2022-09-08', '%Y-%m-%d'),
                            overview='Overview of lesson 2', objective='Objective of lesson 2', subject=SubjectType.MATH, class_id=class2.id)
        lesson6 = LessonPlan(name='Lesson 3', date=datetime.strptime('2022-09-15', '%Y-%m-%d'),
                            overview='Overview of lesson 3', objective='Objective of lesson 3', subject=SubjectType.MATH, class_id=class2.id)
        db.session.add_all([lesson4, lesson5, lesson6])
        class2.lesson_plans.extend([lesson4, lesson5, lesson6])

        db.session.commit()

        # create 3 grades for each student
        for student in [student1, student2, student3, student4, student5, student6, student7, student8, student9, student10]:
            grade1 = Grade(student_id=student.id, grade_type=GradeType.TEST, grade_value=randrange(
                50, 100), date=datetime.strptime('2022-09-01', '%Y-%m-%d'), subject=SubjectType.MATH)
            grade2 = Grade(student_id=student.id, grade_type=GradeType.ASSIGNMENT, grade_value=randrange(
                50, 100), date=datetime.strptime('2022-09-08', '%Y-%m-%d'), subject=SubjectType.MATH)
            grade3 = Grade(student_id=student.id, grade_type=GradeType.QUIZ, grade_value=randrange(
                50, 100), date=datetime.strptime('2022-09-15', '%Y-%m-%d'), subject=SubjectType.READING_AND_WRITING)
            db.session.add_all([grade1, grade2, grade3])
            db.session.commit()

        # create IEPs
        iep1 = IEP(student_id=student1.id, description='Sample Text',
                disability='Dyscalculia', start_date=datetime.strptime('2021-01-01', '%Y-%m-%d'))
        iep2 = IEP(student_id=student2.id, description='Reading Comprehension',
                disability='Dyslexia', start_date=datetime.strptime('2020-08-15', '%Y-%m-%d'))
        iep3 = IEP(student_id=student4.id, description='Attention Deficit Hyperactivity Disorder (ADHD)',
                disability='ADHD', start_date=datetime.strptime('2022-02-01', '%Y-%m-%d'))
        iep4 = IEP(student_id=student7.id, description='Language Barrier',
                disability='ESL', start_date=datetime.strptime('2021-09-01', '%Y-%m-%d'))
        iep5 = IEP(student_id=student10.id, description='Social Anxiety',
                disability='Anxiety', start_date=datetime.strptime('2021-03-01', '%Y-%m-%d'))
        db.session.add_all([iep1, iep2, iep3, iep4, iep5])
        db.session.commit()

        # Create accommodations
        acc1 = Accommodation(student_id=student1.id,
                            lesson_plan_id=lesson1.id, text='Allow use of calculator')
        acc2 = Accommodation(student_id=student2.id, lesson_plan_id=lesson1.id,
                            text='Provide extra time for reading assignments')
        acc3 = Accommodation(student_id=student4.id, lesson_plan_id=lesson1.id,
                            text='Use multi-sensory teaching strategies')
        acc4 = Accommodation(student_id=student7.id, lesson_plan_id=lesson4.id,
                            text='Provide additional language support resources')
        acc5 = Accommodation(student_id=student10.id, lesson_plan_id=lesson4.id,
                            text='Provide alternative seating options')
        db.session.add_all([acc1, acc2, acc3, acc4, acc5])
        db.session.commit()