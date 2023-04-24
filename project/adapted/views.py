from enum import Enum
from datetime import datetime

from flask import Blueprint, jsonify, request, abort

from project import db
from project.models import Teacher, Student, IEP, Enrollment, Class, LessonPlan, Grade, Accommodation, GradeType, SubjectType

index_blueprint=Blueprint('index_page',__name__)

def validate_request(request, required_fields):
    for field in required_fields:
        if field not in request.json:
            return False, {'error': f'Missing {field}'}
    return True, {}


def validate_enum(enum: Enum, enumText):
    try:
        return True, enum(enumText)
    except ValueError as e:
        return False, {'error': f'Invalid {type(enum)}', 'message': str(e)}

### SPECIAL GET REQUESTS ###


@index_blueprint.route('/')
def hello_world():
    return jsonify({"hello": "world"})

@index_blueprint.route('/class/<int:class_id>/students')
def class_students(class_id):
    # Check if class exists
    class_: Class = Class.query.get_or_404(class_id)

    enrolled_students: list[Enrollment] = Enrollment.query.filter_by(
        class_id=class_id).all()
    students = []
    for enrollment in enrolled_students:
        student = Student.query.filter_by(id=enrollment.student_id).first()
        iep = IEP.query.filter_by(student_id=enrollment.student_id).first()
        iep_object = {
            "description": iep.description,
            "disability": iep.disability
        } if iep else None
        students.append({
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "iep": iep_object
        })

    response = {
        "Class": {
            "id": class_id,
            "students": students
        }
    }
    return jsonify(response)


@index_blueprint.route('/class/<int:class_id>/grades')
def class_grades(class_id):
    # Check if class exists
    class_: Class = Class.query.get_or_404(class_id)

    enrolled_students: list[Enrollment] = Enrollment.query.filter_by(
        class_id=class_id).all()
    students = []
    for enrollment in enrolled_students:
        student: Student = Student.query.filter_by(
            id=enrollment.student_id).first()
        grades: list[Grade] = Grade.query.filter_by(
            student_id=enrollment.student_id).all()
        student_grades = []
        for grade in grades:
            student_grades.append({
                "id": grade.id,
                "subject": str(grade.subject),
                "grade_type": str(grade.grade_type),
                "date": grade.date,
                "grade_value": grade.grade_value
            })
        students.append({
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "grades": student_grades
        })

    response = {
        "Class": {
            "id": class_id,
            "students": students
        }
    }
    return jsonify(response)


@index_blueprint.route('/class/<int:class_id>/lesson_plans')
def class_lesson_plans(class_id):
    # Check if class exists
    class_: Class = Class.query.get_or_404(class_id)

    lesson_plan_rows: list[LessonPlan] = LessonPlan.query.filter_by(
        class_id=class_id).all()
    lesson_plans = []
    for lesson_plan in lesson_plan_rows:
        lesson_plans.append({
            "id": lesson_plan.id,
            "name": lesson_plan.name,
            "date": lesson_plan.date,
            "overview": lesson_plan.overview,
            "objective": lesson_plan.objective,
            "subject": str(lesson_plan.subject)
        })

    response = {
        "Class": {
            "id": class_id,
            "lesson_plans": lesson_plans
        }
    }
    return jsonify(response)


@index_blueprint.route('/class/<int:class_id>/lesson_plans/<int:lesson_plan_id>/accommodations')
def class_lesson_plan_accommodations(class_id, lesson_plan_id):
    # Check if class and lesson plan exists
    class_: Class = Class.query.get_or_404(class_id)
    lesson_plan: LessonPlan = LessonPlan.query.get_or_404(lesson_plan_id)

    # Lesson plan ID needs to be of class ID
    if lesson_plan.class_id != class_.id:
        abort(404)

    lesson_plan_specific_accommodations: list[Accommodation] = Accommodation.query.filter_by(
        lesson_plan_id=lesson_plan_id).all()
    student_accommodations = []
    for accommodation in lesson_plan_specific_accommodations:
        student: Student = Student.query.filter_by(
            id=accommodation.student_id).first()
        iep = IEP.query.filter_by(student_id=accommodation.student_id).first()
        iep_object = {
            "description": iep.description,
            "disability": iep.disability
        } if iep else None
        student_accommodations.append({
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "iep": iep_object,
            "accommodation": {"text": accommodation.text, "id": accommodation.id}
        })

    response = {
        "Class": {
            "id": class_id,
            "lesson_plan": {
                "id": lesson_plan_id,
                "student_accommodations": student_accommodations
            }

        }
    }
    return jsonify(response)

