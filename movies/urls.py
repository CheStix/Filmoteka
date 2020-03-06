from django.urls import path

from . import views

urlpatterns = [
    path('', views.MovieView.as_view(), name='movie_list_url'),
    path('filter/', views.FilterMovie.as_view(), name='filter_url'),
    path('add-rating/', views.AddStarRating.as_view(), name='add_rating_url'),
    path('json-filter/', views.JsonFilterMovieView.as_view(), name='json_filter_url'),
    path('<slug:slug>/', views.MovieDetailView.as_view(), name='movie_detail_url'),
    path('review/<int:pk>/', views.AddReview.as_view(), name='add_review_url'),
    path('person/<str:slug>/', views.PersonView.as_view(), name='person_view_url'),
]