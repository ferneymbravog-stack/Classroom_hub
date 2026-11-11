from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client

from .models import Category, Resource



class ClassroomHubTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Programming",
            description="Core programming topics",
        )
        cls.resource = Resource.objects.create(
            title="Python basics",
            description="Variables and functions",
            available=True,
            category=cls.category,
        )
        Resource.objects.create(
            title="Django models",
            description="Database fundamentals",
            available=False,
            category=cls.category,
        )

    def test_home_page_renders(self):
        response = self.client.get(reverse("pages:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")
        self.assertContains(response, "Welcome")

    def test_resources_page_displays_database_records(self):
        response = self.client.get(reverse("pages:resources"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/resources.html")
        self.assertContains(response, "Python basics")
        self.assertContains(response, "Django models")
        self.assertContains(response, "Coming soon")

    def test_resource_displays_related_category(self):
        response = self.client.get(reverse("pages:resources"))
        self.assertContains(response, "Category: <strong>Programming</strong>")

    def test_about_page_renders(self):
        response = self.client.get(reverse("pages:about"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/about.html")

    def test_home_navigation_links_to_resources(self):
        response = self.client.get(reverse("pages:home"))
        self.assertContains(
            response,
            f'href="{reverse("pages:resources")}"',
        )

    def test_unknown_page_returns_not_found(self):
        response = self.client.get("/not-found/")
        self.assertEqual(response.status_code, 404)

    def test_resource_updates_are_persisted(self):
        self.resource.available = False
        self.resource.save(update_fields=["available"])
        self.resource.refresh_from_db()
        self.assertFalse(self.resource.available)

    def test_category_protects_related_resources(self):
        with self.assertRaises(ProtectedError):
            self.category.delete()
        self.assertTrue(
            Category.objects.filter(pk=self.category.pk).exists()
        )

    def test_empty_catalog_shows_message(self):
        Resource.objects.all().delete()
        response = self.client.get(reverse("pages:resources"))
        self.assertContains(response, "No resources are available.")

    def test_category_reverse_relation_contains_resources(self):
        titles = set(
            self.category.resources.values_list("title", flat=True)
        )
        self.assertEqual(titles, {"Python basics", "Django models"})

    def test_available_resources_filter(self):
        response = self.client.get(reverse("pages:available_resources"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python basics")
        self.assertNotContains(response, "Django models")


class AuthenticationTests(TestCase):
    """Pruebas del Laboratorio 8: registro, sesiones y permisos."""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Programming")
        cls.resource = Resource.objects.create(
            title="Python basics", category=cls.category
        )
        User = get_user_model()
        cls.password = "ExampleTestPassword!2026"
        cls.user = User.objects.create_user(
            username="auth_user", password=cls.password
        )
        cls.reviewer = User.objects.create_user(
            username="auth_reviewer", password=cls.password
        )
        content_type = ContentType.objects.get_for_model(Resource)
        permission = Permission.objects.get(
            content_type=content_type, codename="view_resource"
        )
        group = Group.objects.create(name="Catalog reviewers")
        group.permissions.add(permission)
        cls.reviewer.groups.add(group)

    def test_signup_page_renders(self):
        response = self.client.get(reverse("pages:signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/signup.html")

    def test_login_page_renders(self):
        response = self.client.get(reverse("pages:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/login.html")

    def test_signup_creates_account(self):
        response = self.client.post(
            reverse("pages:signup"),
            {
                "username": "new_student",
                "password1": "AnotherTestPassword!2026",
                "password2": "AnotherTestPassword!2026",
            },
        )
        self.assertRedirects(response, reverse("pages:login"))
        self.assertTrue(
            get_user_model().objects.filter(username="new_student").exists()
        )

    def test_signup_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("pages:signup"),
            {
                "username": "bad_student",
                "password1": "AnotherTestPassword!2026",
                "password2": "DifferentPassword!2026",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            get_user_model().objects.filter(username="bad_student").exists()
        )

    def test_signup_creates_unprivileged_account(self):
        self.client.post(
            reverse("pages:signup"),
            {
                "username": "plain_student",
                "password1": "AnotherTestPassword!2026",
                "password2": "AnotherTestPassword!2026",
            },
        )
        account = get_user_model().objects.get(username="plain_student")
        self.assertFalse(account.is_staff)
        self.assertFalse(account.is_superuser)
        self.assertEqual(account.groups.count(), 0)

    def test_authenticated_user_is_redirected_from_signup(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("pages:signup"))
        self.assertRedirects(response, reverse("pages:dashboard"))

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            reverse("pages:login"),
            {"username": "auth_user", "password": self.password},
        )
        self.assertRedirects(response, reverse("pages:dashboard"))

    def test_login_with_invalid_credentials(self):
        response = self.client.post(
            reverse("pages:login"),
            {"username": "auth_user", "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_dashboard_redirects_anonymous_user(self):
        url = reverse("pages:dashboard")
        response = self.client.get(url)
        self.assertRedirects(
            response, reverse("pages:login") + f"?next={url}"
        )

    def test_dashboard_available_to_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("pages:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "auth_user")

    def test_dashboard_counts_visits_in_session(self):
        self.client.force_login(self.user)
        self.client.get(reverse("pages:dashboard"))
        response = self.client.get(reverse("pages:dashboard"))
        self.assertEqual(response.context["visit_count"], 2)

    def test_logout_requires_post_and_ends_session(self):
        self.client.force_login(self.user)
        self.assertEqual(
            self.client.get(reverse("pages:logout")).status_code, 405
        )
        self.client.post(reverse("pages:logout"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_review_redirects_anonymous_user(self):
        url = reverse("pages:resource-review")
        response = self.client.get(url)
        self.assertRedirects(
            response, reverse("pages:login") + f"?next={url}"
        )

    def test_review_denies_user_without_permission(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("pages:resource-review"))
        self.assertEqual(response.status_code, 403)

    def test_review_allows_reviewer(self):
        self.client.force_login(self.reviewer)
        response = self.client.get(reverse("pages:resource-review"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python basics")

    def test_resources_page_remains_public(self):
        response = self.client.get(reverse("pages:resources"))
        self.assertEqual(response.status_code, 200)

    def test_menu_shows_login_links_to_anonymous_user(self):
        response = self.client.get(reverse("pages:home"))
        self.assertContains(response, reverse("pages:login"))
        self.assertContains(response, reverse("pages:signup"))

    def test_menu_shows_logout_form_to_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("pages:home"))
        self.assertContains(response, reverse("pages:logout"))
        self.assertContains(response, "Log out")


class ResourceCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Programming",
            description="Programming resources",
        )
        cls.resource = Resource.objects.create(
            title="Python basics",
            description="Variables and functions",
            category=cls.category,
            available=True,
        )

        User = get_user_model()
        cls.reader = User.objects.create_user(
            username="crud_reader",
            password="ExampleTestPassword!2026",
        )
        cls.editor = User.objects.create_user(
            username="crud_editor",
            password="ExampleTestPassword!2026",
        )
        cls.reviewer = User.objects.create_user(
            username="crud_reviewer",
            password="ExampleTestPassword!2026",
        )

        content_type = ContentType.objects.get_for_model(Resource)
        all_permissions = Permission.objects.filter(
            content_type=content_type,
            codename__in=[
                "view_resource",
                "add_resource",
                "change_resource",
                "delete_resource",
            ],
        )
        editors = Group.objects.create(name="Catalog editors")
        editors.permissions.add(*all_permissions)
        cls.editor.groups.add(editors)

        review_permission = Permission.objects.get(
            content_type=content_type,
            codename="view_resource",
        )
        reviewers = Group.objects.create(name="Catalog reviewers")
        reviewers.permissions.add(review_permission)
        cls.reviewer.groups.add(reviewers)

    def resource_data(self, **overrides):
        values = {
            "title": "Database testing",
            "description": "Database integration practice",
            "resource_type": "Guide",
            "category": self.category.pk,
            "available": "on",
        }
        values.update(overrides)
        return values

    def test_resource_detail_is_public(self):
        url = reverse("pages:resource-detail", args=[self.resource.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python basics")
        self.assertContains(response, "Programming")

    def test_unknown_resource_detail_returns_404(self):
        url = reverse("pages:resource-detail", args=[999999])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_public_catalog_links_to_resource_detail(self):
        response = self.client.get(reverse("pages:resources"))
        detail_url = reverse(
            "pages:resource-detail", args=[self.resource.pk]
        )

        self.assertContains(response, f'href="{detail_url}"')

    def test_create_redirects_anonymous_user_to_login(self):
        url = reverse("pages:resource-create")

        response = self.client.get(url)

        expected = reverse("pages:login") + f"?next={url}"
        self.assertRedirects(response, expected)

    def test_create_denies_authenticated_reader(self):
        self.client.force_login(self.reader)

        response = self.client.get(reverse("pages:resource-create"))

        self.assertEqual(response.status_code, 403)

    def test_reviewer_cannot_create_resource(self):
        self.client.force_login(self.reviewer)

        response = self.client.get(reverse("pages:resource-create"))

        self.assertEqual(response.status_code, 403)

    def test_editor_can_open_create_form(self):
        self.client.force_login(self.editor)

        response = self.client.get(reverse("pages:resource-create"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/resource_form.html")

    def test_reader_cannot_create_resource_via_post(self):
        self.client.force_login(self.reader)

        response = self.client.post(
            reverse("pages:resource-create"),
            self.resource_data(),
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            Resource.objects.filter(title="Database testing").exists()
        )

    def test_editor_can_create_resource(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("pages:resource-create"),
            self.resource_data(),
        )

        self.assertRedirects(response, reverse("pages:resources"))
        self.assertTrue(
            Resource.objects.filter(title="Database testing").exists()
        )

    def test_create_rejects_short_title(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("pages:resource-create"),
            self.resource_data(title="ab"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "title",
            "Title must contain at least 3 characters.",
        )
        self.assertFalse(Resource.objects.filter(title="ab").exists())

    def test_create_rejects_unknown_category(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("pages:resource-create"),
            self.resource_data(category=999999),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("category", response.context["form"].errors)
        self.assertFalse(
            Resource.objects.filter(title="Database testing").exists()
        )

    def test_form_exposes_only_expected_fields(self):
        self.client.force_login(self.editor)

        response = self.client.get(reverse("pages:resource-create"))
        field_names = list(response.context["form"].fields)

        self.assertEqual(
            field_names,
            [
                "title",
                "description",
                "resource_type",
                "category",
                "available",
            ],
        )
        self.assertNotIn("created_at", field_names)

    def test_update_redirects_anonymous_user_to_login(self):
        url = reverse("pages:resource-update", args=[self.resource.pk])

        response = self.client.get(url)

        self.assertRedirects(
            response,
            reverse("pages:login") + f"?next={url}",
        )

    def test_update_denies_authenticated_reader(self):
        self.client.force_login(self.reader)
        url = reverse("pages:resource-update", args=[self.resource.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_reader_cannot_update_resource_via_post(self):
        self.client.force_login(self.reader)
        url = reverse(
            "pages:resource-update", args=[self.resource.pk]
        )

        response = self.client.post(
            url,
            self.resource_data(title="Forbidden update"),
        )

        self.assertEqual(response.status_code, 403)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.title, "Python basics")

    def test_editor_can_open_update_form(self):
        self.client.force_login(self.editor)
        url = reverse("pages:resource-update", args=[self.resource.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/resource_form.html")
        self.assertContains(response, "Python basics")

    def test_editor_can_update_existing_resource(self):
        self.client.force_login(self.editor)
        old_id = self.resource.pk
        url = reverse("pages:resource-update", args=[old_id])

        response = self.client.post(
            url,
            self.resource_data(
                title="Updated Python resource",
                available="",
            ),
        )

        self.assertRedirects(response, reverse("pages:resources"))
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.pk, old_id)
        self.assertEqual(self.resource.title, "Updated Python resource")
        self.assertFalse(self.resource.available)

    def test_invalid_update_keeps_existing_values(self):
        self.client.force_login(self.editor)
        old_title = self.resource.title
        url = reverse(
            "pages:resource-update", args=[self.resource.pk]
        )

        response = self.client.post(
            url,
            self.resource_data(title="ab"),
        )

        self.assertEqual(response.status_code, 200)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.title, old_title)

    def test_delete_redirects_anonymous_user_to_login(self):
        url = reverse(
            "pages:resource-delete", args=[self.resource.pk]
        )

        response = self.client.get(url)

        self.assertRedirects(
            response,
            reverse("pages:login") + f"?next={url}",
        )

    def test_delete_denies_authenticated_reader(self):
        self.client.force_login(self.reader)
        url = reverse(
            "pages:resource-delete", args=[self.resource.pk]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_reviewer_cannot_delete_resource(self):
        self.client.force_login(self.reviewer)
        url = reverse(
            "pages:resource-delete", args=[self.resource.pk]
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Resource.objects.filter(pk=self.resource.pk).exists()
        )

    def test_delete_get_only_shows_confirmation(self):
        self.client.force_login(self.editor)
        url = reverse(
            "pages:resource-delete", args=[self.resource.pk]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "pages/resource_confirm_delete.html"
        )
        self.assertTrue(
            Resource.objects.filter(pk=self.resource.pk).exists()
        )

    def test_delete_post_removes_resource(self):
        self.client.force_login(self.editor)
        url = reverse(
            "pages:resource-delete", args=[self.resource.pk]
        )

        response = self.client.post(url)

        self.assertRedirects(response, reverse("pages:resources"))
        self.assertFalse(
            Resource.objects.filter(pk=self.resource.pk).exists()
        )

    def test_unknown_resource_update_returns_404_for_editor(self):
        self.client.force_login(self.editor)
        url = reverse("pages:resource-update", args=[999999])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_unknown_resource_delete_returns_404_for_editor(self):
        self.client.force_login(self.editor)
        url = reverse("pages:resource-delete", args=[999999])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_reader_does_not_see_edit_or_delete_links(self):
        self.client.force_login(self.reader)
        url = reverse(
            "pages:resource-detail", args=[self.resource.pk]
        )

        response = self.client.get(url)

        self.assertNotContains(response, "Edit resource")
        self.assertNotContains(response, "Delete resource")

    def test_editor_can_manage_without_staff_status(self):
        self.client.force_login(self.editor)

        self.assertFalse(self.editor.is_staff)
        self.assertFalse(self.editor.is_superuser)
        self.assertTrue(self.editor.has_perm("pages.add_resource"))
        self.assertTrue(self.editor.has_perm("pages.change_resource"))
        self.assertTrue(self.editor.has_perm("pages.delete_resource"))

    def test_editor_can_still_open_review_page(self):
        self.client.force_login(self.editor)

        response = self.client.get(reverse("pages:resource-review"))

        self.assertEqual(response.status_code, 200)

    def test_public_catalog_reflects_new_resource(self):
        Resource.objects.create(
            title="New catalog resource",
            category=self.category,
        )

        response = self.client.get(reverse("pages:resources"))

        self.assertContains(response, "New catalog resource")

    def test_post_without_csrf_is_rejected(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.editor)

        response = csrf_client.post(
            reverse("pages:resource-create"),
            self.resource_data(),
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            Resource.objects.filter(title="Database testing").exists()
        )
