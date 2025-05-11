from django.urls import path
from .views import ListNotebooksView, CreateNotebookView, EditNotebookView, DeleteNotebookView, NotebookDetailView, add_sheet_to_notebook, remove_sheet_from_notebook

urlpatterns = [
    path('', ListNotebooksView.as_view(), name='list_notebooks'),
    path('create/', CreateNotebookView.as_view(), name='create_notebook'),
    path('<int:pk>/edit/', EditNotebookView.as_view(), name='edit_notebook'),
    path('<int:pk>/delete/', DeleteNotebookView.as_view(), name='delete_notebook'),
    path('<int:pk>/', NotebookDetailView.as_view(), name='notebook_detail'),
    path('<int:pk>/add-sheet/', add_sheet_to_notebook, name='add_sheet_to_notebook'),
    path('<int:pk>/remove-sheet/<int:sheet_id>/', remove_sheet_from_notebook, name='remove_sheet_from_notebook'),
]