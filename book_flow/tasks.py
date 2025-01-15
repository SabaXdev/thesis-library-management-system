import logging
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mass_mail
from django.conf import settings
from book_flow.models import BorrowHistory

logger = logging.getLogger(__name__)


@shared_task
def remind_users_overdue_books():
    try:
        now = timezone.now()
        overdue_borrowings = BorrowHistory.objects.filter(due_date__lt=now, returned=False)

        emails = []
        for borrow in overdue_borrowings:
            subject = f'Reminder: Book Overdue - "{borrow.book.title}"'
            message = f'Dear {borrow.borrower.full_name},\n\n'
            message += f'This is a friendly reminder that the book "{borrow.book.title}" is overdue for return.\n'
            message += 'Please return the book as soon as possible to avoid any penalties.\n\n'
            message += 'Thank you for your cooperation.'
            from_email = settings.EMAIL_HOST_USER
            recipient = borrow.borrower.email

            emails.append((subject, message, from_email, [recipient]))
        send_mass_mail(tuple(emails))
        logger.info("Reminder emails for overdue books sent successfully.")
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")


@shared_task
def remind_users_due_books():
    try:
        now = timezone.now()
        # Calculate start and end of tomorrow
        tomorrow_start = (now + timezone.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_after_tomorrow_start = (tomorrow_start + timezone.timedelta(days=1))

        # Fetch borrowings due tomorrow
        due_borrowings = BorrowHistory.objects.filter(
            due_date__gte=tomorrow_start,
            due_date__lt=day_after_tomorrow_start,
            returned=False
        )

        if not due_borrowings:
            logger.info("No books due tomorrow.")
            return

        emails = []
        for borrow in due_borrowings:
            subject = f'Reminder: Book Due Tomorrow - "{borrow.book.title}"'
            message = f'Dear {borrow.borrower.full_name},\n\n'
            message += f'This is a reminder that the book "{borrow.book.title}" is due for return tomorrow ({borrow.due_date.strftime("%Y-%m-%d")}).\n'
            message += 'Please make necessary arrangements to return the book on time to avoid any penalties.\n\n'
            message += 'Thank you for your cooperation.'

            from_email = settings.EMAIL_HOST_USER
            recipient = borrow.borrower.email

            emails.append((subject, message, from_email, [recipient]))

        if emails:
            send_mass_mail(tuple(emails))
            logger.info("Reminder emails for due books sent successfully.")
        else:
            logger.info("No due books found for reminders.")

    except Exception as e:
        logger.error(f"Error sending reminder emails for due books: {str(e)}")
