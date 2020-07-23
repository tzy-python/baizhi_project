from rest_framework.generics import ListAPIView, RetrieveAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from course.models import CourseCategory, Course, CourseLesson, CourseChapter
from course.pagination import CoursePageNumber
from course.serializer import CourseCategorySerializer, CourseModelSerializer, CourseLessonModelSerializer, \
    ChapterLessonModelSerializer


class CourseCategoryListAPIView(ListAPIView):
    """课程分类信息查询"""
    queryset = CourseCategory.objects.filter(is_show=True, is_delete=False).order_by("orders")
    serializer_class = CourseCategorySerializer


class CourseListAPIView(ListAPIView):
    """课程列表查询"""
    queryset = Course.objects.filter(is_show=True, is_delete=False).order_by("orders")
    serializer_class = CourseModelSerializer


class CourseFilterListAPIView(ListAPIView):
    """根据条件查询课程"""
    queryset = Course.objects.filter(is_show=True, is_delete=False).order_by("orders")
    serializer_class = CourseModelSerializer

    # 根据不同的分类id查询不同的课程
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filter_fields = ("course_category",)

    ordering_fields = ("id", "students", "price")
    pagination_class = CoursePageNumber


class CourseLessonAPIView(RetrieveAPIView):
    queryset = Course.objects.filter(is_show=True, is_delete=False).order_by("orders")
    serializer_class = CourseLessonModelSerializer
    lookup_field = 'id'


class ChapterLessonListAPIView(ListAPIView):
    queryset = CourseChapter.objects.filter(is_show=True, is_delete=False).order_by("orders",'id')
    serializer_class = ChapterLessonModelSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ["course"]
