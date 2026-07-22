from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from catalog.models import Product, BookTemplate, PageTemplate
from books.models import PreviewRequest, PreviewResult, ChildFace

class PreviewAPITests(TestCase):
    def setUp(self):
        # Create a product and a book template for testing
        self.product = Product.objects.create(
            title="Personalized Adventure",
            description="An exciting custom journey",
            slug="personalized-adventure",
            price=29.99
        )
        self.book_template = BookTemplate.objects.create(
            product=self.product,
            title="The Lost Toy",
            description="Help find the lost toy",
            age_group="3-5"
        )
        # Create page templates
        self.page_1 = PageTemplate.objects.create(
            book_template=self.book_template,
            page_number=1,
            story_text="Once upon a time...",
            image="page_1.png",
            is_preview=True
        )
        self.page_2 = PageTemplate.objects.create(
            book_template=self.book_template,
            page_number=2,
            story_text="Then something happened...",
            image="page_2.png",
            is_preview=False
        )

        # Create mock images for testing uploads
        self.mock_image_1 = SimpleUploadedFile("face1.png", b"file_content_1", content_type="image/png")
        self.mock_image_2 = SimpleUploadedFile("face2.png", b"file_content_2", content_type="image/png")
        self.mock_image_3 = SimpleUploadedFile("face3.png", b"file_content_3", content_type="image/png")

    def test_create_preview_success(self):
        url = reverse('books:create_preview')
        data = {
            'book_template_id': self.book_template.id,
            'contact_email': 'leo@example.com',
            'child_name': 'Leo',
            'child_age': 4,
            'child_gender': 'boy',
            'photo1': self.mock_image_1,
            'photo2': self.mock_image_2,
            'photo3': self.mock_image_3,
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        
        resp_data = response.json()
        self.assertIn('preview_request_id', resp_data)
        self.assertEqual(resp_data['status'], 'pending')
        
        # Verify PreviewRequest exists
        preview_req = PreviewRequest.objects.get(id=resp_data['preview_request_id'])
        self.assertEqual(preview_req.contact_email, 'leo@example.com')
        self.assertEqual(preview_req.child_name, 'Leo')
        self.assertEqual(preview_req.child_age, 4)
        self.assertEqual(preview_req.child_gender, 'boy')
        self.assertEqual(preview_req.faces.count(), 3)
 
    def test_create_preview_missing_parameters(self):
        url = reverse('books:create_preview')
        data = {
            'book_template_id': self.book_template.id,
            'contact_email': 'leo@example.com',
            'child_name': 'Leo',
            # Missing child_age and child_gender
            'photo1': self.mock_image_1,
            'photo2': self.mock_image_2,
            'photo3': self.mock_image_3,
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('details', response.json())
        self.assertIn('child_age', response.json()['details'])
        self.assertIn('child_gender', response.json()['details'])
 
    def test_create_preview_invalid_photo_count(self):
        url = reverse('books:create_preview')
        data = {
            'book_template_id': self.book_template.id,
            'contact_email': 'leo@example.com',
            'child_name': 'Leo',
            'child_age': 4,
            'child_gender': 'neutral',
            'photo1': self.mock_image_1,
            'photo2': self.mock_image_2,
            # Missing photo3
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Exactly 3 photos are required. Received 2.')

    @patch('books.views.process_preview_request_task.delay')
    def test_start_preview(self, mock_celery_task):
        # Create a PreviewRequest first
        preview_req = PreviewRequest.objects.create(
            book_template=self.book_template,
            child_name='Leo',
            child_age=4,
            child_gender='boy'
        )
        
        url = reverse('books:start_preview', kwargs={'preview_request_id': preview_req.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'pending')
        
        # Verify Celery task was triggered
        mock_celery_task.assert_called_once_with(str(preview_req.id))

    def test_get_preview_status_not_completed(self):
        preview_req = PreviewRequest.objects.create(
            book_template=self.book_template,
            child_name='Leo',
            child_age=4,
            child_gender='boy',
            status='generating'
        )
        
        url = reverse('books:get_preview_status', kwargs={'preview_request_id': preview_req.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        self.assertEqual(resp_data['status'], 'generating')
        self.assertEqual(resp_data['pages'], [])

    def test_get_preview_status_completed(self):
        preview_req = PreviewRequest.objects.create(
            book_template=self.book_template,
            child_name='Leo',
            child_age=4,
            child_gender='boy',
            status='completed'
        )
        
        # Create a PreviewResult
        mock_output = SimpleUploadedFile("out1.png", b"output_bytes", content_type="image/png")
        result = PreviewResult.objects.create(
            preview_request=preview_req,
            page_template=self.page_1,
            page_number=1
        )
        result.raw_image.save("out1.png", mock_output)
        
        url = reverse('books:get_preview_status', kwargs={'preview_request_id': preview_req.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        self.assertEqual(resp_data['status'], 'completed')
        self.assertEqual(len(resp_data['pages']), 1)
        self.assertEqual(resp_data['pages'][0]['page_number'], 1)
        self.assertIn('/media/previews/pages/', resp_data['pages'][0]['image_url'])

        # Clean up files generated during test
        result.raw_image.delete()

    @patch('books.processing.ComfyUIClient')
    def test_process_preview_request_logic(self, MockComfyUIClient):
        # Setup mock client
        mock_client_instance = MockComfyUIClient.return_value
        import os
        mock_client_instance.upload_image.side_effect = lambda f: os.path.basename(f.name) + "_uploaded"
        mock_client_instance.run_workflow.return_value = (b"fake_image_bytes", "generated_out.png")

        # Create PreviewRequest and ChildFaces
        preview_req = PreviewRequest.objects.create(
            book_template=self.book_template,
            contact_email='leo@example.com',
            child_name='Leo',
            child_age=4,
            child_gender='boy',
            status='pending'
        )
        ChildFace.objects.create(preview_request=preview_req, image=self.mock_image_1)
        ChildFace.objects.create(preview_request=preview_req, image=self.mock_image_2)
        ChildFace.objects.create(preview_request=preview_req, image=self.mock_image_3)

        # Let's set a mask image name to test mask input mapping
        self.page_1.mask_image = "mask_1.png"
        self.page_1.save()

        from books.processing import process_preview_request
        process_preview_request(preview_req)

        # Refresh from db
        preview_req.refresh_from_db()
        self.assertEqual(preview_req.status, 'completed')
        self.assertEqual(preview_req.results.count(), 1)
        
        # Verify result was saved
        result = preview_req.results.first()
        self.assertEqual(result.page_number, 1)
        self.assertTrue(result.raw_image)
        result.raw_image.delete() # Clean up

        # Verify ComfyUI was called with Node 8 and Node 28 inputs correctly populated
        self.assertEqual(mock_client_instance.run_workflow.call_count, 1)
        called_prompt = mock_client_instance.run_workflow.call_args[0][0]
        self.assertEqual(called_prompt["8"]["inputs"]["image"], "page_1.png_uploaded")
        self.assertEqual(called_prompt["28"]["inputs"]["image"], "mask_1.png_uploaded")
        
        faces = list(preview_req.faces.all().order_by('id'))
        self.assertEqual(called_prompt["5"]["inputs"]["image"], os.path.basename(faces[0].image.name) + "_uploaded")
        self.assertEqual(called_prompt["23"]["inputs"]["image"], os.path.basename(faces[1].image.name) + "_uploaded")
        self.assertEqual(called_prompt["26"]["inputs"]["image"], os.path.basename(faces[2].image.name) + "_uploaded")