### POST REQUESTS ###


'''
Admins can add classes
'''


@index_blueprint.route('/class', methods=['POST'])
def add_class():
    is_valid, error = validate_request(
        request, ['teacher_id', 'name', 'school_year'])
    if not is_valid:
        return error, 400

    if not Teacher.query.filter_by(id=request.json['teacher_id']).first():
        return {'error': 'Invalid teacher ID'}, 400

    # TODO: Will need to add some sort of error checking for school year.
    # The Class creation will throw a ValueError most likely but I would like
    # that error to be handled gracefully.

    new_class = Class(
        teacher_id=request.json['teacher_id'],
        name=request.json['name'],
        school_year=request.json['school_year']
    )

    db.session.add(new_class)
    db.session.commit()
    return {'message': 'Successfully added <Class>'}, 204


'''
Admins can add students
'''


@index_blueprint.route('/student', methods=['POST'])
def add_student():
    is_valid, error = validate_request(request, ['first_name', 'last_name'])
    if not is_valid:
        return error, 400

    new_student = Student(
        first_name=request.json['first_name'],
        last_name=request.json['last_name']
    )

    db.session.add(new_student)
    db.session.commit()
    return {'message': 'Successfully added <Student>'}, 204


'''
Admins can add teachers
'''


@index_blueprint.route('/teacher', methods=['POST'])
def add_teacher():
    is_valid, error = validate_request(
        request, ['first_name', 'last_name', 'email', 'password'])
    if not is_valid:
        return error, 400

    new_teacher = Teacher(
        first_name=request.json['first_name'],
        last_name=request.json['last_name'],
        email=request.json['email'],
        password=request.json['password']
    )

    db.session.add(new_teacher)
    db.session.commit()
    return {'message': 'Successfully added <Teacher>'}, 204


'''
Resource teachers can add IEPs
'''


@index_blueprint.route('/IEP', methods=['POST'])
def add_IEP():
    is_valid, error = validate_request(
        request, ['student_id', 'description', 'disability', 'start_date'])
    if not is_valid:
        return error, 400

    if not Student.query.filter_by(id=request.json['student_id']).first():
        return {'error': 'Invalid student ID'}, 400

    try:
        start_date = datetime.strptime(request.json['start_date'], '%Y-%m-%d')
    except ValueError as e:
        return {'error': str(e)}, 400

    new_IEP = IEP(
        student_id=request.json['student_id'],
        description=request.json['description'],
        disability=request.json['disability'],
        start_date=start_date
    )

    db.session.add(new_IEP)
    db.session.commit()
    return {'message': 'Successfully added <IEP>'}, 204


'''
Admins can enroll students (maybe teachers)
'''


@index_blueprint.route('/enrollment', methods=['POST'])
def add_enrollment():
    is_valid, error = validate_request(request, ['class_id', 'student_id'])
    if not is_valid:
        return error, 400

    if not Class.query.filter_by(id=request.json['class_id']).first():
        return {'error': 'Invalid class ID'}, 400

    if not Student.query.filter_by(id=request.json['student_id']).first():
        return {'error': 'Invalid student ID'}, 400

    new_enrollment = Enrollment(
        student_id=request.json['student_id'],
        class_id=request.json['class_id']
    )

    db.session.add(new_enrollment)
    db.session.commit()
    return {'message': 'Successfully added <Enrollment>'}, 204


'''
Teachers add lesson plans
'''


