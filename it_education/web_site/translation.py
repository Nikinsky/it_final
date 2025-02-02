
from modeltranslation.translator import register, TranslationOptions
from .models import *


@register(Tariff)
class TariffTranslationOptions(TranslationOptions):
    fields = []

@register(TariffInfo)
class TariffInfoTranslationOptions(TranslationOptions):
    fields = ('info',)








@register(MainPage)
class MPTranslationOptions(TranslationOptions):
    fields =('title', 'description')

@register(MainPageQuestions)
class MPQuestionsTranslationOptions(TranslationOptions):
    fields =('question', 'answer')

@register(AboutSchool)
class ASchoolTranslationOptions(TranslationOptions):
    fields = ('title1', 'description1', 'title2', 'description2')

@register(AboutUs)
class AUsTranslationOptions(TranslationOptions):
    fields = ('title', 'description1', 'description2', 'title_serti', 'description_serti')








@register(Statya)
class StatyaTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'description1', 'description2', 'description3', 'for_key_description',
              'for_key_description2')

@register(Keys)
class KeysTranslationOptions(TranslationOptions):
    fields = ('key',)

@register(Keys2)
class Keys2TranslationOptions(TranslationOptions):
    fields = ('keys',)







@register(MasterClass)
class MasterClassTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'dostup', 'count_lesson', 'title_about_master','description_about_master_class',
              'position', 'description_process', 'full_name', 'position', 'title_process', 'description_process', 'title_questions',
              'private_title', 'private_description', 'private_title2', 'private_title3')

@register(Materials)
class MaterialsTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(ProgrammaMasterClass)
class ProgrammaMasterClassTranslationOptions(TranslationOptions):
    fields = ('name_master',)

@register(Process)
class ProcessTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(PrivateMasterClassVideo)
class ProcessTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(PrivateMasterClassKey1)
class ProcessTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(PrivateMasterClassKey2)
class ProcessTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(MasterQuestions)
class ProcessTranslationOptions(TranslationOptions):
    fields = ('questions', 'answer')











@register(Cours)
class CoursTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'description1', 'description2', 'description3',
              'description4', 'description5', 'dostup_course', 'full_name', 'position', 'count_module', 'count_materials',
              'private_title', 'private_description')

@register(WhoForCours)
class WhoForCoursTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(YouLearn)
class YouLearnTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Module)
class ModuleTranslationOptions(TranslationOptions):
    fields = ('description',)


@register(Process_learn)
class Process_learnTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(CourseQuestions)
class CourseQuestionsTranslationOptions(TranslationOptions):
    fields = ('questions', 'answer')

@register(PrivateCourseVideo)
class PrivateCourseVideoTranslationOptions(TranslationOptions):
    fields = ('name',)
