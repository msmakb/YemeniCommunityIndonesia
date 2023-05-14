from django.contrib.admin import ModelAdmin, register

from .models import Attachment, EmailBroadcast


@register(Attachment)
class AttachmentAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('file_name', 'content', 'mimetype', 
                                     'email_broadcast')
    

@register(EmailBroadcast)
class EmailBroadcastAdmin(ModelAdmin):
    list_display: tuple[str, ...] = ('subject', 'body', 'broadcast_date', 
                                     'is_broadcasted', 'email_list', 
                                     'has_attachment', 'created', 'updated')