@index_blueprint.route('/lesson_plan', methods=['POST'])
def add_lesson_plan():
    is_valid, error = validate_request(
        request, ['class_id', 'name', 'date', 'overview', 'objective', 'subject'])
    if not is_valid:
        return error, 400

    is_valid, error = validate_enum(SubjectType, request.json['subject'])
    if not is_valid:
        return error, 400

    if not Class.query.filter_by(id=request.json['class_id']).first():
        return {'error': 'Invalid class ID'}, 400

    try:
        date = datetime.strptime(request.json['date'], '%Y-%m-%d')
    except ValueError as e:
        return {'error': 'Date parsing error YYYY-mm-dd'}, 400

    new_lesson_plan = LessonPlan(
        class_id=request.json['class_id'],
        name=request.json['name'],
        date=date,
        overview=request.json['overview'],
        objective=request.json['objective'],
        subject=SubjectType(request.json['subject'])
    )

    db.session.add(new_lesson_plan)
    db.session.commit()
    return {'message': 'Successfully added <LessonPlan>'}, 204


'''
Teachers add grades
'''


@index_blueprint.route('/grade', methods=['POST'])
def add_grade():
    is_valid, error = validate_request(
        request, ['student_id', 'grade_type', 'grade_value', 'date', 'subject'])
    if not is_valid:
        return error, 400

    is_valid, error = validate_enum(SubjectType, request.json['subject'])
    if not is_valid:
        return error, 400

    is_valid, error = validate_enum(GradeType, request.json['grade_type'])
    if not is_valid:
        return error, 400

    if not Student.query.filter_by(id=request.json['student_id']).first():
        return {'error': 'Invalid student ID'}, 400

    try:
        date = datetime.strptime(request.json['date'], '%Y-%m-%d')
    except ValueError as e:
        return {'error': str(e)}, 400

    # TODO: Will need to add some sort of error checking for GRADE VALUE.
    # The Grade creation will throw a ValueError most likely but I would like
    # that error to be handled gracefully.

    new_grade = Grade(
        student_id=request.json['student_id'],
        grade_type=GradeType(request.json['grade_type']),
        grade_value=request.json['grade_value'],
        date=date,
        subject=SubjectType(request.json['subject'])
    )

    db.session.add(new_grade)
    db.session.commit()
    return {'message': 'Successfully added <Grade>'}, 204


''' 
This will be called in adapt BOOST mode
Accommodations will be added through pipeline and then be
1. sent to client
2. saved to db
'''


@index_blueprint.route('/accommodation', methods=['POST'])
def add_accommodation():
    is_valid, error = validate_request(
        request, ['student_id', 'lesson_plan_id', 'text'])
    if not is_valid:
        return error, 400

    if not Student.query.filter_by(id=request.json['student_id']).first():
        return {'error': 'Invalid student ID'}, 400

    if not LessonPlan.query.filter_by(id=request.json['lesson_plan_id']).first():
        return {'error': 'Invalid lesson plan ID'}, 400

    new_accommodation = Accommodation(
        student_id=request.json['student_id'],
        lesson_plan_id=request.json['lesson_plan_id'],
        text=request.json['text']
    )

    db.session.add(new_accommodation)
    db.session.commit()
    return {'message': 'Successfully added <Accommodation>'}, 204

### PUT REQUESTS ###


'''
Admins can update classes
'''


@index_blueprint.route('/class/<int:id>', methods=['PUT'])
def update_class(id):
    class_ = Class.query.get_or_404(id)

    if request.json.get('teacher_id') and not Teacher.query.filter_by(id=request.json['teacher_id']).first():
        return {'error': 'Invalid teacher ID'}, 400

    # TODO: Will need to add some sort of error checking for school year.
    # The Class creation will throw a ValueError most likely but I would like
    # that error to be handled gracefully.

    class_.teacher_id = request.json.get('teacher_id') or class_.teacher_id
    class_.name = request.json.get('name') or class_.name
    class_.school_year = request.json.get('school_year') or class_.school_year

    db.session.commit()
    return {'message': 'Successfully updated <Class>'}, 204


'''
Admins can update students
'''


