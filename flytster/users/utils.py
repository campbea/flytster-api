from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import escape
from django.utils.safestring import mark_safe


# Emails
HTML_TEMPLATE = 'email.html'
TEXT_TEMPLATE = 'email.txt'


def new_user_email(context):
    user_full_name = context['full_name']
    verification_link = context['verification_link']

    text_content = ('Confirm this email address so we can activate your account:')
    html_content = mark_safe('<p>{0}</p>'.format(escape(text_content)))

    email_context = {
        'header': 'Hi {0},'.format(user_full_name),
        'text_content': text_content,
        'html_content': html_content,
        'link_text': 'Activate my Flytster account',
        'link': verification_link
    }

    subject = 'Welcome to Flytster'
    text = render_to_string(TEXT_TEMPLATE, email_context)
    html = render_to_string(HTML_TEMPLATE, email_context)

    return subject, text, html


def verify_email(context):
    user_full_name = context['full_name']
    verification_link = context['verification_link']

    text_content = ('Confirm your new email address:')
    html_content = mark_safe('<p>{0}</p>'.format(escape(text_content)))

    email_context = {
        'header': 'Hi {0},'.format(user_full_name),
        'text_content': text_content,
        'html_content': html_content,
        'link_text': 'Verify my email',
        'link': verification_link
    }

    subject = 'Flytster Email Verification'
    text = render_to_string(TEXT_TEMPLATE, email_context)
    html = render_to_string(HTML_TEMPLATE, email_context)

    return subject, text, html


def password_reset_email(context):
    user_full_name = context['full_name']
    verification_link = context['verification_link']

    text_content = 'You requested a new password:'
    html_content = mark_safe('<p>{0}</p>'.format(escape(text_content)))

    email_context = {
        'header': 'Hi {0},'.format(user_full_name),
        'text_content': text_content,
        'html_content': html_content,
        'link_text': 'Reset my password',
        'link': verification_link
    }

    subject = 'Flytster Password Reset'
    text = render_to_string(TEXT_TEMPLATE, email_context)
    html = render_to_string(HTML_TEMPLATE, email_context)

    return subject, text, html
