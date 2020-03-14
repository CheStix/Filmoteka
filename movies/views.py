from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.base import View

from .models import Movie, Actor, Genre, Rating
from .forms import ReviewForm,  RatingForm


class GenreYear:
    """Все жанры и года выходов фильмов"""
    def get_genres(self):
        return Genre.objects.all()

    def get_years(self):
        return Movie.objects.filter(draft=False).values('year').distinct()


class MovieView(GenreYear, ListView):
    """Список фильмов"""
    model = Movie
    queryset = Movie.objects.filter(draft=False).order_by('-world_premiere')
    paginate_by = 6


class MovieDetailView(GenreYear, DetailView):
    """Полное описание фильма"""
    model = Movie
    queryset = Movie.objects.filter(draft=False)
    slug_field = 'url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['star_form'] = RatingForm()
        context['form'] = ReviewForm
        return context


class AddReview(View):
    """Добавление отзыва"""
    def post(self, request, pk):
        form = ReviewForm(request.POST)
        movie = Movie.objects.get(id=pk)
        if form.is_valid():
            form = form.save(commit=False)
            if request.POST.get('parent', None):
                form.parent_id = int(request.POST.get('parent'))
            form.movie = movie
            form.save()
        return redirect(movie.get_absolute_url())


class PersonView(GenreYear, DetailView):
    """ВЫвод информации об актере или режиссере"""
    model = Actor
    template_name = 'movies/person.html'
    slug_field = 'name'


class FilterMovie(GenreYear, ListView):
    """фильтр фильмов"""
    paginate_by = 6
    
    def get_queryset(self):
        if self.request.GET.getlist('year') and self.request.GET.getlist('genre'):
            queryset = Movie.objects.filter(year__in=self.request.GET.getlist('year'), genres__in=self.request.GET.getlist('genre'))
        else:
            queryset = Movie.objects.filter(
                Q(year__in=self.request.GET.getlist('year')) | Q(genres__in=self.request.GET.getlist('genre'))
                ).distinct()
        return queryset.order_by('-world_premiere')
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['year'] = ''.join([f'year={x}&' for x in self.request.GET.getlist('year')])
        context['genre'] = ''.join([f'genre={x}&' for x in self.request.GET.getlist('genre')])
        return context


class JsonFilterMovieView(ListView):
    """Фильтр фильмов в json"""
    def get_queryset(self):
        queryset = Movie.objects.filter(
            Q(year__in=self.request.GET.getlist('year')) | Q(genres__in=self.request.GET.getlist('genre'))
        ).distinct().values('title', 'tagline', 'url', 'poster')
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = list(self.get_queryset())
        return JsonResponse({'movies': queryset}, safe=False)


class AddStarRating(View):
    """добавление рейтинга к фильму"""
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                ip=self.get_client_ip(request),
                movie_id=int(request.POST.get('movie')),
                defaults={'star_id': int(request.POST.get('star'))}
            )
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)


class Search(GenreYear, ListView):
    """Поиск фильмов"""

    paginate_by = 6

    def get_queryset(self):
        return Movie.objects.filter(title__icontains=self.request.GET.get('q'))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['q'] = f'q={self.request.GET.get("q")}&'
        return context
