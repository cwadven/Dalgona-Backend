from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from board_list.models import Board_list

from PIL import Image as Img
from PIL import ExifTags
from io import BytesIO
from django.core.files import File


class Profile(AbstractUser):
    nickname = models.CharField(max_length=20, unique=True, blank=False)
    introduction = models.TextField(null=True, blank=True)
    bookmark = models.ManyToManyField(Board_list, related_name='bookmarks', blank=True)
    profile_image = models.ImageField(upload_to='profile_image/', null=True, blank=True)
    points = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    unique_key = models.CharField(max_length=255, default='NONE')
    gender = models.CharField(max_length=10, null=True, blank=True)
    birthday = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return '%s' % self.username

    # 저장할때 이미지는 orientation 맞춰서 저장 또한 전부 삭제 exif 정보
    def save(self, *args, **kwargs):
        if self.profile_image and not self.last_login:
            pil_image = Img.open(BytesIO(self.profile_image.read()))
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                exif = dict(pil_image._getexif().items())

                if exif[orientation] == 3:
                    pil_image = pil_image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    pil_image = pil_image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    pil_image = pil_image.rotate(90, expand=True)

                output = BytesIO()
                pil_image.save(output, format='JPEG', quality=100)
                output.seek(0)
                self.profile_image = File(output, self.profile_image.name)
            except:
                pass

        return super(Profile, self).save(*args, **kwargs)
