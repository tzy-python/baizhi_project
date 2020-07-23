from rest_framework.serializers import ModelSerializer

from course.models import CourseCategory, Course, Teacher, CourseLesson, CourseChapter


class CourseCategorySerializer(ModelSerializer):
    """课程分类"""

    class Meta:
        model = CourseCategory
        fields = ['id', 'name']


class CourseTeacherSerializer(ModelSerializer):
    """课程所属老师的序列化器"""

    class Meta:
        model = Teacher
        fields = ("id", "name", "title", "signature", "role", "brief", "image")


class CourseModelSerializer(ModelSerializer):
    """课程列表"""
    # 序列化器嵌套查询老师信息
    teacher = CourseTeacherSerializer()

    class Meta:
        model = Course
        fields = ["id", "name", "course_img", "students", "lessons", "pub_lessons", "price", "teacher",
                  "lesson_list","discount_name","real_price"]


class CourseLessonModelSerializer(ModelSerializer):
    """课程详细信息序列化器"""
    teacher = CourseTeacherSerializer()

    class Meta:
        model = Course
        fields = ["id", "name", "level_name", "students", "lessons", "course_img",
                  "pub_lessons", "price", "teacher", "course_video","brief_html","discount_name",
                  "real_price","active_time"]


class LessonModelSerializer(ModelSerializer):
    class Meta:
        model = CourseLesson
        fields = ["id", "name", "free_trail"]


class ChapterLessonModelSerializer(ModelSerializer):
    coursesections = LessonModelSerializer(many=True)

    class Meta:
        model = CourseChapter
        fields = ["id", "name", "chapter", "coursesections"]
