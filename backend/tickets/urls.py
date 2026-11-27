from django.urls import path
from .views import TicketImportView

urlpatterns = [
    path(
        "tickets/import",
        TicketImportView.as_view(),
        name="ticket-import"
    ),
]