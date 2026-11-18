from django.db.models import *
from django.db import transaction
from sistema_escolar_backend.serializers import UserSerializer
from sistema_escolar_backend.serializers import *
from sistema_escolar_backend.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group

class AlumnosView(generics.CreateAPIView):
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = UserSerializer(data=request.data)

        if user.is_valid():
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']

            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                return Response({"message": "Usuario "+email+", ya está registrado"}, 400)

            user = User.objects.create(username=email, email=email,
                                       first_name=first_name, last_name=last_name,
                                       is_active=1)
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            alumno = Alumnos.objects.create(user=user,
                                            matricula=request.data["matricula"],
                                            curp=request.data["curp"].upper(),
                                            rfc=request.data["rfc"].upper(),
                                            fecha_nacimiento=request.data["fecha_nacimiento"],
                                            edad=request.data["edad"],
                                            telefono=request.data["telefono"],
                                            ocupacion=request.data["ocupacion"])
            alumno.save()

            return Response({"Alumno creado correctamente": alumno.id}, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)