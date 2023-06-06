from django.shortcuts import render

from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_genre = Genre.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genre': num_genre,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    """Generic class-based view for a list of books."""
    model = Book
    paginate_by = 10 # reducing the number of items displayed on each page

    context_object_name = 'book_list'   # your own name for the list as a template variable
    # template_name = 'books/list.html'  # Specify your own template name/location
    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
    
    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get the context
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     # Create any data and add it to the context
    #     context['some_data'] = 'This is just some data'
    #     return context
    

class BookDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""
    model = Book

    def book_detail_view(request, primary_key):
        book = get_object_or_404(Book, pk=primary_key)
        return render(request, 'catalog/book_detail.html', context={'book': book})
    

class AuthorListView(generic.ListView):
    """Generic class-based list view for a list of authors."""
    model = Author
    paginate_by = 10 # reducing the number of items displayed on each page

class AuthorDetailView(generic.DetailView):
    """Generic class-based detail view for an author."""
    model = Author

class GenreListView(generic.ListView):
    """Generic class-based list view for a list of genres."""
    model = Genre
    paginate_by = 10 # reducing the number of items displayed on each page

class GenreDetailView(generic.DetailView):
    """Generic class-based detail view for an genre."""
    model = Genre




class SwappedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on swapped to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_swapped_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(swapped_with=self.request.user)
            .filter(status__exact='s')
            .order_by('date_posted')
        )

class SwappedBooksByAllListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on swapped, only visible to staff --user who can mark as swapped."""
    model = BookInstance
    permission_required = 'catalog.can_mark_swapped'
    template_name = 'catalog/bookinstance_list_swapped_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.order_by('date_posted')
        )
