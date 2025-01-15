# Library Management System

This Django-based library management system efficiently manages books, borrows, and user accounts, offering functionalities for librarians and users.

## Features

- **Book Management:**
   - Librarians can add, edit, and delete books.
   - Filter and search books by author, title, genre, and ISBN.
   - View statistics like total borrows for each book and stock levels.
- **Borrowing and Returning:**
   - Users can request to borrow available books.
   - Librarians can issue and return books on behalf of users.
   - System validates stock availability and prevents over-borrowing.
- **User Management:**
   - Users can register, login, and view their profile, including a list of borrowed books.
   - Custom user model with email as the unique identifier (replace with username if needed).
- **Additional Functionalities (Optional):**
   - Include API endpoints for book management and statistics using Django REST framework.
   - Implement late return tracking and penalty mechanisms.
   - Create roles and permissions for different user types (librarian, standard user).

## Requirements

- Python 3.x
- Django (tested with version 3.x)
- Django REST framework (optional, for API endpoints)
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate

Use code with caution.

    Install dependencies:
    Bash

    pip install -r requirements.txt

    Use code with caution.

Run database migrations:
Bash

python manage.py makemigrations
python manage.py migrate

Use code with caution.
Create a Django secret key:
Bash

python manage.py secretkey --generate

Use code with caution.
Add the generated key to your project's settings.py file.
(Optional) Create a superuser account:
Bash

python manage.py createsuperuser

Use code with caution.

Usage

    Start the development server:
    Bash

    python manage.py runserver

    Use code with caution.

    Access the application in your web browser at http://127.0.0.1:8000/

Additional Notes

    User authentication and permission checks are implemented using Django's built-in mechanisms and custom permissions.
    Code adheres to best practices for Django development, including code organization, documentation, and testing (implement unit tests as needed).

Customization

    You can customize the application's functionalities by modifying the provided views, templates, and serializers.
    Additional features can be implemented to suit your specific library management needs.

Contributing

We welcome contributions to this project! Please create pull requests for bug fixes or new features.
License

This project is licensed under the MIT License.
Models

users.models.CustomUser (replace with auth.User if not using a custom user model)

    Extends the default Django user model (optional)
    Can include additional fields specific to your user management needs

book_flow.models.Author

    Represents book authors
    Includes name, date of birth (optional), and date of death (optional)

book_flow.models.Genre

    Represents book genres

book_flow.models.Book

    Represents library books
    Includes:
        Author (foreign key)
        Genre (many-to-many relationship)
        Borrowers (many-to-many relationship through BorrowHistory)
        Title
        Published date
        Stock (quantity available)
        Total borrowed (cumulative count)
        Currently borrowed (current number of books borrowed)
        Image URL (optional)
        ISBN (unique identifier, optional)
        Validation to prevent over-borrowing

book_flow.models.BorrowHistory

    Tracks book borrow and return information
    Includes:
        Book (foreign key)
        Borrower (foreign key)
        Issued (boolean flag)
        Returned (boolean flag)
        Borrow date (datetime field)
        Return date (datetime field, optional)
