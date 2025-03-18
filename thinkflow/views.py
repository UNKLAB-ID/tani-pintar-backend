from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from thinkflow.serializers import CreatePlantDiseaseSerializer
from thinkflow.serializers import GetPlantDiseaseSerializer


def index(request):
    return HttpResponse("Hello, world. You're at the thinkflow index.")


class PlantDiseaseAnalyzerView(GenericAPIView):
    authentication_classes = []
    permission_classes = []

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreatePlantDiseaseSerializer
        return super().get_serializer_class()

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plant_disease = serializer.save()
        plant_disease.analyze()

        response_serializer = GetPlantDiseaseSerializer(plant_disease)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
