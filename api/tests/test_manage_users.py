from django.test import TestCase
from django.contrib.auth import get_user_model


class UserManagerTest(TestCase):
    def setUp(self) -> None:
        self.User = get_user_model()
        
    def test_create_user(self) -> None:
        user = self.User.objects.create_user(
            username='normal@user.com',
            password='password',
        )
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'normal@user.com')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self) -> None:
        super_user = self.User.objects.create_superuser(
            username='super@user.com',
            password='password',
        )
        
        self.assertIsNotNone(super_user)
        self.assertEqual(super_user.username, 'super@user.com')
        self.assertTrue(super_user.is_staff)
        self.assertTrue(super_user.is_superuser)
 