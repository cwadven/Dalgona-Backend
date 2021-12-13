from PIL import Image as Img
from PIL import ExifTags
from io import BytesIO

from django.core.files import File
from django.db import models


class BoardImage(models.Model):
    image = models.ImageField(upload_to='board_image/', null=False, blank=False)

    def __str__(self):
        return '%s' % (self.image)

    # 저장할때 이미지는 orientation 맞춰서 저장 또한 전부 삭제 exif 정보
    def save(self, *args, **kwargs):
        if self.image:
            pil_image = Img.open(BytesIO(self.image.read()))
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
                self.image = File(output, self.image.name)
            except FileExistsError as e:
                pass

        return super(BoardImage, self).save(*args, **kwargs)
