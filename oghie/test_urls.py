from rest_framework import status
from rest_framework.test import APITestCase


class ApiDocsTests(APITestCase):
    """Guards the API's docs landing page and schema endpoints.

    The root URL used to serve a plain JSON route map; it now serves
    interactive Swagger UI, with that route map moved to /api/.
    """

    def test_root_serves_swagger_ui(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'swagger-ui', response.content)

    def test_schema_endpoint_returns_openapi_document(self):
        response = self.client.get('/api/schema/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'openapi', response.content)

    def test_redoc_endpoint_is_served(self):
        response = self.client.get('/api/docs/redoc/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_root_still_serves_the_route_map(self):
        response = self.client.get('/api/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['schema'], '/api/schema/')
        self.assertEqual(response.json()['products'], '/api/products/')

    def test_docs_endpoints_are_public(self):
        for path in ('/', '/api/schema/', '/api/docs/redoc/'):
            response = self.client.get(path)
            self.assertNotEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f'{path} should not require authentication',
            )
