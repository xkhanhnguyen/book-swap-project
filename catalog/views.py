from django.shortcuts import render

from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin


import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm



from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from catalog.models import Author

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
    
@login_required
@permission_required('catalog.can_mark_swapped', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""

    """
    Get_object_or_404:
    - Returns a specified object from a model based on its primary key value, and raises an Http404 exception (not found) if the record does not exist.
    - Use the pk argument in get_object_or_404() to get the current BookInstance 
        (if this does not exist, the view will immediately exit and the page will display a "not found" error)
    """
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            """
            Redirect to a new URL:
            -  HttpResponseRedirect: This creates a redirect to a specified URL (HTTP status code 302).
            -  reverse(): This generates a URL from a URL configuration name and a set of arguments. 
                It is the Python equivalent of the url tag that we've been using in our templates.
            """
            return HttpResponseRedirect(reverse('all-books'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    # render() to create the HTML page, specifying the template and a context that contains our form
    return render(request, 'catalog/book_renew_librarian.html', context)



class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth']

class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
