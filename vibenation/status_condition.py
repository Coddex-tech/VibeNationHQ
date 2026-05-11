from django.utils.html import format_html

def get_status_badge(value, true_label="Active", false_label="Inactive"):
    """
    A universal badge creator.
    'value' should be the boolean (True/False) from your field.
    """
    if value:
        color = "#10b981"  # Green
        label = true_label
    else:
        color = "#ef4444"  # Red
        label = false_label

    return format_html(
        '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 11px; text-transform: uppercase;">{}</span>',
        color,
        label
    )