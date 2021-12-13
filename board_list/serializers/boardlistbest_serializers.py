from rest_framework import serializers

from board_list.models import Board_list


class BestBoardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board_list
        fields = ('board_url', 'board_name', 'division')