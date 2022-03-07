from django.db import models

from drf_store.settings import ADULT_CATEGORIES


class ControlAdultMixin:

    @staticmethod
    def user_is_adult(user):
        return hasattr(user, 'profile') and user.profile.is_adult()


class AdultFilteredItems(ControlAdultMixin, models.Manager):

    def adult_control(self, user):
        result = super(AdultFilteredItems, self).get_queryset()
        if self.user_is_adult(user):
            return result
        return result.exclude(category__name__in=ADULT_CATEGORIES)


class AdultFilteredCategory(ControlAdultMixin, models.Manager):

    def adult_control(self, user):
        result = super(AdultFilteredCategory, self).get_queryset()
        if self.user_is_adult(user):
            return result
        return result.exclude(name__in=ADULT_CATEGORIES)
