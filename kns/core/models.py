"""
Models for the core app.
"""

from django.db import models


class FAQ(models.Model):
    """
    Model to store Frequently Asked Questions (FAQs) related to the
    Kingdom Nurturing Suite (KNS).
    """

    class Meta:
        verbose_name_plural = "Frequently asked questions"

    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        """
        Return a string representation of an FAQ instance.

        Returns
        -------
        str
            The question of the FAQ instance.
        """
        return self.question
