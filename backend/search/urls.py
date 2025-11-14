"""
URL configuration for search project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.models import User
from django.urls import include, path
from rest_framework import routers, serializers, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .business_logic import execute_search, SearchType, fetch_document


@api_view(["POST"])
def search(request):
    """
    Perform a search query.

    Spec:
    - Takes JSON: {"query": string, "type": "basic" | "regex"}, extra params optional and ignored if unknown
    """
    query = request.data["query"]
    search_type = request.data.get("type", "basic")
    result = execute_search(query, SearchType(search_type))
    print("execute_search result:", result)
    return Response(result)


@api_view(["GET"])
def get_document_text(_request, doc_id):
    content = fetch_document(doc_id)
    return Response(content)


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/search", search),
    path("api/document_text/<int:doc_id>", get_document_text),
    path('', include(router.urls)),
]
