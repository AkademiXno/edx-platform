"""
Test grading event across apps.
"""
# pylint: disable=protected-access

from capa.tests.response_xml_factory import MultipleChoiceResponseXMLFactory
from courseware.models import StudentModule
from crum import set_current_request
import json
from mock import patch
from uuid import uuid4

from courseware.tests.test_submitting_problems import ProblemSubmissionTestMixin
from lms.djangoapps.course_blocks.api import get_course_blocks
from lms.djangoapps.instructor.enrollment import reset_student_attempts
from openedx.core.djangolib.testing.utils import get_mock_request
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.tests.django_utils import SharedModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from ...new.subsection_grade import SubsectionGradeFactory

from student.models import CourseEnrollment
from student.tests.factories import UserFactory


class GradeEventIntegrationTest(ProblemSubmissionTestMixin, SharedModuleStoreTestCase):
    @classmethod
    def setUpClass(cls):
        super(GradeEventIntegrationTest, cls).setUpClass()
        cls.course = CourseFactory.create()
        cls.chapter = ItemFactory.create(
            parent=cls.course,
            category="chapter",
            display_name="Test Chapter"
        )
        cls.sequence = ItemFactory.create(
            parent=cls.chapter,
            category='sequential',
            display_name="Test Sequential 1",
            graded=True,
            format="Homework"
        )
        cls.vertical = ItemFactory.create(
            parent=cls.sequence,
            category='vertical',
            display_name='Test Vertical 1'
        )
        problem_xml = MultipleChoiceResponseXMLFactory().build_xml(
            question_text='The correct answer is Choice 3',
            choices=[False, False, True, False],
            choice_names=['choice_0', 'choice_1', 'choice_2', 'choice_3']
        )
        cls.problem = ItemFactory.create(
            parent=cls.vertical,
            category="problem",
            display_name="Test Problem",
            data=problem_xml
        )

    def setUp(self):
        super(GradeEventIntegrationTest, self).setUp()
        self.request = get_mock_request(UserFactory())
        self.student = self.request.user
        self.client.login(username=self.request.user.username, password="test")
        CourseEnrollment.enroll(self.request.user, self.course.id)
        course_structure = get_course_blocks(self.request.user, self.course.location)
        self.subsection_factory = SubsectionGradeFactory(
            self.request.user,
            course_structure=course_structure,
            course=self.course,
        )
        self.instructor = UserFactory.create(is_staff=True, username=u'test_instructor', password=u'test')

    @patch('lms.djangoapps.grades.signals.handlers.tracker')
    @patch('lms.djangoapps.instructor.enrollment.uuid4')
    @patch('lms.djangoapps.instructor.enrollment.tracker')
    @patch('lms.djangoapps.grades.models.tracker')
    def test_delete_student_state_events(self, models_tracker, enrollment_tracker, enrollment_uuid, handlers_tracker):
        enrollment_uuid.return_value = uuid4()
        # submit answer
        self.module_to_reset = StudentModule.objects.create(
            student=self.student,
            course_id=self.course.id,
            module_state_key=self.problem.location,
            state=json.dumps({'attempts': 10}),
        )
        self.submit_question_answer(u'problem', {u'2_1': u'Correct'})
        # delete state
        set_current_request(self.request)
        reset_student_attempts(self.course.id, self.student, self.problem.location, self.instructor, delete_module=True)
        # check logging
        enrollment_tracker.emit.assert_called_with(
            u'edx.grades.problem.state_deleted',
            {
                'user_id': unicode(self.student.id),
                'course_id': unicode(self.course.id),
                'problem_id': unicode(self.problem.location),
                'instructor_id': unicode(self.instructor.username),
                'grade_update_root_id': unicode(enrollment_uuid.return_value),
                'grade_update_root_type': u'edx.grades.problem.state_deleted',
            }
        )

        handlers_tracker.emit.assert_called_with(
            u'edx.grades.problem.submitted',
            {
                'user_id': unicode(self.student.id),
                'course_id': unicode(self.course.id),
                'problem_id': unicode(self.problem.location),
                'grade_update_root_id': unicode(enrollment_uuid.return_value),
                'grade_update_root_type': u'edx.grades.problem.state_deleted',
            }
        )

        # re-retrieve the course from the modulestore to get
        # most recent edit timestamp
        course = modulestore().get_course(self.course.id, depth=0)
        models_tracker.emit.assert_called_with(
            u'edx.grades.course.grade_calculated',
            {
                'course_version': u'',
                'percent_grade': 0.0,
                'grading_policy_hash': u'ChVp0lHGQGCevD0t4njna/C44zQ=',
                'user_id': unicode(self.student.id),
                'letter_grade': u'',
                'grade_update_root_id': unicode(enrollment_uuid.return_value),
                'grade_update_root_type': u'edx.grades.problem.state_deleted',
                'course_id': unicode(self.course.id),
                'course_edited_timestamp': unicode(course.subtree_edited_on),
            }
        )
