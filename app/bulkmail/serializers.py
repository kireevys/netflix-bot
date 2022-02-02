from bulkmail.models import Button, Message
from rest_framework import serializers


class MessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class ButtonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Button
        fields = "__all__"
