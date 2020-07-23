from django.urls import path

from course import views

urlpatterns = [
    path("category/",views.CourseCategoryListAPIView.as_view()),
    path("list/",views.CourseListAPIView.as_view()),
    path("list_filter/", views.CourseFilterListAPIView.as_view()),
    path("lesson_list/<str:id>", views.CourseLessonAPIView.as_view()),
    path("chapter/", views.ChapterLessonListAPIView.as_view()),
]