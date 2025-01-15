document.addEventListener('DOMContentLoaded', function () {
    // Book carousel slider in homepage
    new Swiper('.swiper', {
      slidesPerView: 10, // Number of books visible
      spaceBetween: 20, // Space between slides
      navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
      },
      loop: true, // Infinite scrolling
      autoplay: {
        delay: 5000, // Auto-slide every 5 seconds
        disableOnInteraction: false,
      },
    });

    // In my_shelf.html -> Favorite and Borrowed Books buttons
    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    tabButtons.forEach(button => {
        button.addEventListener("click", () => {
            // Remove active class from all buttons
            tabButtons.forEach(btn => btn.classList.remove("active"));
            // Add active class to clicked button
            button.classList.add("active");

            // Show the corresponding tab content
            const tab = button.getAttribute("data-tab");
            tabContents.forEach(content => {
                content.classList.toggle("active", content.id === tab);
            });
        });
    });

    const browseButton = document.getElementById('browse-btn');
    const GenreMenu = document.getElementById('genre-filter');

    if (browseButton && GenreMenu) {
        browseButton.addEventListener('click', function () {
            const isVisible = GenreMenu.style.display === 'block';
            GenreMenu.style.display = isVisible ? 'none' : 'block';
        });

        // Optional: Close the dropdown if clicked outside
        document.addEventListener('click', function (event) {
            if (!browseButton.contains(event.target) && !GenreMenu.contains(event.target)) {
                GenreMenu.style.display = 'none';
            }
        });
    }

    //  Add book to Favorites
    document.querySelectorAll('.heart-btn').forEach(button => {
      button.addEventListener('click', function () {
        const bookId = this.getAttribute('data-book-id');

        // Add a loading indicator
        this.disabled = true;

        fetch(`/books/add_to_favorites/${bookId}/`, {
          method: 'GET',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
          },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.message === "Book added to favorites!") {
                alert(data.message); // Optional: Show confirmation
            } else {
                alert(data.message);
                this.disabled = false;
            }
          })
          .catch((error) => {
            console.error('Error:', error);
            this.textContent = "Add to Favorites";
            this.disabled = false;
          });
      });
    });

    //  Remove book to Favorites
    document.querySelectorAll('.remove-favorite-btn').forEach(button => {
        button.addEventListener('click', function () {
            const bookId = this.getAttribute('data-book-id');

            // Add a loading indicator
            this.disabled = true;

            fetch(`/books/remove_from_favorites/${bookId}/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then((response) => response.json())
            .then((data) => {
                if (data.message === "Book removed from favorites!") {
                    // Remove the book element from the DOM
                    const bookCard = this.closest('.book-card');
                    bookCard.remove();
                } else {
                    // Show an error message
                    alert(data.message);
                    this.disabled = false;
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                this.disabled = false;
            });
        });
    });


    const toggleButton = document.getElementById('dropdownToggle');
    const dropdownMenu = document.getElementById('dropdownMenu');

    if (toggleButton) {
        toggleButton.addEventListener('click', function () {
            const isVisible = dropdownMenu.style.display === 'block';
            dropdownMenu.style.display = isVisible ? 'none' : 'block';
        });
    }

    // Optional: Close the dropdown if clicked outside
    document.addEventListener('click', function (event) {
        if (!toggleButton.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.style.display = 'none';
        }
    });

    // Book-Search bar
    const searchInput = document.getElementById('search-input');
    const suggestionsContainer = document.getElementById('suggestions-container');

    // Event listener for search input
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value;
        if (query.length > 2) {
            fetch(`/books/search/?query=${encodeURIComponent(query)}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
                .then(response => response.json())
                .then(data => {
                    suggestionsContainer.innerHTML = '';
                    suggestionsContainer.style.display = 'block'; // Show suggestions container

                    // Create the unordered list
                    const ul = document.createElement('ul');
                    ul.classList.add('suggestions-list'); // Add a class for styling

                    data.results.forEach(book => {
                        const li = document.createElement('li');
                        li.classList.add('suggestion-item');
                        li.innerHTML = `
                            <a href="/books/book_detail/${book.id}" class="suggestion-link">
                                <img src="${book.image_url}" alt="${book.title}">
                                <div class="suggestion-info">
                                    <strong>${book.title}</strong><br>
                                    <small>${book.author}</small>
                                </div>
                            </a>
                        `;
                        ul.appendChild(li);
                    });
                    suggestionsContainer.appendChild(ul);
                });
        } else {
            suggestionsContainer.innerHTML = '';
            suggestionsContainer.style.display = 'none'; // Hide suggestions if query is too short
        }
    });

    // Hide suggestions container when clicking outside
    document.addEventListener('click', (event) => {
        if (
            !suggestionsContainer.contains(event.target) &&
            !searchInput.contains(event.target)
        ) {
            suggestionsContainer.style.display = 'none'; // Hide container
        }
    });

    // Show suggestions container when focusing on the search bar
    searchInput.addEventListener('focus', () => {
        if (searchInput.value.length > 2) {
            suggestionsContainer.style.display = 'block'; // Show container when focused
        }
    });



    function updateDateTime() {
        const now = new Date();

        // Extract date components
        const day = now.getDate(); // Day of the month
        const month = now.toLocaleString('en-US', { month: 'short' }).toUpperCase(); // Short month name in uppercase
        const year = now.getFullYear(); // Full year

        // Format date as 2-DEC-2024
        const formattedDate = `${day}-${month}-${year}`;

        // Format time as 09:00 AM
        const formattedTime = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true });

        // Update the date and time text
        document.getElementById('date-text').textContent = formattedDate;
        document.getElementById('time-text').textContent = formattedTime;
    }

    updateDateTime(); // Initial call
    setInterval(updateDateTime, 1000); // Update every second
});
