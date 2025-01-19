from rest_framework import serializers
from .models import GroupChat, Message, Bill, BillSplit
from trip.serializers import UserBasicSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = UserBasicSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']

class GroupChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = GroupChat
        fields = ['id', 'trip', 'messages', 'created_at']
        read_only_fields = ['id', 'created_at']

class BillSplitSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = BillSplit
        fields = ['id', 'user', 'user_id', 'amount', 'is_paid', 'paid_at']
        read_only_fields = ['id', 'paid_at']

class BillSerializer(serializers.ModelSerializer):
    paid_by = UserBasicSerializer(read_only=True)
    splits = BillSplitSerializer(many=True, read_only=True)
    split_details = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Bill
        fields = [
            'id', 'title', 'amount', 'currency', 
            'paid_by', 'splits', 'split_details',
            'created_at'
        ]
        read_only_fields = ['id', 'paid_by', 'created_at'] 