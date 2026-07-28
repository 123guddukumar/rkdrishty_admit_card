from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from PIL import Image
import os
import io
from datetime import date
from admit_cards.models import Student, BulkTask
from admit_cards.generator import crop_and_resize_photo, generate_admit_card_files
from coordinates import COORDINATES

class AdmitCardSystemTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test student
        self.student = Student.objects.create(
            name="Rahul Kumar",
            father_name="Ram Kumar",
            mother_name="Sita Devi",
            student_class="12th",
            batch="Batch 2026",
            aadhaar_number="1234 5678 9012",
            registration_number="REG-TEST-101",
            mobile_number="9876543210",
            dob=date(2008, 5, 15),
            gender="Male",
            address="123 Street, Champaran, Bihar"
        )
        
        # Create dummy student photo
        photo_io = io.BytesIO()
        Image.new('RGB', (400, 600), color='blue').save(photo_io, format='JPEG')
        photo_io.seek(0)
        self.student.photo.save('test_photo.jpg', photo_io, save=True)

    def tearDown(self):
        # Clean up files created during test
        if self.student.photo:
            self.student.photo.delete(save=False)
        if self.student.card_jpg:
            self.student.card_jpg.delete(save=False)
        if self.student.card_pdf:
            self.student.card_pdf.delete(save=False)
        
        # Clean up files on disk if any
        media_gen_dir = os.path.join(settings_media_root(), 'generated_cards')
        if os.path.exists(media_gen_dir):
            for f in os.listdir(media_gen_dir):
                if 'REG-TEST-101' in f:
                    try:
                        os.remove(os.path.join(media_gen_dir, f))
                    except OSError:
                        pass

    def test_coordinates_config_validity(self):
        """Verify that all required coordinate keys are present and correctly formatted."""
        required_keys = [
            "name", "father", "mother", "class", "aadhaar", "registration",
            "mobile", "dob", "address", "photo", "male_checkbox", "female_checkbox"
        ]

        for key in required_keys:
            self.assertIn(key, COORDINATES)
            coords = COORDINATES[key]
            self.assertEqual(len(coords), 2)
            self.assertIsInstance(coords[0], int)
            self.assertIsInstance(coords[1], int)

    def test_crop_and_resize_photo(self):
        """Test the PIL intelligent crop & resize logic with wide and tall images."""
        # Tall image (width < height)
        tall_img = io.BytesIO()
        Image.new('RGB', (200, 400), color='red').save(tall_img, format='JPEG')
        tall_img.seek(0)
        
        resized_tall = crop_and_resize_photo(tall_img, 237, 277)
        self.assertEqual(resized_tall.size, (237, 277))

        # Wide image (width > height)
        wide_img = io.BytesIO()
        Image.new('RGB', (600, 300), color='green').save(wide_img, format='JPEG')
        wide_img.seek(0)
        
        resized_wide = crop_and_resize_photo(wide_img, 237, 277)
        self.assertEqual(resized_wide.size, (237, 277))

    def test_generate_card_files(self):
        """Test that the Pillow generator successfully runs and returns files."""
        # Use our test student
        jpg_content, pdf_content = generate_admit_card_files(self.student)
        
        self.assertIsNotNone(jpg_content)
        self.assertIsNotNone(pdf_content)
        self.assertTrue(jpg_content.name.endswith('.jpg'))
        self.assertTrue(pdf_content.name.endswith('.pdf'))

    def test_apis(self):
        """Verify the JSON REST API responses."""
        # 1. Test single generate API
        response = self.client.post(reverse('generate_card_api'), {
            'student_id': self.student.id
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('jpg_url', data)
        self.assertIn('pdf_url', data)

        # Reload student and check card files generated
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_generated)
        self.assertTrue(os.path.exists(self.student.card_jpg.path))

        # 2. Test download endpoint
        dl_response = self.client.get(reverse('download_card_api'), {
            'student_id': self.student.id,
            'format': 'pdf'
        })
        self.assertEqual(dl_response.status_code, 200)
        self.assertEqual(dl_response['content-type'], 'application/pdf')
        dl_response.close()


def settings_media_root():
    from django.conf import settings
    return settings.MEDIA_ROOT
