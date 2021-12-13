import datetime

from django.shortcuts import get_object_or_404

from rest_framework import serializers

from board_list.models import Category, Board_list


class CategorySerializer(serializers.ModelSerializer):
    board_url = serializers.CharField()

    class Meta:
        model = Category
        fields = ('id', 'board_url', 'category_name',)

    def create(self, validated_data):
        # 생성 시
        # 쿼리 가져오기
        qs = get_object_or_404(Board_list, board_url=validated_data["board_url"])
        # board_url 대입하기
        validated_data['board_url'] = qs
        category = Category.objects.create(**validated_data)
        return category

    def update(self, instance, validated_data):
        # 수정 시
        # 내용 수정하기
        instance.category_name = validated_data.get('category_name', instance.category_name)
        instance.save()
        return instance


class BoardListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True, read_only=True)
    is_new = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Board_list
        fields = (
            'board_url', 'board_name', 'introduction',
            'created_at', 'updated_at', 'category',
            'division', 'is_new', 'write_priority',
            'read_priority'
        )

    def get_is_new(self, obj):
        if obj.created_at + datetime.timedelta(days=1) >= datetime.datetime.now():
            return True
        else:
            return False


