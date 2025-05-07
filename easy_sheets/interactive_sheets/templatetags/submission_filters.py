from django import template
from interactive_sheets.models import SheetSubmission

register = template.Library()

@register.filter
def get_submission_status(sheet, user):
    try:
        submission = SheetSubmission.objects.get(sheet=sheet, student=user)
        return submission.status
    except SheetSubmission.DoesNotExist:
        return 'pendiente'