from django.test import SimpleTestCase

from .services import classify_ticket


class TicketClassifierTests(SimpleTestCase):

    def test_ticket_classification(self):

        test_cases = [
            (
                "My package has not arrived",
                "",
                "DELIVERY",
                "HIGH"
            ),
            (
                "I need a payment refund",
                "",
                "BILLING",
                "HIGH"
            ),
            (
                "I cannot login to my account",
                "",
                "LOGIN",
                "MEDIUM"
            ),
            (
                "Application crash frequently",
                "",
                "BUG",
                "MEDIUM"
            ),
            (
                "Production down urgently",
                "",
                "FEATURE_REQUEST",
                "URGENT"
            ),
            (
                "Please add a dark mode feature",
                "",
                "FEATURE_REQUEST",
                "MEDIUM"
            ),
            (
                "My password is locked out",
                "",
                "LOGIN",
                "URGENT"
            ),
        ]

        for subject, body, expected_category, expected_priority in test_cases:

            with self.subTest(subject=subject):

                result = classify_ticket(subject, body)

                self.assertEqual(
                    result["category"],
                    expected_category
                )

                self.assertEqual(
                    result["priority"],
                    expected_priority
                )

    def test_body_is_also_classified(self):

        result = classify_ticket(
            "Application issue",
            "My invoice contains an incorrect charge."
        )

        self.assertEqual(result["category"], "BILLING")

    def test_case_insensitive_classification(self):

        result = classify_ticket(
            "URGENT PAYMENT REFUND",
            ""
        )

        self.assertEqual(result["category"], "BILLING")
        self.assertEqual(result["priority"], "URGENT")

    def test_category_precedence(self):

        result = classify_ticket(
            "Payment login problem",
            ""
        )

        self.assertEqual(result["category"], "BILLING")

from django.test import TestCase

from .models import Ticket
from .services import import_tickets


class TicketImportTests(TestCase):

    def test_new_ticket_import(self):

        data = [
            {
                "externalId": "EXT-100",
                "subject": "Payment refund",
                "body": "I need my payment refunded."
            }
        ]

        result = import_tickets(data)

        self.assertEqual(result["importedCount"], 1)
        self.assertEqual(result["total"], 1)

        ticket = Ticket.objects.get(external_id="EXT-100")

        self.assertEqual(ticket.category, "BILLING")
        self.assertEqual(ticket.priority, "HIGH")

        # Original prediction is retained.
        self.assertEqual(ticket.auto_category, "BILLING")

    def test_duplicate_import_does_not_create_duplicates(self):

        data = [
            {
                "externalId": "EXT-101",
                "subject": "Payment refund",
                "body": "Please refund my payment."
            }
        ]

        import_tickets(data)
        result = import_tickets(data)

        self.assertEqual(result["importedCount"], 0)
        self.assertEqual(Ticket.objects.count(), 1)

    def test_reimport_updates_ticket(self):

        import_tickets([
            {
                "externalId": "EXT-102",
                "subject": "General question",
                "body": "I have a question."
            }
        ])

        result = import_tickets([
            {
                "externalId": "EXT-102",
                "subject": "Payment refund",
                "body": "Please refund my payment."
            }
        ])

        ticket = Ticket.objects.get(external_id="EXT-102")

        self.assertEqual(ticket.subject, "Payment refund")
        self.assertEqual(ticket.category, "BILLING")
        self.assertEqual(ticket.priority, "HIGH")

        # Original prediction remains unchanged.
        self.assertEqual(ticket.auto_category, "FEATURE_REQUEST")

        self.assertEqual(result["updatedCount"], 1)

    def test_human_override_is_preserved(self):

        import_tickets([
            {
                "externalId": "EXT-103",
                "subject": "General question",
                "body": "I have a question."
            }
        ])

        ticket = Ticket.objects.get(external_id="EXT-103")

        # Simulate an agent changing the ticket.
        ticket.category = "LOGIN"
        ticket.is_human_override = True
        ticket.save(
            update_fields=["category", "is_human_override"]
        )

        result = import_tickets([
            {
                "externalId": "EXT-103",
                "subject": "Payment refund",
                "body": "Please refund my payment."
            }
        ])

        ticket.refresh_from_db()

        self.assertEqual(ticket.category, "LOGIN")
        self.assertEqual(ticket.priority, "MEDIUM")
        self.assertEqual(result["skippedOverrideCount"], 1)

        # Subject/body should still update.
        self.assertEqual(ticket.subject, "Payment refund")