@index_blueprint.route('/student/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get_or_404(id)

    student.first_name = request.json.get('first_name') or student.first_name
    student.last_name = request.json.get('last_name') or student.last_name

    db.session.commit()
    return {'message': 'Successfully updated <Student>'}, 204


'''
Admins can update teachers
'''


@index_blueprint.route('/teacher/<int:id>', methods=['PUT'])
def update_teacher(id):
    teacher = Teacher.query.get_or_404(id)

    teacher.first_name = request.json.get('first_name') or teacher.first_name
    teacher.last_name = request.json.get('last_name') or teacher.last_name
    teacher.email = request.json.get('email') or teacher.email
    teacher.password = request.json.get('password') or teacher.password

    db.session.commit()
    return {'message': 'Successfully updated <Teacher>'}, 204


'''
Resource teachers can update IEPs
'''


@index_blueprint.route('/IEP/<int:id>', methods=['PUT'])
def update_IEP(id):
    iep = IEP.query.get_or_404(id)

    if request.json.get('student_id') and not Student.query.filter_by(id=request.json['student_id']).first():
        return {'error': 'Invalid student ID'}, 400

    if request.json.get('start_date'):
        try:
            iep.start_date = datetime.strptime(
                request.json['start_date'], '%Y-%m-%d')
        except ValueError as e:
            return {'error': 'Date parsing error YYYY-mm-dd'}, 400

    iep.student_id = request.json.get('student_id') or iep.student_id
    iep.description = request.json.get('description') or iep.description
    iep.disability = request.json.get('disability') or iep.disability

    db.session.commit()
    return {'message': 'Successfully updated <IEP>'}, 204


'''
Admins can update student enrollment (maybe teachers)
'''


@index_blueprint.route('/enrollment/<int:id>', methods=['PUT'])
def update_enrollment(id):
    enrollment = Enrollment.query.get_or_404(id)

    if request.json.get('student_id') and not Student.query.filter_by(id=request.json['student_id']).first():
        return {'error': 'Invalid student ID'}, 400

    if request.json.get('class_id') and not Class.query.filter_by(id=request.json['class_id']).first():
        return {'error': 'Invalid class ID'}, 400

    enrollment.student_id = request.json.get(
        'student_id') or enrollment.student_id
    enrollment.class_id = request.json.get('class_id') or enrollment.class_id

    db.session.commit()
    return {'message': 'Successfully updated <Enrollment>'}, 204


'''
Teachers update lesson plans
'''


@index_blueprint.route('/lesson_plan/<int:id>', methods=['PUT'])
def update_lesson_plan(id):
    lesson_plan = LessonPlan.query.get_or_404(id)

    if request.json.get('class_id') and not Class.query.filter_by(id=request.json['class_id']).first():
        return {'error': 'Invalid class ID'}, 400

    if request.json.get('date'):
        try:
            lesson_plan.date = datetime.strptime(
                request.json['date'], '%Y-%m-%d')
        except ValueError as e:
            return {'error': 'Date parsing error YYYY-mm-dd'}, 400

    if request.json.get('subject'):
        is_valid, error = validate_enum(SubjectType, request.json['subject'])
        if not is_valid:
            return error, 400
        lesson_plan.subject = SubjectType(request.json.get('subject'))

    lesson_plan.class_id = request.json.get('class_id') or lesson_plan.class_id
    lesson_plan.name = request.json.get('name') or lesson_plan.name
    lesson_plan.overview = request.json.get('overview') or lesson_plan.overview
    lesson_plan.objective = request.json.get(
        'objective') or lesson_plan.objective

    db.session.commit()
    return {'message': 'Successfully updated <LessonPlan>'}, 204


'''
Teachers update grades
'''


@index_blueprint.route('/grade/<int:id>', methods=['PUT'])
def update_grade(id):
    grade = Grade.query.get_or_404(id)

    if request.json.get('student_id') and not Student.query.filter_by(id=request.json['student_id']).first():
        return {'error': 'Invalid student ID'}, 400

    if request.json.get('date'):
        try:
            grade.date = datetime.strptime(request.json['date'], '%Y-%m-%d')
        except ValueError as e:
            return {'error': 'Date parsing error YYYY-mm-dd'}, 400

    if request.json.get('subject'):
        is_valid, error = validate_enum(SubjectType, request.json['subject'])
        if not is_valid:
            return error, 400
        grade.subject = SubjectType(request.json.get('subject'))

    if request.json.get('grade_type'):
        is_valid, error = validate_enum(GradeType, request.json['grade_type'])
        if not is_valid:
            return error, 400
        grade.grade_type = GradeType(request.json.get('grade_type'))

    # TODO: Will need to add some sort of error checking for GRADE VALUE.
    # The Grade creation will throw a ValueError most likely but I would like
    # that error to be handled gracefully.

    grade.student_id = request.json.get('student_id') or grade.student_id
    grade.grade_value = request.json.get('grade_value') or grade.grade_value

    db.session.commit()
    return {'message': 'Successfully updated <Grade>'}, 204


''' 
Teacher can modify accommodations manually
'''


@index_blueprint.route('/accommodation/<int:id>', methods=['PUT'])
def update_accommodation(id):
    accommodation = Accommodation.query.get_or_404(id)

    if request.json.get('student_id') and not Student.query.filter_by(id=request.json['student_id']).first():
        return {'error': 'Invalid student ID'}, 400

    if request.json.get('lesson_plan_id') and not LessonPlan.query.filter_by(id=request.json['lesson_plan_id']).first():
        return {'error': 'Invalid lesson plan ID'}, 400

    accommodation.student_id = request.json.get(
        'student_id') or accommodation.student_id
    accommodation.lesson_plan_id = request.json.get(
        'lesson_plan_id') or accommodation.lesson_plan_id
    accommodation.text = request.json.get('text') or accommodation.text

    db.session.commit()
    return {'message': 'Successfully updated <Accommodation>'}, 204

### DELETE REQUESTS ###


'''
Admins can delete classes
'''


@index_blueprint.route('/class/<int:id>', methods=['DELETE'])
def delete_class(id):
    class_ = Class.query.get_or_404(id)
    db.session.delete(class_)
    db.session.commit()
    return {'message': 'Successfully deleted <Class>'}, 204


'''
Admins can delete students
'''


@index_blueprint.route('/student/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return {'message': 'Successfully deleted <Student>'}, 204


'''
Admins can delete teachers
'''


@index_blueprint.route('/teacher/<int:id>', methods=['DELETE'])
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    return {'message': 'Successfully deleted <Teacher>'}, 204


'''
Resource teachers can delete IEPs
'''


@index_blueprint.route('/IEP/<int:id>', methods=['DELETE'])
def delete_IEP(id):
    iep = IEP.query.get_or_404(id)
    db.session.delete(iep)
    db.session.commit()
    return {'message': 'Successfully deleted <IEP>'}, 204


'''
Admins can delete student enrollment (maybe teachers)
'''


@index_blueprint.route('/enrollment/<int:id>', methods=['DELETE'])
def delete_enrollment(id):
    enrollment = Enrollment.query.get_or_404(id)
    db.session.delete(enrollment)
    db.session.commit()
    return {'message': 'Successfully deleted <Enrollment>'}, 204


'''
Teachers can delete lesson plans
'''


@index_blueprint.route('/lesson_plan/<int:id>', methods=['DELETE'])
def delete_lesson_plan(id):
    lesson_plan = LessonPlan.query.get_or_404(id)
    db.session.delete(lesson_plan)
    db.session.commit()
    return {'message': 'Successfully deleted <LessonPlan>'}, 204


'''
Teachers can delete grades
'''


@index_blueprint.route('/grade/<int:id>', methods=['DELETE'])
def delete_grade(id):
    grade = Grade.query.get_or_404(id)
    db.session.delete(grade)
    db.session.commit()
    return {'message': 'Successfully deleted <Grade>'}, 204


'''
Teacher can delete accommodations manually
'''


@index_blueprint.route('/accommodation/<int:id>', methods=['DELETE'])
def delete_accommodation(id):
    accommodation = Accommodation.query.get_or_404(id)
    db.session.delete(accommodation)
    db.session.commit()
    return {'message': 'Successfully deleted <Accommodation>'}, 204