from django.apps import AppConfig


class StudyGroupsConfig(AppConfig):
    name = 'study_groups'

    def ready(self):
        import study_groups.signals