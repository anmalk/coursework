from django.test import TestCase
from .models import Event, Participant
from .views import TotalParticipantsCalculator, AverageAgeCalculator, GenderDistributionCalculator, UniversityDistributionCalculator, FacultyDistributionCalculator, CourseDistributionCalculator, GroupDistributionCalculator, MinAgeCalculator, MaxAgeCalculator
from datetime import date

class StatisticCalculatorTest(TestCase):

    def setUp(self):
        # Create an Event instance
        self.event = Event.objects.create(
            name='Test Event',
            max_participants=10,
            current_participants=5,
            date=date(2025, 1, 13),
            place='Test Place',
            description='Test Description',
            event_type='conference'
        )
        # Create Participant instances
        self.participant1 = Participant.objects.create(
            event=self.event,
            full_name="John Doe",
            university="Test University",
            faculty="Test Faculty",
            course="2",
            group="A",
            gender="Male",
            email="john.doe@example.com",
            phone="123456789",
            birth_date=date(2000, 1, 1)
        )
        self.participant2 = Participant.objects.create(
            event=self.event,
            full_name="Jane Smith",
            university="Test University",
            faculty="Test Faculty",
            course="3",
            group="B",
            gender="Female",
            email="jane.smith@example.com",
            phone="987654321",
            birth_date=date(2001, 1, 1)
        )

    def test_total_participants_calculator(self):
        calculator = TotalParticipantsCalculator()
        result = calculator.calculate(self.event.participants.all())
        self.assertEqual(result, 2)

    def test_average_age_calculator(self):
        calculator = AverageAgeCalculator()
        result = calculator.calculate(self.event.participants.all())
        # Age calculation: (2025 - 2000) + (2025 - 2001) / 2 = (25 + 24) / 2 = 24.5
        self.assertEqual(result, 24.5)

    def test_gender_distribution_calculator(self):
        calculator = GenderDistributionCalculator()
        result = calculator.calculate(self.event.participants.all())
        self.assertCountEqual(result, [
            {'gender': 'Male', 'count': 1},
            {'gender': 'Female', 'count': 1}
        ])

    def test_university_distribution_calculator(self):
        calculator = UniversityDistributionCalculator()
        result = calculator.calculate(self.event.participants.all())
        self.assertEqual(result, [
            {'university': 'Test University', 'count': 2}
        ])

    def test_faculty_distribution_calculator(self):
        calculator = FacultyDistributionCalculator()
        result = calculator.calculate(self.event.participants.all())
        self.assertEqual(result, [
            {'faculty': 'Test Faculty', 'count': 2}
        ])

    def test_course_distribution_calculator(self):
        calculator = CourseDistributionCalculator()
        result = calculator.calculate(self.event.participants.all())
        self.assertEqual(result, [
            {'course': '2', 'count': 1},
            {'course': '3', 'count': 1}
        ])

    def test_group_distribution_calculator(self):
        calculator = GroupDistributionCalculator()
        result = calculator.calculate(self.event.participants.all())
        self.assertEqual(result, [
            {'group': 'A', 'count': 1},
            {'group': 'B', 'count': 1}
        ])

    def test_min_age_calculator(self):
        calculator = MinAgeCalculator()
        result = calculator.calculate(self.event.participants.all())
        # The minimum age is 24 (2025 - 2001)
        self.assertEqual(result, 24)

    def test_max_age_calculator(self):
        calculator = MaxAgeCalculator()
        result = calculator.calculate(self.event.participants.all())
        # The maximum age is 25 (2025 - 2000)
        self.assertEqual(result, 25)

    def test_empty_participant_list(self):
        # Create an event with no participants
        event_empty = Event.objects.create(
            name='Empty Event',
            max_participants=10,
            current_participants=0,
            date=date(2025, 1, 13),
            place='Empty Place',
            description='No Participants',
            event_type='conference'
        )

        calculator = TotalParticipantsCalculator()
        result = calculator.calculate(event_empty.participants.all())
        self.assertEqual(result, 0)

        calculator = AverageAgeCalculator()
        result = calculator.calculate(event_empty.participants.all())
        self.assertEqual(result, 0)

        calculator = MinAgeCalculator()
        result = calculator.calculate(event_empty.participants.all())
        self.assertEqual(result, 0)

        calculator = MaxAgeCalculator()
        result = calculator.calculate(event_empty.participants.all())
        self.assertEqual(result, 0)
