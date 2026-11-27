import re
from django.db import transaction

from .models import Ticket

def contains_keyword(text, keywords):
    """
    Checks whether any keyword or phrase exists
    as a complete word/phrase in the given text.
    """

    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword) + r"\b"

        if re.search(pattern, text):
            return True

    return False


def classify_ticket(subject, body):

    # Combine subject and body.
    text = f"{subject or ''} {body or ''}".lower()

    # 1. Determine category.

    if contains_keyword(text, [
        "refund",
        "invoice",
        "charge",
        "payment"
    ]):
        category = "BILLING"

    elif contains_keyword(text, [
        "password",
        "2fa",
        "sign in",
        "locked out",
        "login"
    ]):
        category = "LOGIN"

    elif contains_keyword(text, [
        "package",
        "arrived",
        "shipping",
        "tracking",
        "delivery"
    ]):
        category = "DELIVERY"

    elif contains_keyword(text, [
        "crash",
        "error",
        "500",
        "exception",
        "broken"
    ]):
        category = "BUG"

    else:
        category = "FEATURE_REQUEST"

    # 2. Determine priority independently.

    if contains_keyword(text, [
        "urgent",
        "production down",
        "locked out"
    ]):
        priority = "URGENT"

    elif contains_keyword(text, [
        "error",
        "refund",
        "not arrived"
    ]):
        priority = "HIGH"

    else:
        priority = "MEDIUM"

    # 3. Return both results.

    return {
        "category": category,
        "priority": priority
    }

@transaction.atomic
def import_tickets(tickets):

    imported_count = 0
    updated_count = 0
    skipped_override_count = 0

    for item in tickets:

        external_id = item["externalId"]
        subject = item["subject"].strip()
        body = item["body"].strip()

        # Run automatic classification.
        classification = classify_ticket(subject, body)

        # Find the ticket or create it if it doesn't exist.
        ticket, created = Ticket.objects.get_or_create(
            external_id=external_id,
            defaults={
                "subject": subject,
                "body": body,
                "auto_category": classification["category"],
                "category": classification["category"],
                "priority": classification["priority"],
            }
        )

        # New ticket.
        if created:
            imported_count += 1
            continue

        # Lock an existing ticket before modifying it.
        ticket = Ticket.objects.select_for_update().get(
            pk=ticket.pk
        )

        changed_fields = []

        # Update subject if changed.
        if ticket.subject != subject:
            ticket.subject = subject
            changed_fields.append("subject")

        # Update body if changed.
        if ticket.body != body:
            ticket.body = body
            changed_fields.append("body")

        # Protect human overrides.
        if ticket.is_human_override:

            skipped_override_count += 1

        else:

            # Update automatically classified category.
            if ticket.category != classification["category"]:
                ticket.category = classification["category"]
                changed_fields.append("category")

            # Update priority.
            if ticket.priority != classification["priority"]:
                ticket.priority = classification["priority"]
                changed_fields.append("priority")

        # Save only if something actually changed.
        if changed_fields:

            ticket.save(
                update_fields=changed_fields + ["updated_at"]
            )

            updated_count += 1

    return {
        "importedCount": imported_count,
        "updatedCount": updated_count,
        "skippedOverrideCount": skipped_override_count,
        "total": len(tickets)
    }