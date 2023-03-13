from rest_framework import routers

from booklet_information.api import SelectProvinceForMajorViewSet, SelectDefaultProvinceViewSet, InfoViewSet, \
    MajorViewSet, ProvinceViewSet, UniversityViewSet

router = routers.SimpleRouter()
router.register(r'select_province_for_major', SelectProvinceForMajorViewSet, 'select_province_for_major')
router.register(r'select_province', SelectDefaultProvinceViewSet, 'select_province')
router.register(r'information', InfoViewSet, 'information')
router.register(r'major', MajorViewSet, 'major')
router.register(r'province', ProvinceViewSet, 'province')
router.register(r'university', UniversityViewSet, 'university')