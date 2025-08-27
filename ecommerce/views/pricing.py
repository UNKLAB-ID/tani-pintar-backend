from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView

from ecommerce.models import UnitOfMeasure
from ecommerce.serializers.pricing import UnitOfMeasureDetailSerializer
from ecommerce.serializers.pricing import UnitOfMeasureListSerializer


class UnitOfMeasureListView(ListAPIView):
    """
    View for listing all units of measure.
    GET: List all UOMs
    """

    queryset = UnitOfMeasure.objects.all().order_by("name")
    serializer_class = UnitOfMeasureListSerializer
    permission_classes = [permissions.AllowAny]


class UnitOfMeasureDetailView(RetrieveAPIView):
    """
    View for retrieving a specific unit of measure.
    GET: Retrieve UOM details
    """

    queryset = UnitOfMeasure.objects.all()
    serializer_class = UnitOfMeasureDetailSerializer
    permission_classes = [permissions.AllowAny]
